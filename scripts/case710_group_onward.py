exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.interwarehouse_group_onward import InterwarehouseGroupOnward
from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
from app.modules.transport.public import assign_sts
from app.oracle_gateway import OracleGateway
import httpx
p=Path('tmp/context671.json');saved=json.loads(p.read_text(encoding='utf-8'));tag=saved['first']['tag'];gw=OracleGateway();service=InterwarehouseGroupOnward(gw)
op='GROUP710.ONWARD:'+tag;receipt=saved['group_receipt_operation_id'];reason='Own whole two-SKU original ST continuation';reference='DEV710:'+tag
if 'group_onward'not in saved:
 saved['group_onward']=service.prepare(op,receipt,reason,reference,'admin');p.write_text(json.dumps(saved,indent=2),encoding='utf-8')
assert service.prepare(op,receipt,reason,reference,'admin')==saved['group_onward']
if 'group_assigned'not in saved:
 assign_sts(gw,saved['group_plan']['target_trip_id'],[x['st_number']for x in saved['group_onward']['members']],'admin')
 saved['group_assigned']=True;p.write_text(json.dumps(saved,indent=2),encoding='utf-8')
for index,part in enumerate(saved['group_onward']['members']):
 key='group_qc'+str(index)
 if key in saved:continue
 ctx=next(x for x in [saved['first'],saved['second']]if x['lot']==part['pallet_identifier'])
 proof=OutgoingQuality(gw).status(part['shipment_identifier'],'admin')
 with httpx.Client(auth=('admin','admin123'),timeout=40)as client:
  r=client.post('http://127.0.0.1:8088/api/outgoing-quality/'+part['shipment_identifier']+'/scan',json=dict(operation_id='GROUP710.QC:'+str(index)+':'+tag,expected_composition_signature=proof['composition_signature'],error_count=0,scans=[code for unit in ctx['units']for code in unit['codes']]))
  assert r.status_code==200,r.text;saved[key]=r.json();p.write_text(json.dumps(saved,indent=2),encoding='utf-8')
print('PASS710 existingST constructors/perlot frozenrecipient/sourceFF retained/atomicgroup preparation/replay/existingassignment/QC9codes/noquantity')
