from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/weighted_box_capture.py");s=p.read_text(encoding="utf-8")
s=s.replace('set(item) - {"barcode", "codes"}','set(item) - {"barcode", "codes", "gross_weight_kg", "volume_m3", "measurement_reference"}')
s=s.replace('        labels[identity] = decoded','        labels[identity] = {**decoded, **box_dimensions(item, quantities[identity])}')
s+="""

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
        if not isinstance(reference, str) or not reference.strip() or len(reference) > 200 or "\\x00" in reference:
            raise ValueError("Identify the source of each physical box measurement")
    elif reference is not None:
        raise ValueError("Measurement reference requires an actual gross weight or volume")
    return {**dimensions, "measurement_reference": reference}
"""
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py");s=p.read_text(encoding="utf-8")
s=s.replace('                binding = binding_map[unit_id]','                binding = binding_map[unit_id]\n                box = marks.get("weighted_boxes", {}).get(unit_id, {})')
s=s.replace('PHYSICAL_UNIT_KEY,CURRENT_UID,CURRENT_CELL,BASE_UOM,STOCK_STATUS,UNIT_VERSION)\n                    values', 'PHYSICAL_UNIT_KEY,CURRENT_UID,CURRENT_CELL,BASE_UOM,STOCK_STATUS,UNIT_VERSION,\n                    GROSS_WEIGHT_KG,BOX_VOLUME_M3,MEASUREMENT_REFERENCE,WEIGHT_LABEL_SCAN)\n                    values')
s=s.replace(":base,'CAPTURED',0)",":base,'CAPTURED',0,:gross,:volume,:reference,:label)")
s=s.replace('c=cell,base=base_uom)','c=cell,base=base_uom,gross=box.get("gross_weight_kg"),volume=box.get("volume_m3"),\n                    reference=box.get("measurement_reference"),label=box.get("raw_scan"))')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
