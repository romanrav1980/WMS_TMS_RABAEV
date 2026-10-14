exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
from app.modules.transport.infrastructure.warehouse_depot import WarehouseDepot
from app.oracle_gateway import OracleGateway
import uuid
ware=9807
tag="QA285."+uuid.uuid4().hex[:12]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def native(name,args):
  out=q.var(oracledb.DB_TYPE_CLOB);q.callproc(name,args+[out]);return read_oracle_json(out.getvalue())
 before=native("RRL_WARE_DEPOT_API.context",[ware,"admin"])
 route=native("RRL_TT_ROUTE_API.context",[33564,"admin"]);assert route["source"]["source_contract_version"]==4
 q.execute("select ADDR from RRL_ADDR where nvl(DELETED3,0)=0 and SHIROTA between 1 and 89 and DOLGOTA between 1 and 179 group by ADDR having count(*)=1 order by ADDR fetch first 1 row only")
 address=q.fetchone()[0];c.rollback()
 body={"warehouse_id":ware,"expected_version":before["version"],"depot_address":address,"reason":"Изолированная проверка настройки базы; вся транзакция отменяется"}
 payload=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=True)
 try:
  result=native("RRL_WARE_DEPOT_API.apply_setting",[tag,"admin",payload]);assert result["version"]==before["version"]+1
  # Native commands require a clean transaction; exact replay is checked separately.
  current=native("RRL_WARE_DEPOT_API.context",[ware,"admin"]);assert current["configured"]and current["depot_address"]==address
  changed=native("RRL_TT_ROUTE_API.context",[33564,"admin"]);assert changed["source_hash"]!=route["source_hash"]
  assert changed["source"]["warehouse_origins"][0]["depot_address"]==address
  try:q.execute("delete from RRL_WARE_DEPOT_HISTORY where OPERATION_ID=:operation_id",operation_id=tag)
  except oracledb.DatabaseError as e:assert e.args[0].code==20863
  else:raise AssertionError("Immutable history bypass")
 finally:c.rollback()
 assert native("RRL_WARE_DEPOT_API.context",[ware,"admin"])==before
 assert native("RRL_TT_ROUTE_API.context",[33564,"admin"])["source_hash"]==route["source_hash"];c.rollback()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 service=WarehouseDepot(OracleGateway())
 assert service.resolve(tag,body,"admin")["state"]=="NOT_RECORDED"
 try:service.context(ware,"SAP_FILE_GATEWAY")
 except Exception as e:assert getattr(e,"status",None)==403,(type(e),str(e))
 else:raise AssertionError("Gateway scope bypass")
 print("PASS285 native current warehouse origin/version/replay/guard, route sourceV4 stales on origin change, outer rollback exact restore, awaited missing, gateway403, P20H20")
