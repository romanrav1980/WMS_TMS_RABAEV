"""Prepare a scoped manager for exactly one real UI return of the owned10EA QA CASE."""
from pathlib import Path
from uuid import uuid4
import sys,os,json,secrets
sys.path[:0]=['.','tests/tradecase']
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
P=Path('runtime/test-evidence/tradecase/2026-10-19/T11/return-ui-fixture.json');assert not P.exists(),'Already prepared; do not recreate actor'
w=211559882;cid=1158;actor='T11U'+uuid4().hex[:8];password=secrets.token_hex(24);out=dict(warehouse_id=w,case_id=cid,actor=actor)
try:
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
  q.execute("select SSCC,STATUS,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t",t=cid);carrier,status,version=q.fetchone();assert status=='WAIT_CONTROL'and version==2;out['carrier']=carrier
  q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=w);assert list(q.fetchone())==[250,10]
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'QA carrier return UI','TC03QA',:w,0,1)",a=actor,p=password,w=w)
  q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'QA carrier return UI',1,1)",a=actor)
  for right in ['tradecase_view','case_pick_view','case_pick_manage']:q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)',a=actor,p=right)
  q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '2'hour,'admin','Exactly one UI return of QA CASE1158',1)",a=actor,w=str(w));c.commit()
 grantpath=f'/api/tradecase/warehouses/{w}/stock/owner-grants'
 grant=dict(operation_id='T11.UI.OWNER.READ',expected_version=0,username=actor,owner_id='BLC',can_view=True,can_operate=False,reason='Read-only owner must disable physical carrier return')
 expect(200,http('PUT',grantpath,grant))
 lookup=f'/api/case-pick/resolve-carrier?warehouse_id={w}&pallet_identifier={carrier}'
 context=expect(200,http('GET',lookup,None,actor,password));assert context['return_allowed']is False and context['return_blocking_reason']=='PERMISSION';assert context['physical_lots'][0]['physical_qty']=='10';out['view_without_operate']=True
 expect(403,http('GET',f'/api/case-pick/resolve-carrier?warehouse_id=215590763&pallet_identifier={carrier}',None,actor,password));expect(404,http('GET',f'/api/case-pick/resolve-carrier?warehouse_id={w}&pallet_identifier=NOT_A_CASE',None,actor,password));out['foreign_unknown_denied']=True
 grant.update(operation_id='T11.UI.OWNER.OPERATE',expected_version=1,can_operate=True,reason='Allow the owned10EA QA CASE return through the real UI');expect(200,http('PUT',grantpath,grant));context=expect(200,http('GET',lookup,None,actor,password));assert context['return_allowed']is True;out.update(context=context,status='READY_FOR_ONE_UI_RETURN')
 print(json.dumps(dict(status=out['status'],actor=actor,carrier=carrier,physical_lots=len(context['physical_lots']))))
except Exception as e:out.update(status='FAIL',error=str(e));raise
finally:out['http']=CALLS;P.write_text(json.dumps(out,indent=2,default=str))
