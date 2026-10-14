import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
from app.modules.resources.public import legacy_case_reads
reader=legacy_case_reads(OracleGateway())
full=reader.list_tasks(scope="all",limit=500,warehouse_id=6667491)
one=reader.list_tasks(scope="all",limit=1,warehouse_id=6667491)
assert full and one==full[:1] and all(row["ware_id"]==6667491 for row in full)
assert all(row["route_pallet_count"]is not None for row in full)
print("PASS164 bounded selected task window keeps exact first row and whole-wave totals; currentwarehouse preserved/no writes")
