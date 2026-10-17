"""Fresh ordinary 24EA box +1EA pick, foreign-home flat+WARE role, retained mixed-tree QA."""
from pathlib import Path
import sys,json,secrets
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).parent));import assembly_scope_fixture as f
from app.schemas import ResourceCreateRequest,ResourceShiftCreateRequest,ResourceSessionLoginRequest,CasePickLineConfirmRequest
from app.modules.inventory.infrastructure.case_labels import CaseLabels
from app.modules.inventory.contracts_case_labels import CaseSsccLabelRequest
from app.modules.resources.infrastructure.case_resource_commands import CaseResourceCommands
from app.modules.resources.contracts_case_resource import CaseResourceCommand
from app.modules.inventory.infrastructure.case_current_close import CaseCurrentClose
from app.modules.inventory.contracts_case_current_close import CaseCurrentCloseInput
from app.modules.inventory.infrastructure.case_pick_commands import post_case_pick
base=Path('C:\\projects\\TMS\\reports\\retailcase\\2026-10-16\\kpi-pick-proof\\forward');parent=json.loads((f.BASE/'fixture.json').read_text());tree=json.loads((base/'fixture.json').read_text())
out=base/'ordinary-child.json';resume=('--resume' in sys.argv or '--resume-pick' in sys.argv)
if not resume:assert not out.exists()
tag=secrets.token_hex(5);x=dict(prefix='OC16.'+tag,actor='OC16P'+tag,role='OC16R'+tag,assignment='OC16A'+tag,source='OC16.LOT:'+tag,warehouse_id=parent['warehouse_id'],article=parent['article'],cell=parent['cell'],face=parent['face'],revision=parent['revision'],hardware_verified=False,state='PREPARED')
# Own journal separate from retained HU fixture.
own=base/'ordinary';own.mkdir(exist_ok=True);f.BASE=own;g=f.OracleGateway()
report=dict(state='PREPARED',hardware_verified=False,quantity_base='25',steps=[])
if resume:
 x=json.loads((own/'fixture.json').read_text());report=json.loads(out.read_text());assert x['label']['sscc']
def save():out.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8');f.save(x)
if not resume:
 with out.open('x',encoding='utf-8')as stream:json.dump(report,stream)
