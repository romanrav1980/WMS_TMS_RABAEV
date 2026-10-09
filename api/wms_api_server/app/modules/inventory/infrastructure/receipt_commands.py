"""Registered receipt adapter: pure planning, then metadata capture under the Oracle plan."""
from datetime import date
from decimal import Decimal
from hashlib import sha256
import json
from .placement import ReceiptPlacement
from .receiving_marks import ReceivingMarks
from ..domain.mark_identity import canonical_mark
from ..contracts_stock import StockCommand, StockPostingError
from .stock_posting_uow import StockPosting


def _text(value):
    return value.read() if hasattr(value, "read") else value


def plan_receipt(cursor, document: dict) -> tuple[dict, dict]:
    source, payload = document["source"], document["metadata"]
    order_id = source["order_id"]
    sscc = payload["sscc"]
    if not isinstance(sscc, str) or len(sscc) != 18 or not sscc.isascii() or not sscc.isdigit():
        raise ValueError("Receipt SSCC must contain 18 digits")
    digit = (10 - sum(int(n) * (3 if i % 2 == 0 else 1) for i, n in enumerate(reversed(sscc[:17]))) % 10) % 10
    if digit != int(sscc[-1]):
        raise ValueError("Invalid SSCC check digit")
    cursor.execute("select NAKLAD_ID,WARE_ID,RECEIVE_CELL,ORDER_NUMBER,SENDER,REVISION from RRL_SAP_SUPPLY_ORDER where ORDER_ID=:i", i=order_id)
    order = cursor.fetchone()
    if not order:
        raise LookupError("SAP supply order not found")
    cursor.execute("select ARTICUL,BASE_UOM from RRL_SAP_SUPPLY_LINE where ORDER_ID=:i and LINE_NUMBER=:l",
                   i=order_id, l=payload["line_number"])
    line = cursor.fetchone()
    if not line:
        raise LookupError("SAP supply line not found")
    article, input_uom = line
    cursor.execute("""select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE,POLICY_VERSION from RRL_STOCK_UOM_CONVERSION
        where ARTICUL=:a and INPUT_UOM=:u and POLICY_VERSION=(select max(POLICY_VERSION) from RRL_STOCK_UOM_CONVERSION where ARTICUL=:a and INPUT_UOM=:u)""",
                   a=article, u=input_uom)
    conversion = cursor.fetchone()
    if not conversion:
        raise ValueError("Stock UOM policy required before receiving")
    base, numerator, denominator, scale, version = conversion
    cursor.execute("select RRL_STOCK_MATH.convert_exact(:q,:n,:d,:s) from dual",
                   q=payload["quantity"], n=numerator, d=denominator, s=scale)
    qbase = Decimal(str(cursor.fetchone()[0]))
    marks = ReceivingMarks(cursor).resolve(order_id, article, payload["line_number"], qbase, payload, base, lock_policy=False)
    placement = ReceiptPlacement(cursor).choose(order[1], order[2], article, payload)
    cursor.execute("select nvl(f.GTIN,a.BARCODE_SHT) from RRL_ARTICULS a left join RRL_FINISHED_GOODS_SKU f on f.ARTICUL=a.ACTICUL where a.ACTICUL=:a", a=article)
    gtin = str(cursor.fetchone()[0]).zfill(14)
    bindings, aliases = [], {}
    for unit_id, codes in marks["units"].items():
        identities = []
        for profile, code in codes.items():
            normalized = canonical_mark(profile[0], profile[1], code, gtin if profile[0] == "CRPT" else None)
            digest = sha256(normalized["identity"].encode()).hexdigest()
            alias_key = (profile[0], digest)
            if alias_key in aliases and aliases[alias_key]["unit_id"] != unit_id:
                raise ValueError("One unique code identifies multiple physical units")
            aliases[alias_key] = {"system": profile[0], "hash": digest, "unit_id": unit_id}
            identities.append(profile[0] + ":" + normalized["identity"])
        unit_key = sha256(min(identities).encode()).hexdigest()
        bindings.append({"unit_id": unit_id, "key": unit_key, "quantity": format(marks["unit_quantities"][unit_id], "f")})
    if len({b["key"] for b in bindings}) != len(bindings):
        raise ValueError("Duplicate physical unit")
    result = {"status": "RECEIVED", "operation_id": document["operation_id"],
              "pallet_identifier": payload["sscc"], "sscc": payload["sscc"], "quantity": payload["quantity"],
              "base_quantity": format(qbase, "f"), "base_uom": base,
              "sap_order_number": order[3], "sap_sender": order[4], "order_revision": order[5],
              "line_number": payload["line_number"], "material": article, "unit": input_uom,
              "supplier_batch": payload["supplier_batch"], "expiry_date": payload["expiry_date"],
              "produced_date": payload.get("produced_date"), "warehouse_id": order[1],
              "physical_measurements": {k: payload.get(k) for k in ("gross_weight", "pallet_height", "pallet_height_m", "volume_m3")},
              "receive_cell": order[2], "putaway_cell": placement["cell"], "placement": placement,
              "marking_units": len(bindings), "marking_policy_version": marks["policy_version"],
              "regulatory_validation": "NOT_PERFORMED" if bindings else "NOT_APPLICABLE", "idempotent": False}
    hints = {"article": article, "input_uom": input_uom, "base_uom": base, "base_quantity": format(qbase, "f"),
             "uom_version": int(version), "order_revision": order[5], "naklad_id": order[0],
             "marking_policy_version": marks["policy_version"], "placement": placement,
             "unit_bindings": bindings, "aliases": list(aliases.values()), "result": result,
             "aggregations": [{"system": a["system"], "hash": sha256(a["code"].encode()).hexdigest()} for a in marks["scanned"]]}
    return hints, marks


