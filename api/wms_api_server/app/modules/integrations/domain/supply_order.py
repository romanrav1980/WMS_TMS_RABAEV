"""Assumed gateway contract v1. This is not a claimed SAP standard IDoc type."""
from decimal import Decimal, InvalidOperation
import base64
from hashlib import sha256
import xml.etree.ElementTree as ET

from .artmas import MAX_IDOC_BYTES, local_name


def read_supply_order(raw: bytes) -> dict:
    if not raw or len(raw) > MAX_IDOC_BYTES:
        raise ValueError("Supply order must contain 1 byte to 4 MiB")
    xml = raw.decode("utf-8-sig")
    if "<!DOCTYPE" in xml.upper() or "<!ENTITY" in xml.upper():
        raise ValueError("DTD and entities are forbidden")
    root = ET.fromstring(xml)
    if local_name(root.tag) != "WarehouseSupplyOrder" or root.get("version") != "1":
        raise ValueError("Expected WarehouseSupplyOrder version=1")
    allowed = {"Sender", "MessageId", "OrderNumber", "Revision", "WarehouseId", "ReceiveCell", "Supplier", "Lines", "Aggregations"}
    if any(local_name(node.tag) not in allowed for node in root):
        raise ValueError("Unmapped supply order field: update gateway contract explicitly")

    def value(node: ET.Element, name: str, maximum: int) -> str:
        found = [c for c in node if local_name(c.tag) == name]
        if len(found) != 1 or len(found[0]):
            raise ValueError(f"Exactly one scalar {name} is required")
        text = (found[0].text or "").strip()
        if not text or len(text.encode("utf-8")) > maximum:
            raise ValueError(f"Missing or oversized {name}")
        return text

    sender = value(root, "Sender", 100)
    message_id = value(root, "MessageId", 100)
    order_number = value(root, "OrderNumber", 20)
    revision = value(root, "Revision", 10)
    warehouse = value(root, "WarehouseId", 18)
    if not revision.isdigit() or int(revision) < 1 or not warehouse.isdigit():
        raise ValueError("Revision must be positive and WarehouseId numeric")
    containers = [n for n in root if local_name(n.tag) == "Lines"]
    if len(containers) != 1 or not 1 <= len(containers[0]) <= 1000:
        raise ValueError("Supply order requires 1..1000 lines")
    lines, numbers, materials = [], set(), set()
    for node in containers[0]:
        if local_name(node.tag) != "Line":
            raise ValueError("Unexpected child in Lines")
        number = value(node, "LineNumber", 20)
        material = value(node, "Material", 40)
        qty_text = value(node, "Quantity", 30)
        quantity_node = next(n for n in node if local_name(n.tag) == "Quantity")
        unit = quantity_node.get("unit", "").strip()
        try:
            qty = Decimal(qty_text)
        except InvalidOperation as exc:
            raise ValueError("Invalid quantity") from exc
        if not qty.is_finite() or qty <= 0 or qty > Decimal("999999999999") or qty.as_tuple().exponent < -6:
            raise ValueError("Quantity must be positive with at most 6 decimal places")
        if not unit or len(unit) > 20 or number in numbers:
            raise ValueError("Missing unit or duplicate line number")
        if material in materials:
            raise ValueError("Working v1 contract requires one line per material")
        numbers.add(number)
        materials.add(material)
        lines.append({"line_number": number, "material": material, "quantity": str(qty), "unit": unit})
    aggregations = []
    manifests = [n for n in root if local_name(n.tag) == "Aggregations"]
    if len(manifests) > 1:
        raise ValueError("Duplicate Aggregations container")
    if manifests:
        if len(manifests[0]) > 1000:
            raise ValueError("At most 1000 source aggregations per message")

        def code(node: ET.Element) -> str:
            found = [c for c in node if local_name(c.tag) == "Code"]
            if len(found) != 1 or len(found[0]):
                raise ValueError("Exactly one scalar Code is required")
            result = found[0].text or ""
            if found[0].get("encoding") == "base64":
                try:
                    result = base64.b64decode(result, validate=True).decode("utf-8")
                except (ValueError, UnicodeDecodeError) as exc:
                    raise ValueError("Invalid base64 UTF-8 code") from exc
            elif found[0].get("encoding") not in {None, "text"}:
                raise ValueError("Unsupported Code encoding")
            if not result or len(result.encode()) > 4000:
                raise ValueError("Code must contain 1..4000 UTF-8 bytes")
            return result

        identities = set()
        for aggregation in manifests[0]:
            if local_name(aggregation.tag) != "Aggregation":
                raise ValueError("Unexpected aggregation element")
            line = value(aggregation, "LineNumber", 20)
            system = value(aggregation, "System", 40)
            profile = value(aggregation, "Profile", 80)
            level = value(aggregation, "Level", 10)
            aggregate_code = code(aggregation)
            identity = (system, profile, aggregate_code)
            if line not in numbers or level not in {"BOX", "PALLET"} or identity in identities:
                raise ValueError("Invalid line, level or duplicate source aggregation")
            identities.add(identity)
            containers = [n for n in aggregation if local_name(n.tag) == "Units"]
            if len(containers) != 1 or not 1 <= len(containers[0]) <= 10000:
                raise ValueError("Aggregation requires known 1..10000 unit members")
            members, member_ids = [], set()
            for member in containers[0]:
                if local_name(member.tag) != "Unit":
                    raise ValueError("Unexpected aggregation unit element")
                unit_id = value(member, "UnitId", 100)
                if unit_id in member_ids:
                    raise ValueError("Duplicate physical unit inside aggregation")
                member_ids.add(unit_id)
                item = {"unit_id": unit_id, "code": code(member)}
                quantities = [n for n in member if local_name(n.tag) == "Quantity"]
                if quantities:
                    amount = Decimal(value(member, 'Quantity', 30))
                    if not amount.is_finite() or amount<=0 or amount.normalize().as_tuple().exponent < -6:
                        raise ValueError('Aggregation member quantity must be positive with at most 6 decimals')
                    item['quantity'] = str(amount)
                members.append(item)
            aggregations.append({"line_number": line, "system": system, "profile": profile,
                                 "level": level, "code": aggregate_code, "units": members})
    return {"sender": sender, "message_id": message_id, "order_number": order_number,
            "revision": int(revision), "warehouse_id": int(warehouse),
            "receive_cell": value(root, "ReceiveCell", 60), "supplier": value(root, "Supplier", 200),
            "lines": lines, "aggregations": aggregations,
            "payload_hash": sha256(raw).hexdigest(), "raw_xml": raw.decode("utf-8")}
