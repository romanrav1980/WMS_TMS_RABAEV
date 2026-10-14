exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.interwarehouse import Interwarehouse
from app.modules.inventory.public import build_stock_posting_service
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.domain.interwarehouse_scans import normalize_interwarehouse_scans
p=Path('tmp/context406.json');saved=json.loads(p.read_text(encoding='utf-8'));first=saved['first'];second=saved['second'];tag=first['tag'];plan=saved['group_plan']
svc=Interwarehouse(OracleGateway(),build_stock_posting_service())
if 'group_receive_cell'not in saved:
 cell='IR412'+tag
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
  try:
   q.execute('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE,BLOCKED_FOR_ACCEPT)values(:cell,:ware,0,0,0,0,1,1,1,0)',cell=cell,ware=plan['target_warehouse_id'])
   q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell);c.commit()
  finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
 saved['group_receive_cell']=cell;p.write_text(json.dumps(saved,indent=2),encoding='utf-8')
if 'group_unload'not in saved:
 meta=dict(scan_pallet=saved['root'],scan_vehicle='QL'+tag,scan_dock=plan['inbound_dock'])
 saved.update(group_unload=svc.receive_action('INTERWARE_UNLOAD','GROUP412.UNLOAD:'+tag,saved['group_plan_operation_id'],meta,'admin'),group_unload_metadata=meta)
 p.write_text(json.dumps(saved,indent=2),encoding='utf-8')
meta=dict(scan_pallet=saved['root'],scan_cell=saved['group_receive_cell'],items=[dict(uid=x['lot'],article=x['article'],scan_article=x['barcode'],quantity='3',base_uom='EA')for x in(first,second)],scans=[code for ctx in(first,second)for unit in ctx['units']for code in unit['codes']])
op='GROUP412.RECEIVE:'+tag
if 'group_receipt'not in saved:
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();request=dict(contract_version=2,operation_id=op,command_type='INTERWARE_RECEIVE',actor='admin',source=dict(plan_operation_id=saved['group_plan_operation_id']),lines=[],units=[],metadata=normalize_interwarehouse_scans(meta));out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc('RRL_STOCK_POSTING_API.prepare_command',[json.dumps(request),'admin',out,None])
   if out.getvalue()is None:q.callproc('RRL_STOCK_POSTING_API.execute_prepared',[out])
   trial=read_oracle_json(out.getvalue());assert trial['physical_unit_count']==6
   q.execute('select count(*)from RRL_IW_GROUP_RECEIPT_LINE where OPERATION_ID=:op',op=op);assert q.fetchone()[0]==2
   c.rollback();q.execute('select count(*)from RRL_IW_GROUP_RECEIPT where OPERATION_ID=:op',op=op);assert q.fetchone()[0]==0
  finally:q.callproc('RRL_STOCK_POSTING_API.reset_connection')
 saved.update(group_receipt=svc.receive_action('INTERWARE_RECEIVE',op,saved['group_plan_operation_id'],meta,'admin'),group_receipt_operation_id=op,group_receipt_metadata=meta)
 p.write_text(json.dumps(saved,indent=2),encoding='utf-8')
assert svc.receive_action('INTERWARE_RECEIVE',op,saved['group_plan_operation_id'],meta,'admin')==saved['group_receipt']
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for ctx in(first,second):
  q.execute('select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell',lot_id=ctx['lot'],cell=saved['group_receive_cell']);assert q.fetchone()==(3,0)
  q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and CURRENT_CELL=:cell and STOCK_STATUS='AVAILABLE'",lot_id=ctx['lot'],cell=saved['group_receive_cell']);assert q.fetchone()==(3,3)
 q.execute('select count(*)from RRL_WMS_HU_LINK where PARENT_UID=:root_uid and ACTIVE_FLAG=1',root_uid=saved['root']);assert q.fetchone()[0]==2
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
print('PASS412 groupedfirstleg/nativewholetransaction/twoSKU3each/6originalunits9codes/oneTOP restored2links/quarantine/rollback/replay/noFFrepeat')
