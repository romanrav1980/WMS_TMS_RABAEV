"""Current route-point read model against Oracle under an owned temporary role."""
import json
import os
from pathlib import Path
import secrets
import sys
import time
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server'),str(ROOT/'tests/tradecase'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from fastapi.testclient import TestClient
from app.main import app
from tools.mcp.tms_mcp_server import oracle_connection

W=220793322
ACTOR='RP22'+uuid4().hex[:10]
PASSWORD=secrets.token_hex(24)
PATH=f'/api/tradecase/warehouses/{W}/trips/R1.1168/route-points'
report=dict(status='FAIL',actor=ACTOR,checks=[],http=[],mode='HTTP8088 with real Oracle' if '--http' in sys.argv else 'ASGI with real Oracle; no lifespan workers')
client=TestClient(app)


def call(method,path,body=None,actor=ACTOR,password=PASSWORD,status=200):
    start=time.perf_counter()
    if '--http' in sys.argv:
        from live_document_acceptance import http
        code,result=http(method,path,body,actor,password)
    else:
        response=client.request(method,path,json=body,auth=(actor,password))
        code,result=response.status_code,response.json()
    report['http'].append(dict(method=method,path=path,status=code,elapsed_ms=round((time.perf_counter()-start)*1000,2),response=result))
    assert code==status,(code,result)
    return result


def owner(version,view):
    return call('PUT',f'/api/tradecase/warehouses/{W}/stock/owner-grants',dict(operation_id=ACTOR+'.owner.'+str(version),expected_version=version,
        username=ACTOR,owner_id='SNS',can_view=view,can_operate=False,reason='Owned route-point visibility acceptance'),actor='admin',password='admin123')


if __name__=='__main__':
    created=False
    try:
        with oracle_connection() as conn:
            q=conn.cursor();q.execute('select NAME from RRL_WARES where ID=:w',w=W);assert q.fetchone()[0].startswith('TRADECASE QA ')
            q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Route visibility QA','TC03QA',222823304,0,1)",a=ACTOR,p=PASSWORD)
            q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Route visibility QA',1,1)",a=ACTOR)
            q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'tradecase_view')",a=ACTOR)
            q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE','220793322','CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Owned route read proof',1)",a=ACTOR)
            conn.commit();created=True
        hidden=call('GET',PATH)
        assert hidden['points']==[] and hidden['blocked_reason']=='ROUTE_POINTS_NOT_VISIBLE'
        assert all(secret not in json.dumps(hidden)for secret in ('FP21.QA.ADDRESS','N22A.220793322','MT22.220793322.RECIPIENT','641547'))
        report['checks'].append('No owner grant reveals no stop/address/shipment/recipient/count')
        owner(0,True)
        visible=call('GET',PATH)
        assert visible['points'][0]['link_status']=='LINKED' and visible['points'][0]['recipient_id']=='MT22.220793322.RECIPIENT'
        report['checks'].append('Scoped owner view reveals own recipient mapping')
        owner(1,False)
        assert call('GET',PATH)['points']==[]
        report['checks'].append('Owner revocation clears entire point list')
        owner(2,True)
        with oracle_connection() as conn:
            q=conn.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=ACTOR);conn.commit()
        call('GET',PATH,status=403)
        call('GET',PATH.replace(str(W),'220639789'),status=403)
        report['checks'].append('Warehouse revocation and foreign warehouse deny access')
        full=call('GET','/api/tradecase/warehouses/220639789/trips/R1.1221/route-points',actor='admin',password='admin123')
        assert full['points'][0]['link_status']=='LINKED',full
        report['checks'].append('Full pallet links by saved fulfillment warehouse task, not reusable pallet ID')
        with oracle_connection() as conn:
            q=conn.cursor();q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=W);assert q.fetchone()==(7,5)
        report['status']='PASS'
    finally:
        if created:
            with oracle_connection() as conn:
                q=conn.cursor();q.execute("select VERSION_NO,CAN_VIEW,CAN_OPERATE from RRL_TRADE_OWNER_GRANT where WARE_ID=:w and USERNAME=:a and OWNER_ID='SNS'",w=W,a=ACTOR);row=q.fetchone()
            if row and(row[1]or row[2]):owner(row[0],False)
            with oracle_connection() as conn:
                q=conn.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=ACTOR);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp) where ASSIGNMENT_ID=:a',a=ACTOR);conn.commit()
            report['qa_retired']=True
        out=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T09/root-C0148'/('route-scope-'+ACTOR+'.json')
        out.parent.mkdir(exist_ok=True,parents=True);out.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],checks=len(report['checks']),evidence=str(out))))
