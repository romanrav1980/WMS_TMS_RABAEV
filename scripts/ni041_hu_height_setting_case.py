"""Private dev warehouse settings only; old caller preserves new unit, explicit null clears it."""
import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.configuration import ReceiptConfiguration
from app.modules.inventory.api.receiving_routes import WarehouseReceiptSettings
g=OracleGateway();rows=g.fetch_all("select max(ID) WARE_ID from RRL_WARES where NAME like 'HU private %'")
ware=rows[0]["ware_id"];assert ware is not None
service=ReceiptConfiguration(g);old=service.get(ware)
body=WarehouseReceiptSettings(company_prefix="1234567").model_dump()
try:
 body["hu_cell_height_unit"]="CM"
 assert service.save(ware,body,"admin")["hu_cell_height_unit"]=="CM"
 body.pop("hu_cell_height_unit")
 assert service.save(ware,body,"admin")["hu_cell_height_unit"]=="CM"
 body["hu_cell_height_unit"]=None
 assert service.save(ware,body,"admin")["hu_cell_height_unit"] is None
 print("PASS existing warehouse config: explicit SI legacy height unit, old caller preserves it, explicit clear",flush=True)
finally:
 body["hu_cell_height_unit"]=old.get("hu_cell_height_unit")
 for key in ("company_prefix","extension_digit","coordinate_unit_m","reachtruck_mps","lift_mps","placement_metric"):
  if old.get(key) is not None:body[key]=old[key]
 service.save(ware,body,"admin")
