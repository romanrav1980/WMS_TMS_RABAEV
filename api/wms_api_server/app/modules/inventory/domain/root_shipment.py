"""C-0193 pure rules: one root HU tree with closed CASE children -> one ST, one recipient, exact composition, no split."""
from decimal import Decimal
from hashlib import sha256
import json
from typing import Any, Sequence
from .stock_quantity import quantity_text

class RootShipmentError(Exception):
    """A confirmed refusal with its stable code; nothing is written when it is raised."""
    def __init__(self, code: str, status: int = 409, message: str | None = None) -> None:
        super().__init__(message or code)
        self.code, self.status = code, status


CLOSED = {"WAIT_CONTROL", "CONTROL_IN_PROGRESS", "CONTROLLED", "READY_TO_SHIP"}


def request_hash(body: dict[str, Any], actor: str) -> str:
    payload = {k: body[k] for k in ("operation_id", "shipment_identifier", "scanned_root", "expected_root_version")} | {"actor": actor}
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def root_children(snapshot: dict[str, Any], scanned_root: str, expected_version: int) -> list[dict[str, Any]]:
    """The scanned top-level PALLET/BOX at its current version and every CASE child in its tree (the tree is read, never changed)."""
    nodes = snapshot.get("nodes") or []
    if not nodes or snapshot.get("root") != scanned_root:
        raise RootShipmentError("ROOT_NOT_FOUND", 404)
    root = nodes[0]
    if root.get("kind") != "CONTAINER" or root.get("type") not in ("PALLET", "BOX"):
        raise RootShipmentError("ROOT_PALLET_OR_BOX_REQUIRED")
    if snapshot.get("ancestors"):
        raise RootShipmentError("ROOT_MUST_BE_TOP_LEVEL")
    if root.get("version") != expected_version:
        raise RootShipmentError("ROOT_VERSION_CHANGED")
    cases = [n for n in nodes if n.get("kind") == "CASE"]
    if not cases:
        raise RootShipmentError("ROOT_HAS_NO_CASE_CHILDREN")
    if any(n.get("kind") not in ("CONTAINER", "CASE", "STOCK") for n in nodes):
        raise RootShipmentError("ROOT_TREE_UNSUPPORTED_NODE")
    if len({n["case_task_id"] for n in cases}) != len(cases):
        raise RootShipmentError("ROOT_CASE_DUPLICATED")
    return [{"task": int(n["case_task_id"]), "version": n.get("version"), "sscc": n.get("sscc")} for n in cases]


def check_tasks(tasks: dict[int, tuple], children: list[dict[str, Any]], warehouse: int, shipment_id: int) -> None:
    """tasks: CASE_PICK_TASK_ID -> (customer_order_id, ware_id, sscc, status, content_version, legacy_sborka_pallet_id)."""
    orders = set()
    for child in children:
        row = tasks.get(child["task"])
        if row is None:
            raise RootShipmentError("ROOT_CASE_MISSING_OR_FOREIGN")
        order, ware, sscc, status, version, legacy = row
        if ware != warehouse:
            raise RootShipmentError("ROOT_CASE_FOREIGN_WAREHOUSE")
        if child.get("sscc") is not None and sscc != child["sscc"]:
            raise RootShipmentError("ROOT_CASE_CARRIER_CHANGED")
        if status not in CLOSED:
            raise RootShipmentError("ROOT_CASE_NOT_CLOSED")
        if version != child["version"]:
            raise RootShipmentError("ROOT_CASE_VERSION_CHANGED")
        if legacy is not None:
            raise RootShipmentError("ROOT_CASE_ALREADY_BOUND_TO_ANOTHER_ST" if legacy != shipment_id else "ROOT_CASE_ALREADY_BOUND")
        if order in orders:
            raise RootShipmentError("ROOT_CASE_ORDER_NOT_UNIQUE")  # one fulfillment receives one CASE composition
        orders.add(order)


def check_fulfillments(rows: Sequence[tuple], orders: set[int]) -> dict[int, int]:
    """rows: (fulfillment_id, customer_order_id, status, address) of this ST. Exactly one PLANNED per child order, nothing else, one address."""
    by_order: dict[int, list[tuple]] = {}
    for row in rows:
        by_order.setdefault(row[1], []).append(row)
    if set(by_order) != orders:
        raise RootShipmentError("ST_FULFILLMENT_ORDERS_DIFFER_FROM_ROOT")
    if any(len(v) != 1 or v[0][2] != "PLANNED" for v in by_order.values()):
        raise RootShipmentError("ST_FULFILLMENT_NOT_SINGLE_PLANNED")
    if len({(v[0][3] or "").strip() for v in by_order.values()}) != 1:
        raise RootShipmentError("ST_RECIPIENT_NOT_SINGLE")
    return {order: int(v[0][0]) for order, v in by_order.items()}


def leaf_totals(snapshot: dict[str, Any]) -> dict[tuple[str, str], Decimal]:
    out: dict[tuple[str, str], Decimal] = {}
    for n in snapshot.get("nodes") or []:
        if n.get("kind") == "STOCK":
            key = (n.get("article"), n.get("base_uom"))
            out[key] = out.get(key, Decimal(0)) + Decimal(quantity_text(n.get("quantity")))
    return out


def physical_totals(rows: Sequence[tuple]) -> dict[tuple[str, str], Decimal]:
    out: dict[tuple[str, str], Decimal] = {}
    for article, base, quantity in rows:
        out[(article, base)] = out.get((article, base), Decimal(0)) + Decimal(quantity_text(quantity))
    return out


def assert_tree_matches_carriers(snapshot: dict[str, Any], physical_rows: Sequence[tuple]) -> None:
    """The root composition must equal the sum of its CASE carriers (no stock outside the CASE children, nothing missing)."""
    if leaf_totals(snapshot) != physical_totals(physical_rows):
        raise RootShipmentError("ROOT_COMPOSITION_CHANGED")
