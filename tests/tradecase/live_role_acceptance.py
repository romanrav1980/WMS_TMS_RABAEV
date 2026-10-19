"""Fresh role-only actor; no retired actor is reactivated."""
import sys,json,secrets
from pathlib import Path
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-19/T04';WARE=215590763
actor='T4R'+uuid4().hex[:10];password=secrets.token_hex(24);report={};created=False
try:
    with oracle_connection()as c:
        q=c.cursor();q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:u,:p,'TRADECASE QA read role','TC04QA',:w,0,1)",u=actor,p=password,w=WARE)
        q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:r,'TRADECASE QA read role',1,1)",r=actor)
        for permission in ['tradecase_view','pick_wave_view']:q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:r,:p)',r=actor,p=permission)
        q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:r,:r,:r,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '12'hour,'admin','TRADECASE read acceptance',1)",r=actor,w=str(WARE));c.commit();created=True
    def get(path):return http('GET',path,actor=actor,password=password)
    work=expect(200,get('/api/access/workspaces?capability=tradecase'));assert [x['warehouse_id']for x in work['warehouses']]==[WARE],work
    expect(403,get('/api/tradecase/warehouses/225837931/stock/pallets'))
    assert not expect(200,get(f'/api/tradecase/warehouses/{WARE}/stock/pallets'))['items']
    expect(403,get('/api/picking/waves/595/pick-readiness'))
    grant=dict(operation_id='T4.role.grant.'+actor,expected_version=0,username=actor,owner_id='SNS',can_view=True,can_operate=False,reason='Read-only legal-owner acceptance')
    expect(200,http('PUT',f'/api/tradecase/warehouses/{WARE}/stock/owner-grants',grant))
    stock=expect(200,get(f'/api/tradecase/warehouses/{WARE}/stock/pallets'));assert stock['items'][0]['base_quantity']=='250'
    assert expect(200,get('/api/picking/waves/595/pick-readiness'))['ready']is True
    expect(403,http('POST','/api/picking/waves/595/release-picking',dict(operation_id='T4.role.release.'+actor),actor,password))
    grant.update(operation_id='T4.role.revoke.'+actor,expected_version=1,can_view=False)
    expect(200,http('PUT',f'/api/tradecase/warehouses/{WARE}/stock/owner-grants',grant))
    assert not expect(200,get(f'/api/tradecase/warehouses/{WARE}/stock/pallets'))['items'];expect(403,get('/api/picking/waves/595/pick-readiness'))
    with oracle_connection()as c:
        q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:r',r=actor);c.commit()
    assert not expect(200,get('/api/access/workspaces?capability=tradecase'))['warehouses']
    report=dict(status='PASS',role_only=True,view_without_execution=True,foreign_denied=True,revoked_visibility_removed=True)
except Exception as e:report=dict(status='FAIL',error=str(e));raise
finally:
    if created:
        with oracle_connection()as c:
            q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:u and USER_GROUP='TC04QA'",u=actor);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:r',r=actor);c.commit()
    report.update(actor=actor,retired=created,http=CALLS);p=OUT/('role-'+actor+'.json');p.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(dict(status=report['status'],file=str(p),http_calls=len(CALLS))))
