exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.transport_composition import build_transport_loading
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import read_oracle_json
p=Path('tmp/context671.json');saved=json.loads(p.read_text(encoding='utf-8'));tag=saved['first']['tag'];root=saved['root'];loading=build_transport_loading()
if 'group_second_load'not in saved:
 tree=WarehouseHu(OracleGateway()).preview(root,'admin')
 metadata=dict(expected_version=tree['nodes'][0]['version'],scan_container=root,scan_cell=saved['group_put_cell'],loading_context=dict(transport_task_id=saved['group_plan']['target_trip_id'],scan_vehicle='QL'+tag,scan_dock=saved['group_put_cell'],measurements=dict(origin='MANUAL_CONFIRMED',content_version=tree['nodes'][0]['version'],gross_weight_kg='7',width_m='1',depth_m='1',height_m='1.5')))
 op='GROUP711.LOAD:'+tag
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();req=dict(contract_version=2,operation_id=op,command_type='HU_SHIP',actor='admin',source=dict(uid=root),lines=[],units=[],metadata=metadata);out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc('RRL_STOCK_POSTING_API.prepare_command',[json.dumps(req),'admin',out,None])
   if out.getvalue()is None:q.callproc('RRL_STOCK_POSTING_API.execute_prepared',[out])
   trial=read_oracle_json(out.getvalue());q.execute('select count(*),sum(BASE_QTY)from RRL_IW_GROUP_DISPATCH where OPERATION_ID=:op',op=op);assert q.fetchone()==(2,6)
   c.rollback();q.execute('select count(*)from RRL_IW_GROUP_DISPATCH where OPERATION_ID=:op',op=op);assert q.fetchone()[0]==0
  finally:q.callproc('RRL_STOCK_POSTING_API.reset_connection')
 saved.update(group_second_load=loading.load(op,root,metadata,'admin'),group_second_load_operation_id=op,group_second_load_metadata=metadata);p.write_text(json.dumps(saved,indent=2),encoding='utf-8')
assert loading.load(saved['group_second_load_operation_id'],root,saved['group_second_load_metadata'],'admin')==saved['group_second_load']
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute('select RRL_INTERWARE_DEPART_GATE.promises(:trip)from dual',trip=saved['group_plan']['target_trip_id'])
 promises=read_oracle_json(q.fetchone()[0]);assert any(x.get('grouped_cargo')and x['physically_loaded']for x in promises)
 for ctx in(saved['first'],saved['second']):
  q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id',lot_id=ctx['lot']);assert q.fetchone()==(0,0)
print('PASS711 group secondleg existingHU load/original2STsource/2dispatch6EA/P0/wholelate rollback/replay/groupdeparturepromise ready')
