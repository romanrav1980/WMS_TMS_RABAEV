exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
from app.modules.inventory.public import build_stock_posting_service
from app.modules.inventory.contracts_stock import StockCommand
from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
from app.oracle_gateway import OracleGateway
import httpx
p=Path('tmp/source405_progress.json');ctx=json.loads(p.read_text(encoding='utf-8'))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
 try:
  q.execute("update RRL_CELLS set IS_SYSTEM=1 where CELL=:cell and WARE_ID=:ware",cell=ctx['shipcell'],ware=ctx['warehouse']);c.commit()
 finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
result=build_stock_posting_service().post(StockCommand(operation_id='GROUP405.TOSHIP:'+ctx['tag'],command_type='INTERNAL_MOVE',actor='admin',source={},lines=(),metadata=dict(uid=ctx['lot'],source_cell=ctx['dst'],target_cell=ctx['shipcell'],quantity='0',unit='EA')))
qc=OutgoingQuality(OracleGateway());proof=qc.status(ctx['st_uid'],'admin')
with httpx.Client(auth=('admin','admin123'),timeout=40)as client:
 r=client.post('http://127.0.0.1:8088/api/outgoing-quality/'+ctx['st_uid']+'/scan',json=dict(operation_id='GROUP405.QC:'+ctx['tag'],expected_composition_signature=proof['composition_signature'],error_count=0,scans=[code for unit in ctx['units']for code in unit['codes']]))
 assert r.status_code==200,r.text
ctx['source_trip']=ctx.pop('trip');Path('tmp/context405.json').write_text(json.dumps(ctx,indent=2),encoding='utf-8')
print('SOURCE405 retained original3/P3H3/QC/CRPT-only; shared shipping zone')
