import sys
from pathlib import Path
sys.path.insert(0,str(Path("api/wms_api_server").resolve()))
from app.modules.inventory.api.receiving_routes import PalletReceipt
from pydantic import ValidationError
base=dict(operation_id="UID687:test",line_number="1",quantity="3",supplier_batch="test",expiry_date="2030-01-01")
uid="LEGACY.RECEIPT:687-abcdef0123456789"
new=PalletReceipt(**base,pallet_identifier=uid)
assert new.model_dump()["sscc"]==uid
old=PalletReceipt(**base,sscc="200001013413186783");assert old.sscc=="200001013413186783"
assert PalletReceipt(**base,sscc="(00)200001013413186783",pallet_identifier="200001013413186783").sscc==old.sscc
for body in [dict(pallet_identifier=uid,sscc=old.sscc),dict(pallet_identifier="x"*51),dict(pallet_identifier="bad uid"),dict(sscc="200001013413186784")]:
 try:PalletReceipt(**base,**body);raise AssertionError("Invalid identifier accepted")
 except ValidationError:pass
print("687 PASS: internal UID/legacy sscc/GS1 prefix aliases; conflicting/overlong/space/bad check digit rejected; no Oracle writes")
