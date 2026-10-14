"""178 actual existing empty carrier outbound-and-back, no quantity movement."""
import sys
from pathlib import Path
from uuid import uuid4
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
from app.modules.inventory.contracts_stock import StockCommand
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
g=OracleGateway();posting=StockPosting();uid="HU.CASE:61016ccdb0";tag=uuid4().hex[:10];operations=[]
for target in ["QI61016ccdb0","QCL61016ccdb0"]:
 rows=g.fetch_all("select RRL_STOCK_HU_READ.snapshot_json(:p_uid) SNAPSHOT from dual",{"p_uid":uid})
 import json
 tree=rows[0]["snapshot"];tree=tree if isinstance(tree,dict)else json.loads(tree)
 assert tree["leaf_count"]==0
 op="SPARSE178:"+tag+":"+str(len(operations));operations.append(op)
 result=posting.post(StockCommand(operation_id=op,command_type="HU_MOVE",actor="admin",source={"uid":uid},
  metadata={"expected_version":tree["nodes"][0]["version"],"target_cell":target,"scan_container":uid,"scanned_from_cell":tree["cell"],"scanned_to_cell":target},lines=()))
 assert result["cell"]==target and result["leaf_count"]==0
 count=g.fetch_all("select count(*) N from RRL_EVENTS where OPERATION_ID=:p_op",{"p_op":op})[0]["n"]
 assert count==0
print("PASS178 actual empty carrier move/back through same native owner/indexed container-cell queries; no quantity journal",operations)
