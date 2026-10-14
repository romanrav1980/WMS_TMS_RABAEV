exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
from app.modules.transport.public import assign_sts
from app.modules.transport.infrastructure.st_assignment import unassign_st
from app.oracle_gateway import OracleGateway
from app.transport_composition import build_transport_loading
import httpx
first=json.loads(Path('tmp/context404.json').read_text(encoding='utf-8'));second=json.loads(Path('tmp/context405.json').read_text(encoding='utf-8'))
p=Path('tmp/context406.json');saved=json.loads(p.read_text(encoding='utf-8'))if p.exists()else dict(first=first,second=second)
def save():p.write_text(json.dumps(saved,indent=2),encoding='utf-8')
gw=OracleGateway();hu=WarehouseHu(gw);tag=first['tag'];root='GROUP406:'+tag
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
 try:
  q.execute('update RRL_TR_VEHICLE set PALLETS=2 where ID=:vehicle_id',vehicle_id=first['vehicle']);c.commit()
 finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
if 'assigned'not in saved:
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.execute('select ST_NUMBER,TRANSTASK_ID from RRL_SBORKA_PALLETS where ID=:st_id',st_id=second['st']);number,old_trip=q.fetchone()
 if old_trip and old_trip!=first['source_trip']:unassign_st(gw,old_trip,number)
 assign_sts(gw,first['source_trip'],[number],'admin');saved['assigned']=True;save()
if 'created'not in saved:saved['created']=hu.command('HU_CREATE',root,'GROUP406.CREATE:'+tag,dict(cell=first['shipcell'],warehouse=first['warehouse'],container_type='PALLET',tare_weight_kg='1',scan_container=root,scan_cell=first['shipcell']),'admin');save()
for index,ctx in enumerate((first,second)):
 key='attached'+str(index)
 if key not in saved:
  parent=hu.preview(root,'admin');child=hu.preview(ctx['lot'],'admin')
  saved[key]=hu.command('HU_ATTACH',root,'GROUP406.ATTACH:'+str(index)+':'+tag,dict(child_uid=ctx['lot'],expected_version=parent['nodes'][0]['version'],expected_child_version=child['nodes'][0]['version'],scan_container=root,scan_child=ctx['lot'],reason='Own multi-SKU first-leg exact whole composition'),'admin');save()
 with httpx.Client(auth=('admin','admin123'),timeout=40)as client:
  key='qc'+str(index)
  if key not in saved:
   qc=OutgoingQuality(gw).status(ctx['st_uid'],'admin')
   r=client.post('http://127.0.0.1:8088/api/outgoing-quality/'+ctx['st_uid']+'/scan',json=dict(operation_id='GROUP406.QC:'+str(index)+':'+tag,expected_composition_signature=qc['composition_signature'],error_count=0,scans=[code for unit in ctx['units']for code in unit['codes']]))
   assert r.status_code==200,r.text;saved[key]=r.json();save()
tree=hu.preview(root,'admin')
if 'load'not in saved:
 metadata=dict(expected_version=tree['nodes'][0]['version'],scan_container=root,scan_cell=first['shipcell'],loading_context=dict(transport_task_id=first['source_trip'],scan_vehicle='QL'+tag,scan_dock=first['dock'],measurements=dict(origin='MANUAL_CONFIRMED',content_version=tree['nodes'][0]['version'],gross_weight_kg='7',width_m='1',depth_m='1',height_m='1.5')))
 op='GROUP406.LOAD:'+tag;saved.update(load=build_transport_loading().load(op,root,metadata,'admin'),load_operation_id=op,load_metadata=metadata,root=root);save()
if 'depart'not in saved:saved['depart']=build_transport_loading().depart('GROUP406.DEPART:'+tag,first['source_trip'],'admin');save()
print('GROUP406 actual firstlegHU_SHIP/two originalST/differentSKU/profile matrices2+1/6units9codes/P0/depart')
