"""NI01 working ARTMAS10 mapping, deliberately limited to warehouse master data."""
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from .article_logistics import box_logistics
from .article_units import map_units


def positive(value: str) -> Decimal:
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("Invalid SAP unit conversion") from exc
    if not result.is_finite() or result <= 0:
        raise ValueError("SAP unit conversion must be positive")
    return result


def map_articles(envelope: dict) -> list[dict]:
    result = []
    for material in envelope["materials"]:
        records = [r for r in envelope["segments"] if r["fields"].get("MATERIAL") == material]
        heads = [r["fields"] for r in records if r["segment"] == "E1BPE1MATHEAD"]
        if not heads:  # VARKEY references do not create phantom articles.
            continue
        if len(material) > 40 or len(heads) != 1:
            raise ValueError("Article key exceeds WMS length or has ambiguous header")
        values = {}
        changed = None
        units = []
        descriptions = []
        for record in records:
            segment, data = record["segment"], record["fields"]
            if data.get("FUNCTION") == "003":
                raise ValueError("Deletion segments require an explicit deletion contract")
            if segment == "E1BPE1MARART":
                values.update(data)
            elif segment == "E1BPE1MARARTX":
                changed = {k for k, v in data.items() if v == "X"}
            elif segment == "E1BPE1MAKTRT" and data.get("MATL_DESC"):
                descriptions.append(data)
        units = map_units(records)
        descriptions.sort(key=lambda d: {"RU": 0, "R": 0, "EN": 1, "E": 1}.get(d.get("LANGU_ISO") or d.get("LANGU"), 2))
        base_uom = values.get("BASE_UOM") or values.get("BASE_UOM_ISO")
        source_base_uom = base_uom
        if changed is not None and not {"BASE_UOM", "BASE_UOM_ISO"}.intersection(changed):
            base_uom = None
        base_ean = next((u["ean"] for u in units if u["uom"] == source_base_uom and u["ean"]), None)
        if not base_ean and (changed is None or "EAN_UPC" in changed):
            base_ean = values.get("EAN_UPC") or None
        boxes = [u for u in units if u["uom"] in {"BOX", "CAR", "CS", "KAR"}]
        pallets = [u for u in units if u["uom"] == "PAL"]
        if len(boxes) > 1 or len(pallets) > 1:
            raise ValueError("Ambiguous box/pallet UoM: configure SAP mapping")
        result.append({"material": material, "name": descriptions[0]["MATL_DESC"] if descriptions else None,
                       "base_uom": base_uom, "ean": base_ean,
                       "box_ean": boxes[0]["ean"] if boxes else None,
                       "box_qty": Decimal(boxes[0]["ratio"]) if boxes and boxes[0]["ratio"] is not None else None,
                       "pallet_qty": Decimal(pallets[0]["ratio"]) if pallets and pallets[0]["ratio"] is not None else None,
                       "units": units, "logistics": box_logistics(records), "active": (int(values["DEL_FLAG"] != "X")
                       if "DEL_FLAG" in values and (changed is None or "DEL_FLAG" in changed) else None)})
    if not result:
        raise ValueError("No article master records in ARTMAS10")
    return result
