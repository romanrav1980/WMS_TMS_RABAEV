exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from datetime import datetime,timedelta,timezone
from app.modules.inventory.infrastructure.interwarehouse_group_plan import InterwarehouseGroupPlan
from app.modules.inventory.infrastructure.interwarehouse_group_source import InterwarehouseGroupSource
from app.oracle_gateway import OracleGateway
p=Path('tmp/context406.json');saved=json.loads(p.read_text(encoding='utf-8'));first=saved['first'];tag=first['tag']
service=InterwarehouseGroupPlan(OracleGateway());proof=service.source(saved['load_operation_id'],'admin')
assert len(proof['source']['lots'])==2 and proof['source']['stock_leaf_count']==2,proof
view=InterwarehouseGroupSource(OracleGateway()).read(saved['load_operation_id'],'admin');assert view['source_eligible'] and sum(x['issued_manifest']['physical_unit_count']for x in view['lots'])==6
if 'group_metadata'not in saved:
 target=first['warehouse']+50000000;inbound='QI407'+tag;outbound='QO407'+tag
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
  try:
   q.execute("insert into RRL_WARES(ID,NAME,PREFIX)values(:ware,:name,'QG')",ware=target,name='Own407 group target '+tag)
   for dock in(inbound,outbound):q.execute('insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED)values(:dock,:ware,0)',dock=dock,ware=target)
   q.execute('select RRL_TRANSPORT_TASK_SQ.nextval from dual');trip=int(q.fetchone()[0])
   q.execute("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED)values(:trip,:plate,:typ,'Спланирован',trunc(sysdate),:driver,:dock,0)",trip=trip,plate='QL'+tag,typ=first['trtype'],driver=first['driver'],dock=outbound)
   c.commit()
  finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
 now=datetime.now(timezone.utc)
 saved['group_metadata']=dict(source_load_operation_id=saved['load_operation_id'],target_warehouse_id=target,target_trip_id=trip,inbound_dock=inbound,arrival_due=(now+timedelta(hours=1)).isoformat(),ready_due=(now+timedelta(hours=2)).isoformat(),reason='Own exact whole two-SKU first-leg grouped routing',decision_reference='DEV407:'+tag,expected_source_signature=proof['source_signature'])
 p.write_text(json.dumps(saved,indent=2),encoding='utf-8')
body=dict(saved['group_metadata']);body['arrival_due']=datetime.fromisoformat(body['arrival_due']);body['ready_due']=datetime.fromisoformat(body['ready_due'])
op='GROUP407.PLAN:'+tag
result=service.plan(op,body,'admin');assert service.plan(op,body,'admin')==result
saved.update(group_plan=result,group_plan_operation_id=op,group_source_proof=proof,group_source_view=view);p.write_text(json.dumps(saved,indent=2),encoding='utf-8')
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute('select count(*)from RRL_EVENTS where OPERATION_ID=:op',op=op);assert q.fetchone()[0]==0
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
print('PASS407 twoSKU/6oldunits9codes/currentarchive/groupplan/replay/noqty/sourceP0')
