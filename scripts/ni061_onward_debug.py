import sys,json,traceback
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.interwarehouse_onward import InterwarehouseOnward
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select ID from RUSERS where NAME='Own onward dispatcher'and ID like 'QIN%'");actor=q.fetchone()[0]
 records=Path("api/wms_api_server/runtime/api_audit/2026-10-10.jsonl").read_text(encoding="utf-8").splitlines()
 body=next(json.loads(json.loads(line)["request_body"])for line in reversed(records)if json.loads(line).get("phase")=="STARTED"and json.loads(line).get("path")=="/api/inventory/interwarehouse/prepare-onward")
 actor="QIN"+body["operation_id"].split(":")[-1]
 q.execute("update RUSERS set DELETED=0 where ID=:id",id=actor);c.commit()
 try:
  result=InterwarehouseOnward(OracleGateway()).prepare(body["operation_id"],body["receipt_operation_id"],body["reason"],body["decision_reference"],actor,body.get("accept_legacy_address",False))
  print(result)
 except Exception:traceback.print_exc()
 finally:q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