if not resume:
 save();pw=secrets.token_urlsafe(32)
 with(f.root/'runtime'/('ordinary-child-'+tag+'-secrets.json')).open('x',encoding='utf-8')as stream:json.dump({x['actor']:pw},stream)
 with f.stock_configuration_transaction(g,f.NOTE,'admin','warehouse_settings_edit')as c:
  c.execute('insert into USER_GROUP(ID,NAME)values(:id,:n)',id=x['actor'],n=f.NOTE)
  c.execute('insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:pw,:n,:id,1,0,0)',id=x['actor'],pw=pw,n=f.NOTE)
  c.execute("insert into RIGHTS(ID,USER_GROUP,RIGHT1,DESCR)select nvl(max(ID),0)+1,:a,'CASE_PICK_EXECUTE',:n from RIGHTS",a=x['actor'],n=f.NOTE)
  x['box_barcode']=x['prefix']+'.BOX24'
  c.execute('update RRL_ARTICULS set BARCODE_KOR=:v where ACTICUL=:a',v=x['box_barcode'],a=x['article']);assert c.rowcount==1
  for key,seq in [('order','RRL_CUSTOMER_ORDER_SQ'),('order_row','RRL_CUSTOMER_ORDER_ROW_SQ'),('plan','RRL_PICK_PLAN_SQ'),('line','RRL_PICK_PLAN_LINE_SQ'),('task','RRL_PICK_TASK_SQ'),('reservation','RRL_PICK_RESERVATION_SQ'),('wave','RRL_PICK_WAVE_SQ'),('wave_order','RRL_PICK_WAVE_ORDER_SQ')]:
   c.execute('select '+seq+'.nextval from dual');x[key]=int(c.fetchone()[0])
  f.demand.WARE=x['warehouse_id'];f.demand.CELL=x['cell'];f.demand.SOURCE=x['source'];f.demand.ARTICLE=x['article'];f.demand.create_demand(c,x)
  for table,key,id_column,assign in [('RRL_CUSTOMER_ORDER_ROW','order_row','CUSTOMER_ORDER_ROW_ID','ORDER_QTY=25'),('RRL_PICK_PLAN','plan','PICK_PLAN_ID','TOTAL_ORDER_QTY=25,TOTAL_PLANNED_QTY=25'),('RRL_PICK_PLAN_LINE','line','PICK_PLAN_LINE_ID','REQUESTED_QTY=25,PLANNED_QTY=25,CASE_PICK_QTY=25'),('RRL_PICK_TASK','task','PICK_TASK_ID','QTY=25'),('RRL_PICK_RESERVATION','reservation','PICK_RESERVATION_ID','RESERVED_QTY=25')]:
   c.execute('update '+table+' set '+assign+' where '+id_column+'=:v',v=x[key]);assert c.rowcount==1
 x['state']='METADATA_CREATED';save()
 f.acl(g,x,'ROLE_SAVE',dict(role_id=x['role'],title=f.NOTE,permissions=['case_pick_execute'],active=True,expected_version=0),'ROLE')
 now=datetime.now(timezone.utc)
 f.acl(g,x,'ASSIGN',dict(assignment_id=x['assignment'],username=x['actor'],role_id=x['role'],scope_kind='WAREHOUSE',scope_id=str(x['warehouse_id']),valid_from=(now-timedelta(minutes=1)).isoformat(),valid_until=(now+timedelta(hours=6)).isoformat(),expected_version=0,reason=f.NOTE),'ASSIGN')
 f.post(x,'INVENTORY_REGISTER_LOT',dict(revision_id=x['revision']),dict(uid=x['source'],cell=x['cell'],article=x['article'],quantity='25',expiry_date='2030-01-01',price='0',reason=f.NOTE),'BIRTH')
 picking=f.PickingService(g);picking.preview_wave(x['wave'],f.PickWaveActionRequest(updated_by='admin'));x['launch']=picking.launch_wave(x['wave'],f.PickWaveActionRequest(updated_by='admin',operation_id=x['prefix']+'.LAUNCH'));save()
 rows=g.fetch_all('select CASE_PICK_TASK_ID,CONTENT_VERSION,SSCC from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:w',{'w':x['wave']});assert len(rows)==1;x['task_id']=rows[0]['case_pick_task_id'];x['case_before']=rows[0];save()
 rows=g.fetch_all('select CASE_PICK_LINE_ID,PLANNED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:t',{'t':x['task_id']});assert len(rows)==1 and rows[0]['planned_qty']==25;x['case_line_id']=rows[0]['case_pick_line_id'];save()
 f.post(x,'WAVE_PICK_RELEASE',dict(wave_id=x['wave']),{},'RELEASE')
 svc=f.ResourceManagementService(g)
 x['resource_id']=svc.create_resource(ResourceCreateRequest(resource_code=x['prefix'],resource_name=f.NOTE,resource_type='CASE_PICKER',user_id=x['actor'],ware_id=x['warehouse_id'],created_by='admin'));save()
 report['qualification']=f.QualificationAdmin(g).set_qualification(x['resource_id'],'CASE_PICK',True,'admin');save()
 now=datetime.now(ZoneInfo('Europe/Moscow'))
 x['shift_id']=svc.create_shift(ResourceShiftCreateRequest(shift_code=x['prefix'],shift_date=now.date(),start_at=now-timedelta(minutes=1),finish_at=now+timedelta(hours=6),ware_id=x['warehouse_id'],status='OPEN',created_by='admin'));save()
 x['resource_session_id']=svc.login_session(ResourceSessionLoginRequest(shift_id=x['shift_id'],resource_id=x['resource_id'],operator_user_id=x['actor'],terminal_id='TEST:'+x['prefix'],created_by='admin'));save()
 t=x['case_before'];f.post(x,'CASE_PALLET_TYPE_CHANGE',dict(case_task_id=x['task_id']),dict(expected_version=t['content_version'],scan_container=t['sscc'],pallet_type_id=32,reason=f.NOTE),'TYPE')
 t=g.fetch_all('select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',{'t':x['task_id']})[0]
 labels=CaseLabels(g);x['label']=labels.issue(x['task_id'],CaseSsccLabelRequest(operation_id=x['prefix']+'.LABEL',scan_container=t['sscc'],expected_content_version=t['content_version']),'admin');save();report['label_confirm']=labels.confirm(x['task_id'],x['label']['sscc'],'admin');save()
