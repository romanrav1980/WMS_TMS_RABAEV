from pathlib import Path
import json
s=Path("scripts/ni052_single_fullpal_case.py").read_text(encoding="utf-8-sig")
needle='  post("WAVE_PICK_RELEASE"'
at=s.index(needle)
s=s[:at]+'''  post("TARE_COUNT",{"owner_ware_id":ware,"pallet_type_id":1,"condition":"GOOD","observed_quantity":"1","expected_version":0,"reason":"Own standalone tare","decision_reference":"TARE:"+tag},{})
  bookop="TARE.FULL.BOOK:"+tag
  booked=post("TARE_BOOK",{"pallet_type_id":1,"expected_warehouse_id":ware},{"place_kind":"HU","place_id":lot},bookop)
  assert booked["available_quantity"]=="0"
  assert post("TARE_BOOK",{"pallet_type_id":1,"expected_warehouse_id":ware},{"place_kind":"HU","place_id":lot},bookop)==booked
  try:post("TARE_BOOK_CANCEL",{},{"booking_operation_id":bookop})
  except oracledb.DatabaseError as exc:assert "EMPTY_PLACE_REQUIRED" in str(exc),str(exc)
  else:raise AssertionError("Goods pallet was cancelled as empty")
'''+s[at:]
# Reuse successful dedicated current driver block, replacing just physical fixture naming.
h=Path("scripts/ni063_booked_cargo_case.py").read_text(encoding="utf-8-sig")
block=h[h.index('  import httpx'):h.index('  from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu')]
block=block.replace("TARE.CARGO.","TARE.FULL.").replace("PASS102 one outer PALLET booked/actual existing nested BOX+STOCK load","PASS103 standalone original STOCK/FULLPAL actual existing single load")
begin=s.index('  state=loading.status(trip);');end=s.index(' finally:',begin)
s=s[:begin]+block+s[end:]
print(json.dumps({"scripts/ni063_fullpal_tare_case.py":s},ensure_ascii=True))
