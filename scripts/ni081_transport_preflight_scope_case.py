"""163 original personal actor; rollback-only permission/warehouse/deactivation checks."""
import sys,json
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.transport.infrastructure.plan_preflight import dispatcher,current_sources
from app.modules.transport.contracts_plan import TransportPlanError
s=get_settings();actor="Q1341a19738325"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select USER_GROUP,WARE_ID,DELETED from RUSERS where ID=:id",id=actor);group,ware,deleted=q.fetchone()
 assert ware==6667491 and (deleted or 0)==0
 q.execute("select to_clob(PAYLOAD)from RRL_PLANNER_PLANS where ID=632")
 raw=q.fetchone()[0];raw=raw.read()if hasattr(raw,"read")else raw
 numbers=json.loads(raw)["routes"][0]["stops"]
 try:
  q.execute("insert into RIGHTS(USER_GROUP,RIGHT1)values(:grp,'transport_dispatch_edit')",grp=group)
  dispatcher(q,actor)
  try:current_sources(q,numbers,actor,None);raise AssertionError("Foreign warehouse sources leaked")
  except TransportPlanError as exc:assert exc.status==403 and exc.code=="PLAN_CURRENT_WARE_ACTOR_REQUIRED"
  q.execute("update RUSERS set WARE_ID=1 where ID=:id",id=actor)
  sources=current_sources(q,numbers,actor,None);assert sources and all(row["warehouse_id"]==1 for row in sources)
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor)
  try:dispatcher(q,actor);raise AssertionError("Inactive dispatcher admitted")
  except TransportPlanError as exc:assert exc.status==403
 finally:c.rollback()
 q.execute("select WARE_ID,DELETED from RUSERS where ID=:id",id=actor);assert q.fetchone()==(ware,deleted)
 print("PASS163 original personal actor current warehouse enforced before source response/own admitted/inactive denied; all permission+actor changes rolled back/no stock")