if '--resume-pick' not in sys.argv:
 balance=g.fetch_all('select BALANCE_VERSION,PHYSICAL_QTY from RRL_TARE_AVAILABILITY where OWNER_WARE_ID=:w and PALLET_TYPE_ID=32',{'w':x['warehouse_id']});assert len(balance)==1 and balance[0]['physical_qty']==1
 f.post(x,'TARE_COUNT',{},dict(owner_ware_id=x['warehouse_id'],pallet_type_id=32,condition='GOOD',observed_quantity='2',expected_version=balance[0]['balance_version'],reason=f.NOTE,decision_reference=x['prefix']+'.SIMULATED'),'TARE.COUNT')
 f.post(x,'TARE_BOOK',dict(place_kind='CASE',place_id=str(x['task_id'])),dict(pallet_type_id=32,expected_warehouse_id=x['warehouse_id']),'TARE.BOOK')
 commands=CaseResourceCommands(g)
 for i,action in enumerate(['CLAIM','START']):
  result=commands.command(x['task_id'],CaseResourceCommand(operation_id=x['prefix']+'.'+action,action=action,expected_assignment_version=i,resource_session_id=x['resource_session_id'],reason=f.NOTE),x['actor']);report['steps'].append(dict(action=action,result=result));save()
 classifier=g.fetch_all("select RRL_HAS_WRIGHT(:a,'case_pick_execute')F,RRL_CASE_TASK_ACCESS.legacy_executor(:t,:a)L,RRL_CASE_TASK_ACCESS.has_current_scoped_execute(:t,:a)S from dual",{'a':x['actor'],'t':x['task_id']});assert classifier==[dict(f=1,l=0,s=1)];report['classifier']=classifier;save()
if '--capture-test-tare' in sys.argv:
 from app.modules.inventory.infrastructure.warehouse_scales import WarehouseScales
 from app.modules.inventory.contracts_warehouse_scale import WarehouseFinalScalePacket
 def stamp(t):return t.strftime('%Y-%m-%dT%H:%M:%S.%f+00:00')
 now=datetime.now(timezone.utc);ct=g.fetch_all('select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',{'t':x['task_id']})[0]
 body=WarehouseFinalScalePacket(device_id=parent['device'],capture_id=x['prefix']+'.TARE',post_cell=x['cell'],case_task_id=x['task_id'],expected_content_version=ct['content_version'],scan_container=x['label']['sscc'],purpose='EMPTY_TARE',device_policy_version=1,calibration_ref=parent['prefix']+'.TEST',unit='KG',basis='GROSS',preset_tare_kg='0',zero_confirmed=True,zero_check_kg='0',zero_check_at=stamp(now-timedelta(seconds=10)),measured_at=stamp(now),samples=[dict(offset_ms=i*500,weight_kg='0.5')for i in range(5)])
 report['empty_tare_request']=body.model_dump(mode='json');save();report['empty_tare']=WarehouseScales(g).capture(body,parent['sender']);save()
time_service=build_picker_time_service()
def time_command(action):
 state=time_service.current(x['actor']);values=dict(operation_id=x['prefix']+'.TIME.'+action,action=action,expected_version=state['stream_version'],resource_session_id=x['resource_session_id'],reason=f.NOTE)
 if action not in ('ACTUAL_SHIFT_START','ACTUAL_SHIFT_FINISH'):values.update(source_kind='CASE_PICK_TASK',source_id=x['task_id'])
 x.setdefault('time_requests',{})[action]=values;save();ack=time_service.command(PickerTimeCommand(**values),x['actor']);x.setdefault('time_results',{})[action]=ack;save();assert ack['outcome']=='APPLIED',ack
 return ack
time_command('ACTUAL_SHIFT_START');time_command('WORK_START')
for cumulative,scan,label in [('24',x['box_barcode'],'BOX24'),('25',x['article'],'EA1')]:
 body=CasePickLineConfirmRequest(fact_qty=cumulative,operation_id=x['prefix']+'.'+label,scan_cell=x['cell'],scan_product=scan,scan_container=x['label']['sscc'],resource_id=x['resource_id'],resource_session_id=x['resource_session_id'],actor=x['actor'])
 x.setdefault('pick_bodies',{})[label]=body.model_dump(mode='json');save()
 if label=='EA1':time_command('PAUSE');time_command('RESUME')
 result=post_case_pick(g,x['task_id'],x['case_line_id'],body);assert post_case_pick(g,x['task_id'],x['case_line_id'],body)==result;report['steps'].append(dict(action=label,result=result,replay_exact=True));save()
time_command('WORK_FINISH');time_command('ACTUAL_SHIFT_FINISH')
ct=g.fetch_all('select CONTENT_VERSION,PICKED_QTY from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',{'t':x['task_id']})[0];assert ct['picked_qty']==25
body=CaseCurrentCloseInput(operation_id=x['prefix']+'.CLOSE',expected_content_version=ct['content_version']);result=CaseCurrentClose(g).close(x['task_id'],body,x['actor']);assert CaseCurrentClose(g).close(x['task_id'],body,x['actor'])==result
report['close']=result;x['state']='ORDINARY_BOX24_EA1_CLOSED_RETAINED';report['state']='PASS_FOREIGN_FLAT_ROLE_NEW_QUANTITY';save();print(json.dumps(dict(state=report['state'],task=x['task_id'],steps=len(report['steps']))))
