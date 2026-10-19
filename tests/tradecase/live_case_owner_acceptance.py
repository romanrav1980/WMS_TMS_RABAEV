"""Role-only CASE legal-owner read filter and command denial, no goods writes."""
from pathlib import Path
import json,os,secrets,sys
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
w=215590763;actor='T6V'+uuid4().hex[:9];password=secrets.token_hex(24);report={}
try:
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:p,'TRADECASE case view QA','TC03QA',:w,0,1)",id=actor,p=password,w=w)
  q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:r,'TRADECASE case view QA',1,1)",r=actor)
  for perm in ['case_pick_view','case_pick_execute','warehouse_task_execute']:q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:r,:p)',r=actor,p=perm)
  q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:r,:r,:r,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '6'hour,'admin','Isolated case owner view acceptance',1)",r=actor,w=str(w));c.commit()
 listing=f'/api/case-pick/tasks?scope=all&ware_id={w}';detail='/api/case-pick/tasks/1155';grant=f'/api/tradecase/warehouses/{w}/stock/owner-grants'
 assert expect(200,http('GET',listing,None,actor,password))==[];expect(404,http('GET',detail,None,actor,password))
 expect(200,http('PUT',grant,dict(operation_id=actor+'.SNS',expected_version=0,username=actor,owner_id='SNS',can_view=True,can_operate=True,reason='Owner SNS alone does not reveal the BLC CASE')))
 assert expect(200,http('GET',listing,None,actor,password))==[]
 expect(200,http('PUT',grant,dict(operation_id=actor+'.BLC',expected_version=0,username=actor,owner_id='BLC',can_view=True,can_operate=False,reason='Read-only current BLC stock permission')))
 rows=expect(200,http('GET',listing,None,actor,password));assert any(r['case_pick_task_id']==1155 for r in rows),rows
 card=expect(200,http('GET',detail,None,actor,password));assert card['case_pick_task_id']==1155
 expect(403,http('POST',detail+'/move-carrier',dict(operation_id=actor+'.denied',scan_container='CP595000000001155',scanned_to_cell='CPT_'+str(w),expected_content_version=2),actor,password))
 expect(200,http('PUT',grant,dict(operation_id=actor+'.revoke',expected_version=1,username=actor,owner_id='BLC',can_view=False,can_operate=False,reason='Revoke current BLC read permission')))
 assert expect(200,http('GET',listing,None,actor,password))==[];expect(404,http('GET',detail,None,actor,password))
 expect(403,http('GET','/api/case-pick/tasks?scope=all&ware_id=211559882',None,actor,password))
 report=dict(status='PASS',warehouse_id=w,case_id=1155,goods_writes=0,actor=actor,checks=['missing_owner_hidden','other_owner_hidden','view_only_visible','view_only_move_denied','revoke_hidden','foreign_warehouse_denied'])
except Exception as e:report=dict(status='FAIL',error=str(e));raise
finally:
 with oracle_connection()as c:
  q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:u and USER_GROUP='TC03QA'",u=actor);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:r',r=actor);c.commit()
 report['http']=CALLS;p=ROOT/'runtime/test-evidence/tradecase/2026-10-19/T06'/('case-owner-'+actor+'.json');p.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8');print(json.dumps(dict(status=report['status'],file=str(p),http_calls=len(CALLS))))
