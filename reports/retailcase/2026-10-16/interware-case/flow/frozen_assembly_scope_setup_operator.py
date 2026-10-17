from pathlib import Path
import sys,json
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).parent))
import assembly_scope_fixture as f
from app.schemas import ResourceCreateRequest,ResourceShiftCreateRequest,ResourceSessionLoginRequest,RightsGrantRequest
from app.routers.admin_rights import grant_group_right,revoke_group_right
from app.auth import AdminUser
from app.modules.inventory.infrastructure.case_labels import CaseLabels
from app.modules.inventory.contracts_case_labels import CaseSsccLabelRequest
from app.modules.resources.infrastructure.case_resource_commands import CaseResourceCommands
from app.modules.resources.contracts_case_resource import CaseResourceCommand
x=json.loads((f.BASE/'fixture.json').read_text());g=f.OracleGateway();assert x['state']=='FRESH_CASE_READY'
out=f.BASE/'operator-setup.json';assert not out.exists()
report=dict(state='PREPARED',actor=x['actor'],task=x['task_id'],hardware_verified=False)
def save():out.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8');f.save(x)
with out.open('x',encoding='utf-8')as stream:json.dump(report,stream)
admin=AdminUser(username='admin',display_name='Root isolated fixture',user_group='GLOBAL_ADMIN',permissions={'*'})
report['temporary_flat']=grant_group_right(x['actor'],RightsGrantRequest(right_name='case_pick_execute',description=f.NOTE),admin);save()
svc=f.ResourceManagementService(g)
x['resource_id']=svc.create_resource(ResourceCreateRequest(resource_code=x['prefix'],resource_name=f.NOTE,resource_type='CASE_PICKER',user_id=x['actor'],ware_id=x['warehouse_id'],created_by='admin'));save()
report['qualification']=f.QualificationAdmin(g).set_qualification(x['resource_id'],'CASE_PICK',True,'admin');save()
now=datetime.now(ZoneInfo('Europe/Moscow'))
x['shift_id']=svc.create_shift(ResourceShiftCreateRequest(shift_code=x['prefix'],shift_date=now.date(),start_at=now-timedelta(minutes=1),finish_at=now+timedelta(hours=6),ware_id=x['warehouse_id'],status='OPEN',created_by='admin'));save()
x['resource_session_id']=svc.login_session(ResourceSessionLoginRequest(shift_id=x['shift_id'],resource_id=x['resource_id'],operator_user_id=x['actor'],terminal_id='TEST:'+x['prefix'],created_by='admin'));save()
report['flat_revoked']=revoke_group_right(x['actor'],'case_pick_execute',admin);save()
f.acl(g,x,'ROLE_SAVE',dict(role_id=x['role'],title=f.NOTE,permissions=['case_pick_execute'],active=True,expected_version=0),'ROLE')
now=datetime.now(timezone.utc)
f.acl(g,x,'ASSIGN',dict(assignment_id=x['assignment'],username=x['actor'],role_id=x['role'],scope_kind='WAREHOUSE',scope_id=str(x['warehouse_id']),valid_from=(now-timedelta(minutes=1)).isoformat(),valid_until=(now+timedelta(hours=6)).isoformat(),expected_version=0,reason=f.NOTE),'ASSIGN')
t=x['case_before'];f.post(x,'CASE_PALLET_TYPE_CHANGE',{'case_task_id':x['task_id']},dict(expected_version=t['content_version'],scan_container=t['sscc'],pallet_type_id=32,reason=f.NOTE),'TYPE')
t=g.fetch_all('select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',{'t':x['task_id']})[0]
labels=CaseLabels(g);x['label']=labels.issue(x['task_id'],CaseSsccLabelRequest(operation_id=x['prefix']+'.LABEL',scan_container=t['sscc'],expected_content_version=t['content_version']),'admin');save()
report['simulated_label_confirmation']=labels.confirm(x['task_id'],x['label']['sscc'],'admin');save()
balance=g.fetch_all('select BALANCE_VERSION from RRL_TARE_AVAILABILITY where OWNER_WARE_ID=:w and PALLET_TYPE_ID=32',{'w':x['warehouse_id']});assert not balance
f.post(x,'TARE_COUNT',{},dict(owner_ware_id=x['warehouse_id'],pallet_type_id=32,condition='GOOD',observed_quantity='1',expected_version=0,reason=f.NOTE,decision_reference=x['prefix']+'.SIMULATED'),'TARE.COUNT')
f.post(x,'TARE_BOOK',dict(place_kind='CASE',place_id=str(x['task_id'])),dict(pallet_type_id=32,expected_warehouse_id=x['warehouse_id']),'TARE.BOOK')
commands=CaseResourceCommands(g)
for i,action in enumerate(['CLAIM','START']):
 report[action]=commands.command(x['task_id'],CaseResourceCommand(operation_id=x['prefix']+'.'+action,action=action,expected_assignment_version=i,resource_session_id=x['resource_session_id'],reason=f.NOTE),x['actor']);save()
assert g.fetch_all("select RRL_HAS_WRIGHT(:a,'case_pick_execute')F,RRL_CASE_TASK_ACCESS.scoped_assembly_executor(:t,:a)S from dual",{'a':x['actor'],'t':x['task_id']})==[dict(f=0,s=1)]
x['state']='SCOPED_OPERATOR_STARTED';report['state']='PASS';save()
print(json.dumps({k:x[k]for k in('state','task_id','resource_id','resource_session_id')}))
