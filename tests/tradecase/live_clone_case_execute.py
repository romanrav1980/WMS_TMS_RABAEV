"""BLC-only operator moves and picks a bought clone through real native task/session APIs."""
from pathlib import Path
from uuid import uuid4
import sys,os,json,secrets
sys.path[:0]=['.','tests/tradecase']
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
P=Path('runtime/test-evidence/tradecase/2026-10-19/T06/clone-case.json');s=json.loads(P.read_text())
def save():P.write_text(json.dumps(s,indent=2,default=str))
def run():
 w=s['warehouse_id'];base=f'/api/tradecase/warehouses/{w}'
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
  if 'actor'not in s:
   actor='T6C'+uuid4().hex[:9];password=secrets.token_hex(24)
   q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'TRADECASE clone picker','TC03QA',:w,0,1)",a=actor,p=password,w=w)
   q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'TRADECASE clone picker',1,1)",a=actor)
   for perm in ['case_pick_execute','case_pick_view','warehouse_task_execute']:q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)',a=actor,p=perm)
   q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '4'hour,'admin','BLC-only clone physical acceptance',1)",a=actor,w=str(w));c.commit();s['actor']=actor;save()
  q.execute('select PASS from RUSERS where ID=:a and nvl(DELETED,0)=0',a=s['actor']);row=q.fetchone();assert row,'QA actor was retired; do not reactivate';password=row[0]
 actor=s['actor']
 if 'owner_grant'not in s:s['owner_grant']=expect(200,http('PUT',base+'/stock/owner-grants',dict(operation_id='T6C.owner.'+actor,expected_version=0,username=actor,owner_id='BLC',can_view=True,can_operate=True,reason='Only BLC operates the bought clone; SNS is not granted')));save()
 def own(method,path,body=None):return http(method,path,body,actor,password)
 task=s['replenishment_tasks'][0]
 if 'shift'not in s:s['shift']=expect(200,http('POST','/api/resources/shifts',dict(shift_code=actor,shift_date='2026-10-19',start_at='2026-10-19T00:00:00+03:00',finish_at='2026-10-19T23:59:59+03:00',ware_id=w,status='OPEN')))['id'];save()
 if 'reach_equipment'not in s:s['reach_equipment']=expect(200,http('POST','/api/resources/equipment',dict(equipment_code=actor+'.REACH',equipment_type='REACHTRUCK',equipment_name='QA reachtruck, no hardware proof',ware_id=w)))['id'];save()
 if 'reach_resource'not in s:s['reach_resource']=expect(200,http('POST','/api/resources',dict(resource_code=actor+'.REACH',resource_name='QA reachtruck operator',resource_type='REACHTRUCK',resource_class='WAREHOUSE_EQUIPMENT',equipment_id=s['reach_equipment'],user_id=actor,ware_id=w)))['id'];save()
 if 'reach_qualification'not in s:s['reach_qualification']=expect(200,http('PUT',f"/api/resources/{s['reach_resource']}/qualifications",dict(task_type='REPLENISHMENT',active=True)));save()
 if 'reach_session'not in s:s['reach_session']=expect(200,http('POST','/api/resources/sessions/login',dict(shift_id=s['shift'],resource_id=s['reach_resource'],equipment_id=s['reach_equipment'],operator_user_id=actor,terminal_id='QA_NOT_HARDWARE')))['id'];save()
 for key,action in [('reach_assigned','ASSIGN'),('reach_started','START')]:
  if key not in s:
   context=expect(200,http('GET',f'/api/warehouse-tasks/{task[0]}/resource-context?target='+actor))
   body=dict(operation_id='T6C.REPL.'+action,action=action,target=actor,expected_assignment_version=context['assignment_version'],expected_task_signature=context['task_signature'],resource_session_id=s['reach_session'],resource_id=s['reach_resource'],equipment_id=s['reach_equipment'])
   s[key]=expect(200,http('POST',f'/api/warehouse-tasks/{task[0]}/resource-commands',body)if action=='ASSIGN'else own('POST',f'/api/warehouse-tasks/{task[0]}/resource-commands',body));assert s[key]['outcome']=='APPLIED';save()
 if 'repl_complete'not in s:
  context=expect(200,own('GET',f'/api/warehouse-tasks/{task[0]}/resource-context'));s['repl_body']=dict(operation_id='T6C.REPL.COMPLETE.V2',expected_task_signature=context['task_signature'],scanned_pallet=task[2],scanned_from_cell=task[3],scanned_to_cell=task[4],fact_qty=str(task[5]));save()
  s['repl_complete']=expect(200,own('POST',f'/api/warehouse-tasks/{task[0]}/complete',s['repl_body']));save()
 assert expect(200,own('POST',f'/api/warehouse-tasks/{task[0]}/complete',s['repl_body']))==s['repl_complete']
 if 'reach_logout'not in s:s['reach_logout']=expect(200,http('POST',f"/api/resources/sessions/{s['reach_session']}/logout",dict(reason='QA physical replenishment completed')));save()
 if 'released'not in s:s['released']=expect(200,http('POST',f"/api/picking/waves/{s['wave']}/release-picking",dict(operation_id='T6C.RELEASE')));save()
 with oracle_connection()as c:
  q=c.cursor();q.execute('select CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,PICK_TASK_ID from RRL_CASE_PICK_LINE where PICK_WAVE_ID=:w',w=s['wave']);rows=q.fetchall();assert len(rows)==1,rows;s['case_id'],s['line_id'],s['pick_task_id']=rows[0]
  q.execute('select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=s['case_id']);s['carrier'],version=q.fetchone();save()
 if 'tare_book'not in s:
  s['tare_count']=expect(200,http('POST','/api/inventory/tare/count',dict(operation_id='T6C.TARE.COUNT',owner_ware_id=w,pallet_type_id=1,condition='GOOD',observed_quantity='1',expected_version=0,reason='Synthetic isolated QA pallet count, not a physical survey',decision_reference='TEST_FIXTURE_NOT_HARDWARE:T6C')));save()
  s['tare_book']=expect(200,http('POST','/api/inventory/tare/book',dict(operation_id='T6C.TARE.BOOK',place_kind='CASE',place_id=str(s['case_id']),expected_warehouse_id=w,pallet_type_id=1)));save()
 if 'resource'not in s:s['resource']=expect(200,http('POST','/api/resources',dict(resource_code=actor,resource_name='QA clone picker',resource_type='CASE_PICKER',resource_class='PERSON',user_id=actor,ware_id=w)))['id'];save()
 if 'qualification'not in s:s['qualification']=expect(200,http('PUT',f"/api/resources/{s['resource']}/qualifications",dict(task_type='CASE_PICK',active=True)));save()
 if 'shift'not in s:s['shift']=expect(200,http('POST','/api/resources/shifts',dict(shift_code=actor,shift_date='2026-10-19',start_at='2026-10-19T00:00:00+03:00',finish_at='2026-10-19T23:59:59+03:00',ware_id=w,status='OPEN')))['id'];save()
 if 'session'not in s:s['session']=expect(200,http('POST','/api/resources/sessions/login',dict(shift_id=s['shift'],resource_id=s['resource'],operator_user_id=actor,terminal_id='QA_KEYBOARD_NOT_HARDWARE')))['id'];save()
 if 'claim_owner_denied'not in s:
  expect(200,http('PUT',base+'/stock/owner-grants',dict(operation_id='T6C.owner.readonly',expected_version=1,username=actor,owner_id='BLC',can_view=True,can_operate=False,reason='Reject marked CASE claim without current owner operation rights')))
  s['claim_owner_denied']=expect(403,own('POST',f"/api/case-pick/tasks/{s['case_id']}/resource-commands",dict(operation_id='T6C.CASE.CLAIM.DENIED',action='CLAIM',expected_assignment_version=0,resource_session_id=s['session'],resource_id=s['resource'],reason='Verify denial without owner operate')));save()
  expect(200,http('PUT',base+'/stock/owner-grants',dict(operation_id='T6C.owner.restore',expected_version=2,username=actor,owner_id='BLC',can_view=True,can_operate=True,reason='Restore owned BLC operation rights for actual CASE')));s['owner_restored']=True;save()
 if 'claimed'not in s:
  ctx=expect(200,own('GET',f"/api/case-pick/tasks/{s['case_id']}/resource-context"));s['claim_body']=dict(operation_id='T6C.CASE.CLAIM.V2',action='CLAIM',expected_assignment_version=ctx['assignment_version'],resource_session_id=s['session'],resource_id=s['resource'],reason='Claim owned marked CASE through current qualified session');save()
  s['claimed']=expect(200,own('POST',f"/api/case-pick/tasks/{s['case_id']}/resource-commands",s['claim_body']));assert s['claimed']['outcome']=='APPLIED';save()
 if 'started'not in s:
  ctx=expect(200,own('GET',f"/api/case-pick/tasks/{s['case_id']}/resource-context"));s['start_body']=dict(operation_id='T6C.CASE.START.V2',action='START',expected_assignment_version=ctx['assignment_version'],resource_session_id=s['session'],resource_id=s['resource'],reason='Physical clone acceptance through current own resource session');save()
  s['started']=expect(200,own('POST',f"/api/case-pick/tasks/{s['case_id']}/resource-commands",s['start_body']));assert s['started']['outcome']=='APPLIED';save()
 if 'pick_body'not in s:
  with oracle_connection()as c:
   q=c.cursor();q.execute("select c.SYSTEM_CODE,c.RAW_CODE from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID join RRL_STOCK_RESERVATION r on r.RESERVATION_ID=u.HARD_RESERVATION_ID where r.SOURCE_DOC_TYPE='PICK_WAVE'and r.SOURCE_LINE_ID=:p and r.STATUS in('ACTIVE','ALLOCATED','PICKING')order by u.UNIT_ID",p=s['pick_task_id']);scans=[dict(system_code=system,profile_code='TOBACCO',code=raw.read()if hasattr(raw,'read')else raw)for system,raw in q];assert len(scans)==1
  s['pick_body']=dict(operation_id='T6C.CASE.PICK',fact_qty='1',scan_cell=s['pick_cell'],scan_product=s['article'],scan_container=s['carrier'],resource_id=s['resource'],resource_session_id=s['session'],unit_scans=scans);save()
 if 'picked'not in s:s['picked']=expect(200,own('POST',f"/api/case-pick/tasks/{s['case_id']}/lines/{s['line_id']}/confirm",s['pick_body']));save()
 assert expect(200,own('POST',f"/api/case-pick/tasks/{s['case_id']}/lines/{s['line_id']}/confirm",s['pick_body']))==s['picked']
 if 'closed'not in s:s['closed']=expect(200,own('POST',f"/api/case-pick/tasks/{s['case_id']}/close-current",dict(operation_id='T6C.CASE.CLOSE',expected_content_version=1)));save()
 with oracle_connection()as c:
  q=c.cursor();q.execute('select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=s['case_id']);version=q.fetchone()[0]
 if 'moved'not in s:s['moved']=expect(200,own('POST',f"/api/case-pick/tasks/{s['case_id']}/move-carrier",dict(operation_id='T6C.CASE.WAIT',scan_container=s['carrier'],scanned_to_cell=s['wait_cell'],expected_content_version=version)));save()
 with oracle_connection()as c:
  q=c.cursor();q.execute('select r.UID_POLETA,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w and r.REMAIN>0 order by r.REMAIN',w=w);s['final_stock']=[list(r)for r in q];assert sum(x[2]for x in s['final_stock'])==250 and sum(x[3]for x in s['final_stock'])==1
  q.execute("select count(*)from RRL_TRADE_OWNER_GRANT where USERNAME=:a and OWNER_ID='SNS'and CAN_OPERATE=1",a=actor);assert q.fetchone()[0]==0
 s['status']='PASS_CLONE_CASE';s['source_session']='TEST_FIXTURE_NO_SHIFT_NORM_OR_PRODUCTIVITY_CLAIM';s.pop('error',None);print(json.dumps(dict(status=s['status'],case=s['case_id'],actor=actor,stock=s['final_stock'])))
if __name__=='__main__':
 try:run()
 except Exception as e:s['status']='FAIL';s['error']=str(e);raise
 finally:s['history']+=CALLS;save()
