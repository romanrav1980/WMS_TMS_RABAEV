exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.interwarehouse import Interwarehouse
from app.modules.inventory.public import build_stock_posting_service
from app.oracle_gateway import OracleGateway
from datetime import datetime,timedelta,timezone
p=Path("tmp/context314.json");nested=json.loads(Path("tmp/context315.json").read_text(encoding="utf-8"));old=nested["source"];tag=old["tag"]
if p.exists():raise SystemExit("314 plan context exists; exact retained source only")
ware=old["target_warehouse"]+50000000;inbound="QI314"+tag;outbound="QO314"+tag;cell="IR314"+tag
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  q.execute("select count(*)from RRL_WARES where ID=:ware_no",ware_no=ware)
  if not q.fetchone()[0]:q.execute("insert into RRL_WARES(ID,NAME,PREFIX)values(:ware_no,:name,'I3')",ware_no=ware,name="Own314 physical nested receiving "+tag)
  for dock in[inbound,outbound]:
   q.execute("select count(*)from RRL_TT_DOCK where DOCK=:dock_code",dock_code=dock)
   if not q.fetchone()[0]:q.execute("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED)values(:dock_code,:ware_no,0)",dock_code=dock,ware_no=ware)
  for code,blocked in[(cell,1),(outbound,0)]:
   q.execute("select count(*)from RRL_CELLS where CELL=:cell_code",cell_code=code)
   if not q.fetchone()[0]:
    q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE)values(:cell_code,:ware_no,0,0,0,0,0,0,0,0,:blocked,:blocked)",cell_code=code,ware_no=ware,blocked=blocked)
    q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell_code),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell_code=code)
  q.execute("select ID from RRL_TRANSPORT_TASK where DOCK=:dock_code and CONDITION='Спланирован'",dock_code=outbound);row=q.fetchone()
  if row:trip=row[0]
  else:
   q.execute("select VODITEL_ID,TRANSPORT,TRANSTYPE from RRL_TRANSPORT_TASK where ID=:trip_id",trip_id=old["target_trip"]);driver,plate,kind=q.fetchone()
   q.execute("select RRL_TRANSPORT_TASK_SQ.nextval from dual");trip=q.fetchone()[0]
   q.execute("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED)values(:trip_id,:plate,:kind,'Спланирован',trunc(sysdate),:driver,:dock_code,0)",trip_id=trip,plate=plate,kind=kind,driver=driver,dock_code=outbound)
  c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
service=Interwarehouse(OracleGateway(),build_stock_posting_service());now=datetime.now(timezone.utc);op="IW314.PLAN:"+tag
result=service.plan(op,nested["load_operation_id"],ware,trip,inbound,now+timedelta(hours=1),now+timedelta(hours=2),"Принять неизменённую физическую матрёшку на следующем складе","DEV314:frozen whole tree","admin")
assert result["physical_tree_expected"]and result["pallet_identifier"]==nested["root"]and result["stock_pallet_identifier"]==old["lot"],result
ctx=dict(tag=tag,article=old["article"],barcode=old["barcode"],stock_uid=old["lot"],place_uid=nested["root"],source_load=nested["load_operation_id"],warehouse=ware,trip=trip,inbound=inbound,outbound=outbound,cell=cell,plan_operation_id=op,plan_result=result,units=old["units"],aggregations=old["aggregations"])
p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
print("PLAN314 physical place != stock leaf; frozen3nodes/links/currentcontainer epochs/native existing units; no stock effect")