def stage_receipt(cursor, document: dict, marks: dict) -> None:
    from .receiving import Receiving
    cursor.execute("select RESOLVED_PLAN_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:i", i=document["operation_id"])
    domain = json.loads(_text(cursor.fetchone()[0]))["domain"]
    result = domain["result"]
    payload = document["metadata"]
    expiry = date.fromisoformat(payload["expiry_date"])
    produced = date.fromisoformat(payload["produced_date"]) if payload.get("produced_date") else None
    if expiry < date.today() or (produced and (produced > date.today() or produced > expiry)):
        raise ValueError("Invalid production or expiry date")
    # Check capacity while the complete cell/slot/configuration plan is already held.
    ReceiptPlacement(cursor).validate_target(domain["warehouse_id"], domain["placement"]["cell"],
                                            domain["placement"]["slot_id"], result)
    cursor.execute("""select count(*) from RRL_REMAINS r where r.CELL=:c and r.REMAIN>0 and not exists(
        select 1 from RRL_RECEIPT_SLOT_CLAIM cl where cl.CELL=:c and cl.UID_PALLET=r.UID_POLETA
         and cl.STATUS='OCCUPIED' and cl.CELL_SLOT_ID<>:slot)""", c=domain["placement"]["cell"], slot=domain["placement"]["slot_id"])
    if cursor.fetchone()[0]:
        raise ValueError("Putaway destination is occupied")
    cursor.execute("""select count(*) from RRL_WAREHOUSE_TASK where TO_CELL=:c and STATUS not in('DONE','CANCELLED')
         and (:slot is null or TO_CELL_SLOT_ID is null or TO_CELL_SLOT_ID=:slot)""",
                   c=domain["placement"]["cell"], slot=domain["placement"]["slot_id"])
    if cursor.fetchone()[0]:
        raise ValueError("Putaway destination has already been assigned")
    order = (domain["naklad_id"], domain["warehouse_id"], domain["receive_cell"],
             result["sap_order_number"], result["sap_sender"], domain["order_revision"])
    line = (domain["article"], None, domain["input_uom"])
    Receiving(None)._book_pallet(cursor, order, line, payload, marks, domain["placement"], document["actor"],
                                 task_id=domain["task_id"], stock_quantity=Decimal(domain["base_quantity"]),
                                 emit_event=False, bindings=domain["unit_bindings"], stock_base=domain["base_uom"],
                                 receive_cell=domain["receive_cell"])


def receive_command(gateway, order_id: str, payload: dict, actor: str):
    rows = gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if rows and rows[0]["state"] == "PREPARED":
        return None
    metadata = {k: v for k, v in payload.items() if k != "operation_id"}
    metadata["quantity"] = format(Decimal(str(payload["quantity"])), "f")
    # Decimal fields must reach JSON as exact strings.
    for name in ("gross_weight", "pallet_height", "pallet_height_m", "volume_m3"):
        if isinstance(metadata.get(name), Decimal):
            metadata[name] = format(metadata[name], "f")
    return StockPosting().post(StockCommand(operation_id=payload["operation_id"], command_type="SAP_RECEIPT",
        actor=actor, lines=(), source={"type": "SAP_SUPPLY_ORDER", "order_id": order_id}, metadata=metadata))
