"""TEST-mode series; no hardware/OPC acceptance and no quantity commit."""
from pathlib import Path
import sys,json,time
from datetime import datetime,timedelta,timezone
sys.path.insert(0,str(Path(__file__).parent))
import assembly_scope_fixture as f
from app.modules.inventory.infrastructure.warehouse_scales import WarehouseScales
from app.modules.inventory.contracts_warehouse_scale import WarehouseScaleConfiguration,WarehouseFinalScalePacket
from app.modules.inventory.infrastructure.assembly_scale import AssemblyScales,wire
from app.modules.inventory.contracts_assembly_scale import AssemblyStationPolicy,AssemblySkuPolicy,AssemblySessionOpen,AssemblyStepOpen,AssemblyCapture
from app.modules.platform.public import read_oracle_json
import oracledb
x=json.loads((f.BASE/'fixture.json').read_text());g=f.OracleGateway();assert x['state']=='SCOPED_OPERATOR_STARTED'
out=f.BASE/'test-mass-stage.json';assert not out.exists()
report=dict(state='PREPARED',hardware_verified=False,device_mode='TEST',stock_effects=0)
def save():out.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8');f.save(x)
with out.open('x',encoding='utf-8')as stream:json.dump(report,stream)
def stamp(t=None):return(t or datetime.now(timezone.utc)).strftime('%Y-%m-%dT%H:%M:%S.%f+00:00')
def nopost(command):raise AssertionError('Mass stage cannot commit quantity')
def invoke(name,body,actor):
 report.setdefault('requests',{})[name]=body.model_dump();save()
 with g.transaction('AS16 TEST evidence '+name)as c:
  result=c.var(oracledb.DB_TYPE_CLOB);c.callproc('RRL_ASSEMBLY_SCALE_API.capture',[wire(body),actor,result]);return read_oracle_json(result.getvalue())
calibration=x['prefix']+'.TEST'
config=WarehouseScaleConfiguration(warehouse_id=x['warehouse_id'],post_cell=x['cell'],sender_id=x['sender'],expected_version=0,active=True,device_mode='TEST',basis='GROSS',capacity_kg='100',resolution_kg='0.001',calibration_ref=calibration,calibrated_until=stamp(datetime.now(timezone.utc)+timedelta(days=1)))
report['device_request']=config.model_dump();save();report['device']=WarehouseScales(g).configure(x['device'],config,'admin');save()
assembly=AssemblyScales(g,nopost)
station=AssemblyStationPolicy(operation_id=x['prefix']+'.STATION',expected_version=0,confirmation_mode='AUTO',max_session_seconds=21600,cumulative_tolerance_kg='0.002',active=True,reason=f.NOTE)
report['station_request']=station.model_dump();save();report['station']=assembly.station_policy(x['device'],station,'admin');save()
policy=AssemblySkuPolicy(operation_id=x['prefix']+'.SKU',warehouse_id=x['warehouse_id'],article=x['article'],base_uom='EA',expected_version=0,min_unit_kg='0.99',max_unit_kg='1.01',min_delta_kg='0.01',tolerance_kg='0',active=True,evidence_reference=calibration,reason=f.NOTE)
report['sku_request']=policy.model_dump();save();report['sku']=assembly.sku_policy(policy,'admin');save()
task=g.fetch_all('select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',{'t':x['task_id']})[0];v=task['content_version']
now=datetime.now(timezone.utc)
tare=WarehouseFinalScalePacket(device_id=x['device'],capture_id=x['prefix']+'.TARE',post_cell=x['cell'],case_task_id=x['task_id'],expected_content_version=v,scan_container=x['label']['sscc'],purpose='EMPTY_TARE',device_policy_version=1,calibration_ref=calibration,unit='KG',basis='GROSS',preset_tare_kg='0',zero_confirmed=True,zero_check_kg='0',zero_check_at=stamp(now-timedelta(seconds=10)),measured_at=stamp(now),samples=[dict(offset_ms=i*500,weight_kg='0.5')for i in range(5)])
report['tare_request']=tare.model_dump(exclude_none=True);save();report['tare']=WarehouseScales(g).capture(tare,x['sender']);save();report['refreshed_tare']=report['tare'];save()
x['assembly_session']=x['prefix']+'.SESSION';x['step']=x['prefix']+'.STEP';x['pick_operation']=x['prefix']+'.PICK'
body=AssemblySessionOpen(session_id=x['assembly_session'],task_id=x['task_id'],device_id=x['device'],expected_content_version=v,tare_capture_key=report['tare']['capture_key'],scan_container=x['label']['sscc'])
report['session_request']=body.model_dump();save();report['session']=assembly.open_session(body,x['actor']);save()
body=AssemblyStepOpen(step_id=x['step'],operation_id=x['pick_operation'],case_line_id=x['case_line_id'],quantity='1',scan_source_cell=x['cell'],scan_product=x['article'],scan_container=x['label']['sscc'],expected_content_version=v,consent_to_auto=True)
report['step_request']=body.model_dump();save();report['step']=assembly.open_step(x['assembly_session'],body,x['actor']);save()
for phase,weight in[('BEFORE','0.5'),('AFTER','1.5')]:
 time.sleep(2.1)
 requests=assembly.gateway_requests(x['device'],x['sender'])['items'];assert len(requests)==1 and requests[0]['phase']==phase
 packet=AssemblyCapture(session_id=x['assembly_session'],step_id=x['step'],capture_id=requests[0]['capture_id'],phase=phase,device_id=x['device'],device_policy_version=1,calibration_ref=calibration,unit='KG',basis='GROSS',preset_tare_kg='0',tare_mode_clear=True,quality_confirmed=True,measured_at=stamp(),samples=[dict(offset_ms=i*500,weight_kg=weight)for i in range(5)])
 report[phase]=invoke(phase,packet,x['sender']);save()
report['current']=assembly.read_step(x['step'],x['actor']);assert report['current']['state']=='READY'
report['post_context']=assembly._read_post(x['step'],x['actor']);assert report['post_context']['eligible']is True
x['state']='SCOPED_ASM_READY_NO_QUANTITY_COMMIT';report['state']='PASS';save()
print(json.dumps(dict(state=x['state'],task=x['task_id'],step=x['step'],flat_execute=0,hardware_verified=False)))
