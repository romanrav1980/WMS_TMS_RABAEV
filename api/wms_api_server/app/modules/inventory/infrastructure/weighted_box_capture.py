"""Serialized net-weight labels are physical units, independent of government marking."""
from decimal import Decimal
import json
from typing import Any
import oracledb
from ..domain.mark_identity import canonical_mark


def decode_box(cur: Any, raw: str) -> dict:
    value = cur.callfunc("RRL_WEIGHT_BOX_READ.decode_json", oracledb.DB_TYPE_CLOB, [raw])
    return json.loads(value.read() if hasattr(value, "read") else value)


def resolve_weighted_boxes(cur: Any, article: str, quantity: Decimal, payload: dict,
                           base: str, policy: tuple) -> dict:
    if base != "KG" or not policy[2] or payload.get("capture_mode") != "WEIGHTED_BOXES":
        raise ValueError("Enable serialized KG boxes in the current WMS SKU policy")
    if payload.get("policy_version") != policy[0] or payload.get("units") or payload.get("aggregations"):
        raise ValueError("Current policy version and one weighted-box capture mode required")
    boxes = payload.get("weighted_boxes")
    if not isinstance(boxes, list) or not 1 <= len(boxes) <= 10000:
        raise ValueError("Capture requires 1..10000 serialized weighted boxes")
    cur.execute("select SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE from RRL_SKU_RECEIPT_PROFILE where ARTICUL=:p_article",
                p_article=article)
    profiles = {(r[0], r[1]): {"version": r[2], "mode": r[3]} for r in cur.fetchall()}
    if bool(profiles) != bool(policy[1]):
        raise ValueError("Current marking flag/profile configuration is inconsistent")
    units, quantities, labels = {}, {}, {}
    for item in boxes:
        if not isinstance(item, dict) or set(item) - {"barcode", "codes", "gross_weight_kg", "volume_m3", "measurement_reference"} or not isinstance(item.get("barcode"), str):
            raise ValueError("Each box requires its original barcode and applicable unique codes")
        decoded = decode_box(cur, item["barcode"])
        cur.callproc("RRL_WEIGHT_BOX_READ.assert_sku", [article, decoded["gtin"]])
        identity = decoded["identity"]
        if identity in units:
            raise ValueError("Weighted physical box scanned twice")
        codes = item.get("codes", [])
        if not isinstance(codes, list) or len(codes) != len(profiles):
            raise ValueError("Every applicable WMS marking profile must be scanned for the same box")
        registered = {}
        for code in codes:
            if not isinstance(code, dict) or set(code) != {"system_code", "profile_code", "code"}:
                raise ValueError("Exact unique marking fields required")
            profile = (code["system_code"], code["profile_code"])
            if profile not in profiles or profile in registered or profiles[profile]["mode"] not in {"UNIT", "UNIT_OR_AGGREGATION"}:
                raise ValueError("Weighted serialized trade unit requires a permitted unit scan")
            normalized = canonical_mark(*profile, code["code"], decoded["gtin"] if profile[0] == "CRPT" else None)
            if profile[0] == "CRPT" and (normalized["gtin"] != decoded["gtin"] or normalized["serial"] != decoded["serial"]):
                raise ValueError("Product-weight label and government code identify different units")
            registered[profile] = code["code"]
        units[identity] = registered
        quantities[identity] = Decimal(decoded["net_weight_kg"])
        labels[identity] = {**decoded, **box_dimensions(item, quantities[identity])}
    if sum(quantities.values(), Decimal(0)) != quantity:
        raise ValueError("Exact captured net weight must equal lot KG quantity")
    return {"policy_version": policy[0], "marking_required": int(policy[1]), "profiles": profiles,
            "units": units, "unit_quantities": quantities, "scanned": [],
            "weighted_boxes": labels, "manifest_operation_id": None}


def assert_current_weighted_policy(cur: Any, pallet: str, marks: dict) -> None:
    cur.execute("""select p.POLICY_VERSION,p.MARKING_REQUIRED,p.SERIALIZED_WEIGHT_BOXES
        from RRL_SKU_RECEIPT_POLICY p join RRL_PALLETS lot on lot.ARTICUL=p.ARTICUL
        where lot.UID_PALLET=:p_lot""", p_lot=pallet)
    if cur.fetchone() != (marks["policy_version"], marks["marking_required"], 1):
        raise ValueError("Weighted-box policy changed after preparation")
    cur.execute("select ARTICUL from RRL_PALLETS where UID_PALLET=:p_lot", p_lot=pallet)
    article = cur.fetchone()[0]
    for label in marks["weighted_boxes"].values():
        cur.callproc("RRL_WEIGHT_BOX_READ.assert_sku", [article, label["gtin"]])
    cur.execute("select SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE from RRL_SKU_RECEIPT_PROFILE where ARTICUL=:p_article",
                p_article=article)
    current = {(r[0], r[1]): {"version": r[2], "mode": r[3]} for r in cur.fetchmany(51)}
    if current != marks["profiles"]:
        raise ValueError("Weighted-box marking profiles changed after preparation")


def box_dimensions(item: dict, net: Decimal) -> dict:
    dimensions = {}
    for field in ("gross_weight_kg", "volume_m3"):
        value = item.get(field)
        if value is None:
            dimensions[field] = None
            continue
        if not isinstance(value, str):
            raise ValueError("Physical box measurements must be exact decimal strings")
        from decimal import InvalidOperation
        try:
            measurement = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError("Invalid physical box measurement") from exc
        if not measurement.is_finite() or not 0 < measurement <= Decimal("999999999999") or measurement.as_tuple().exponent < -9:
            raise ValueError("Positive bounded physical measurement with at most nine decimal places required")
        if field == "gross_weight_kg" and measurement < net:
            raise ValueError("Physical box gross KG cannot be below label net KG")
        dimensions[field] = format(measurement, "f")
    reference = item.get("measurement_reference")
    if any(dimensions.values()):
        if not isinstance(reference, str) or not reference.strip() or len(reference) > 200 or "\x00" in reference:
            raise ValueError("Identify the source of each physical box measurement")
    elif reference is not None:
        raise ValueError("Measurement reference requires an actual gross weight or volume")
    return {**dimensions, "measurement_reference": reference}
