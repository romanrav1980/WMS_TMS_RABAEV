"""Fresh TEST final gross via real intent/claim and existing manager ST binding."""
from pathlib import Path
import sys,json,time
from datetime import datetime,timedelta,timezone
sys.path.insert(0,str(Path(__file__).parent))
import assembly_scope_fixture as f
from app.modules.inventory.infrastructure.case_shipment_binding import bind_case_shipment
from app.modules.inventory.infrastructure.warehouse_scale_requests import WarehouseWeighRequests
from app.modules.inventory.infrastructure.warehouse_scales import WarehouseScales
from app.modules.inventory.contracts_warehouse_scale import WarehouseFinalScalePacket
from app.modules.inventory.infrastructure.assembly_scale import AssemblyScales
from app.modules.inventory.contracts_assembly_scale import AssemblyFinish
from app.modules.platform.public import read_oracle_json
import oracledb
x=json.loads((f.BASE/'fixture.json').read_text());assert x['state']=='SCOPED_ASM_CLOSED_WAIT_FINAL'
mass=json.loads((f.BASE/'test-mass-stage.json').read_text());g=f.OracleGateway();out=f.BASE/'finalize.json';resume='--resume-after-binding'in sys.argv
if resume:report=json.loads(out.read_text());assert 'binding'in report and'request'not in report
else:assert not out.exists();report=dict(state='PREPARED',hardware_verified=False,device_mode='TEST',shipping_qc=False)
def save():out.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8');f.save(x)
def create_metadata(c):
 c.execute('select RRL_SBORKA_PALLETS_SQ.nextval from dual');x['st']=int(c.fetchone()[0]);x['st_identifier']=x['prefix']+'.ST'
 c.execute("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,ADDR)values(:id,:u,:u,:w,0,:note)",id=x['st'],u=x['st_identifier'],w=x['warehouse_id'],note=f.NOTE)
 c.execute("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY)values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:u,:a,'EA',1)",u=x['st_identifier'],a=x['article'])
 c.execute("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY)values(RRL_CUSTOMER_ORDER_FULF_SQ.nextval,:o,:st,:u,'PLANNED',0)",o=x['order'],st=x['st'],u=x['st_identifier'])
if not resume:
 with out.open('x',encoding='utf-8')as stream:json.dump(report,stream)
if not resume:
 with f.stock_configuration_transaction(g,f.NOTE,'admin','warehouse_settings_edit')as c:
  create_metadata(c)
save();task=g.fetch_all('select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',{'t':x['task_id']})[0]
if not resume:report['binding']=bind_case_shipment(g,x['task_id'],x['st_identifier'],x['label']['sscc'],task['content_version'],'admin');save()
def no_post(command):raise AssertionError('Finalize cannot write goods quantity')
assembly=AssemblyScales(g,no_post)
context=assembly.context(x['task_id'],x['actor']);assert context['final_signature_domain']=='ASM_FINAL'
snapshot=dict(composition_signature=context['final_composition_signature'])
report['snapshot']=snapshot;save()
requests=WarehouseWeighRequests(g);request_id=x['prefix']+'.FINAL.REQUEST'
body=dict(request_id=request_id,device_id=x['device'],purpose='FINAL_GROSS',case_task_id=x['task_id'],expected_content_version=task['content_version'],scan_container=x['label']['sscc'],tare_capture_key=mass['refreshed_tare']['capture_key'],expected_composition_signature=snapshot['composition_signature'])
report['request_body']=body;save();report['request']=requests.request(body,x['actor']);save()
claim_body=dict(claim_id=x['prefix']+'.FINAL.CLAIM',device_id=x['device']);report['claim_body']=claim_body;save();report['claim']=requests.claim(request_id,claim_body,x['sender']);save()
now=datetime.now(timezone.utc);stamp=lambda t:t.strftime('%Y-%m-%dT%H:%M:%S.%f+00:00')
packet={**report['claim']['capture_context'],**dict(unit='KG',basis='GROSS',preset_tare_kg='0',zero_confirmed=True,zero_check_kg='0',zero_check_at=stamp(now-timedelta(seconds=10)),measured_at=stamp(now),samples=[dict(offset_ms=i*500,weight_kg='1.5')for i in range(5)])}
report['packet']=packet;save();report['capture']=WarehouseScales(g).capture(WarehouseFinalScalePacket(**packet),x['sender']);save()
def no_post(command):raise AssertionError('Finalize cannot write goods quantity')
assembly=AssemblyScales(g,no_post);body=AssemblyFinish(final_capture_key=report['capture']['capture_key'])
report['finish_request']=body.model_dump();save();report['finish']=assembly.finish(x['assembly_session'],body,x['actor']);save()
report['finish_replay']=assembly.finish(x['assembly_session'],body,x['actor']);assert report['finish']==report['finish_replay']and report['finish']['state']=='FINALIZED'
report['request_status']=requests.status(request_id,x['actor']);report['state']='PASS_NATIVE_SCOPED_ASM_FINALIZED_TEST';x['state']='SCOPED_ASM_FINALIZED_TEST';save()
print(json.dumps(dict(state=report['state'],task=x['task_id'],request_claim_capture=True,hardware_verified=False,shipping_qc=False)))
