"""Complete scoped reading proof without rerunning or replacing recipient snapshot history."""
from pathlib import Path
from uuid import uuid4
import sys,os,json,secrets
sys.path[:0]=['.','tests/tradecase']
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
P=Path('runtime/test-evidence/tradecase/2026-10-19/T09/need-fixture.json');s=json.loads(P.read_text());w=s['warehouse_id'];actor='T9R'+uuid4().hex[:9];password=secrets.token_hex(24)
try:
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'QA demand reader','TC03QA',:w,0,1)",a=actor,p=password,w=w)
  q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'QA demand reader',1,1)",a=actor);q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'tradecase_view')",a=actor)
  q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Recipient demand read only QA',1)",a=actor,w=str(w));c.commit()
 path=f"/api/tradecase/warehouses/{w}/needs/{s['a_id']}?max_age_minutes=60"
 assert expect(200,http('GET',path,None,actor,password))['additional_boxes']=='40'
 expect(403,http('POST','/api/tradecase/messages',s['requests'][2],actor,password));expect(403,http('GET',f"/api/tradecase/warehouses/211559882/needs/{s['a_id']}?max_age_minutes=60",None,actor,password))
 with oracle_connection()as c:
  q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp,VERSION_NO=VERSION_NO+1 where ASSIGNMENT_ID=:a',a=actor);c.commit()
 expect(403,http('GET',path,None,actor,password));s['checks']+=['warehouse_read_only','import_and_foreign_denied','revocation_denies_read'];s['initial_scope_harness_error']=s.pop('error',None);s['status']='PASS';s['limits']='External recipient snapshot calculation only; no sender stock, automatic route, proposal, approval, SAP order or physical shipment accepted'
 print(json.dumps(dict(status=s['status'],checks=s['checks'])))
finally:
 with oracle_connection()as c:
  q=c.cursor();q.execute('update RUSERS set DELETED=1 where ID=:a',a=actor);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=nvl(REVOKED_AT,systimestamp),VERSION_NO=VERSION_NO+1 where ASSIGNMENT_ID=:a',a=actor);c.commit()
 s['http']+=CALLS;s['scope_actor_retired']=actor;P.write_text(json.dumps(s,indent=2,default=str))
