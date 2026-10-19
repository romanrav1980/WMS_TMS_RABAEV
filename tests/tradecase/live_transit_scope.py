"""Role-only exact cargo visibility, scope marker, owner revoke and financial write denial."""
from pathlib import Path
from uuid import uuid4
import json,os,secrets,sys
sys.path[:0]=['.','tests/tradecase']
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
actor='T7V'+uuid4().hex[:9];password=secrets.token_hex(24);w=215590763;report={}
base=f'/api/tradecase/warehouses/{w}';path=base+'/stock/transit?load_operation_id=T7.LOAD.1156&limit=100'
try:
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'TRADECASE cargo reader','TC03QA',:w,0,1)",a=actor,p=password,w=w)
  q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'TRADECASE cargo reader',1,1)",a=actor)
  for permission in ['tradecase_view','tradecase_buyout_request']:q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)',a=actor,p=permission)
  q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Exact cargo scope acceptance',1)",a=actor,w=str(w));c.commit()
 hidden=expect(200,http('GET',path,actor=actor,password=password));assert hidden['items']==[]and hidden['owner_scope_filtered']
 grant=lambda owner,version,view,operate,tag:expect(200,http('PUT',base+'/stock/owner-grants',dict(operation_id=actor+'.'+tag,expected_version=version,username=actor,owner_id=owner,can_view=view,can_operate=operate,reason='Owned scope acceptance only')))
 grant('BLC',0,True,False,'BLC')
 shown=expect(200,http('GET',path,actor=actor,password=password));assert len(shown['items'])==40 and not shown['owner_scope_filtered'];assert all(x['owner_id']=='BLC'and x['cell']is None for x in shown['items'])
 body=dict(operation_id=actor+'.write',buyout_id=actor+'.write',basis_order_id='TC7.FIN.TRANSIT',basis_line_id='1',expected_basis_version=1,unit_keys=[x['physical_unit_key']for x in shown['items']],demand_order_id='TRANSIT',demand_line_id='1',load_operation_id='T7.LOAD.1156')
 expect(403,http('POST',base+'/buyouts',body,actor,password))
 grant('BLC',1,False,False,'revoke');hidden2=expect(200,http('GET',path,actor=actor,password=password));assert hidden2['items']==[]and hidden2['owner_scope_filtered']
 expect(403,http('GET','/api/tradecase/warehouses/211559882/stock/transit?load_operation_id=T7.LOAD.1156',actor=actor,password=password))
 admin=expect(200,http('GET',path));assert len(admin['items'])==40 and not admin['owner_scope_filtered']
 with oracle_connection()as c:
  q=c.cursor();q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=w);assert list(q.fetchone())==[110,0]
 report=dict(status='PASS',warehouse_id=w,physical_writes=0,actor=actor,checks=['hidden_set_marked','BLC_view40_complete','view_only_buyout_denied','revoke_hides','foreign_warehouse_denied','admin40_complete'])
except Exception as e:report=dict(status='FAIL',error=str(e));raise
finally:
 with oracle_connection()as c:
  q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=actor);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=actor);c.commit()
 report['http']=CALLS;P=Path('runtime/test-evidence/tradecase/2026-10-19/T07/transit-scope-'+actor+'.json');P.write_text(json.dumps(report,indent=2,default=str));print(json.dumps(dict(status=report['status'],http_calls=len(CALLS),file=str(P))))
