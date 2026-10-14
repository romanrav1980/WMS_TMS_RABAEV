import json,sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.transport.api.loading_routes import LoadingRequest
from app.modules.inventory.contracts_stock import StockCommand
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select dbms_lob.substr(CANONICAL_REQUEST,4000,1) from RRL_STOCK_OPERATION where OPERATION_ID='FULL.HU.SHIP:22c5dc5ec4'");raw=q.fetchone()[0];old=json.loads(raw)
 m=old["metadata"];context=m["loading_context"]
 body=LoadingRequest.model_validate({"operation_id":old["operation_id"],"identifier":old["source"]["uid"],**{k:v for k,v in m.items() if k!="loading_context"},**context})
 new_m=body.model_dump(mode="json",exclude={"operation_id","identifier","transport_task_id","scan_vehicle","scan_dock","measurements","physical_boxes"})
 new_m["loading_context"]={"transport_task_id":body.transport_task_id,"scan_vehicle":body.scan_vehicle,"scan_dock":body.scan_dock,"measurements":body.measurements.model_dump(mode="json")}
 new_m["loading_context"]["physical_boxes"]=[x.model_dump() for x in body.physical_boxes]
 new=StockCommand(operation_id=old["operation_id"],command_type="HU_SHIP",actor="admin",source=old["source"],lines=(),metadata=new_m).canonical_json()
 print("Semantic equality:",old==json.loads(new),"Exact text equality:",raw==new,"old text prefix:",repr(raw[:80]))
 def compare(a,b,path=""):
  if isinstance(a,dict) and isinstance(b,dict):
   for k in set(a)|set(b):
    if k not in a or k not in b:print("Missing key",path+"/"+k)
    else:compare(a[k],b[k],path+"/"+k)
  elif a!=b:print("Changed",path,repr(a),repr(b))
 compare(old,json.loads(new))
