"""Real ASGI/Oracle SAP correlation, synthetic external order, no new physical receipt."""
from datetime import datetime,timedelta,timezone
import json,os,secrets,sys
from pathlib import Path
from time import perf_counter
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from fastapi.testclient import TestClient
from app.main import app
from tools.mcp.tms_mcp_server import oracle_connection
W=210564699;PREFIX='SAP22.'+uuid4().hex[:12];BASE=f'/api/tradecase/warehouses/{W}';TRIP=BASE+'/trips/T1'
report=dict(status='FAIL',checks=[],calls=[],external='SYNTHETIC; no actual SAP delivery',physical_receipts=0)
actor='TSA22'+uuid4().hex[:9];password=secrets.token_hex(24);qa=(actor,password)
client=TestClient(app);pid=None;order=None;owner_version=0


def call(method,path,body=None,auth=('admin','admin123'),status=200):
    began=perf_counter();r=client.request(method,path,json=body,auth=auth)
    value=r.json();report['calls'].append(dict(method=method,path=path,status=r.status_code,ms=round((perf_counter()-began)*1000,2),result=value))
    assert r.status_code==status,(r.status_code,value)
    return value


def owner(view,operate):
    global owner_version
    call('PUT',BASE+'/stock/owner-grants',dict(operation_id=PREFIX+'.owner.'+str(owner_version),expected_version=owner_version,username=actor,owner_id='SNS',can_view=view,can_operate=operate,reason='Owned synthetic SAP top-up correlation'))
    owner_version+=1


def document(identifier,payload,version):
    return call('POST','/api/tradecase/messages',dict(schema_version=1,event_id=PREFIX+'.order.'+str(version),source_id='TC03.SAP',warehouse_id=W,document_id=identifier,version=version,occurred_at=datetime.now(timezone.utc).isoformat(),payload=payload))


try:
    with oracle_connection() as c:
        q=c.cursor();q.execute('select NAME from RRL_WARES where ID=:w',w=W);assert q.fetchone()==('TRADECASE QA 089ddb36',)
        q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Synthetic SAP reply QA','TC03QA',:w,0,1)",a=actor,p=password,w=W)
        q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Synthetic SAP reply QA',1,1)",a=actor)
        for permission in ('tradecase_view','tradecase_topup_result'):
            q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)',a=actor,p=permission)
        q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Owned synthetic SAP reply',1)",a=actor,w=str(W));c.commit()
    saved=call('POST',TRIP+'/topup-proposals',dict(operation_id=PREFIX+'.save',need_ids=['N1'],max_age_minutes=1440));p=saved['proposals'][0];pid=p['proposal_id'];report['proposal_id']=pid
    confirmed=call('POST',TRIP+f'/topup-proposals/{pid}/confirm',dict(operation_id=PREFIX+'.confirm',expected_version=p['version']))
    assert confirmed['status']=='CONFIRMED'
    endpoint=TRIP+f'/topup-proposals/{pid}/sap-reply'
    body=dict(operation_id=PREFIX+'.answer',source_id='TC03.SAP',event_id=(PREFIX+'.'+('X'*100))[:100],expected_version=confirmed['version'],outcome='ACCEPTED',sap_order_id=PREFIX+'.SAP.ORDER')
    report['answer_request']=body
    owner(True,False);call('POST',endpoint,body,qa,403)
    owner(True,True)
    call('POST',endpoint,dict(body,expected_version=99,event_id=PREFIX+'.STALE',operation_id=PREFIX+'.STALE'),qa,409)
    call('POST',endpoint,dict(body,source_id='WRONG',event_id=PREFIX+'.WRONG',operation_id=PREFIX+'.WRONG'),qa,409)
    accepted=call('POST',endpoint,body,qa);assert accepted['status']=='SAP_ACCEPTED' and accepted['sap_order_received'] is False and accepted['picking_allowed'] is False
    repeated=call('POST',endpoint,body,qa);assert repeated['replayed'] and repeated['proposal_id']==pid
    changed=call('POST',endpoint,dict(body,sap_order_id=PREFIX+'.OTHER'),qa,409);assert changed['detail']['outcome_confirmed'] is False
    report['checks'].append('Version/source/owner-write enforced; 100-character event accepted and exact replay retained')
    with oracle_connection() as c:
        q=c.cursor();q.execute("delete from RRL_ACCESS_ROLE_RIGHT where ROLE_ID=:a and PERMISSION='tradecase_topup_result'",a=actor);c.commit()
    call('POST',endpoint,body,qa,403)
    with oracle_connection() as c:
        q=c.cursor();q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'tradecase_topup_result')",a=actor);c.commit()
    owner(False,False);call('POST',endpoint,body,qa,403)
    report['checks'].append('Current SAP permission and owner-write apply to accepted cached event')
    order=body['sap_order_id'];payload=dict(entity_type='ORDER',order_kind='TOPUP',parent_trip_id='T1',recipient_id='C1',planned_ship_at=(datetime.now(timezone.utc)+timedelta(hours=3)).isoformat(),lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='SNS',mrc='200',quantity=str(accepted['approved_boxes']),uom='BOX',min_osg_days=0)])
    assert document(order,payload,1)['status']=='ACCEPTED'
    listed=call('GET',TRIP+'/topup-proposals');card=next(x for x in listed['items']if x['proposal_id']==pid)
    assert card['sap_order_received'] is True and card['picking_allowed'] is False and listed['approval_available'] is False
    with oracle_connection() as c:
        q=c.cursor();q.execute('select count(*)from RRL_PICK_WAVE where WARE_ID=:w',w=W);assert q.fetchone()==(0,)
    report['checks'].append('Ordinary external TOPUP order correlated; no invented native order, wave or picking admission')
    released=call('POST',TRIP+f'/topup-proposals/{pid}/release',dict(operation_id=PREFIX+'.release',expected_version=card['version']));assert released['status']=='CANCELLED'
    assert document(order,dict(payload,cancelled=True),2)['status']=='ACCEPTED'
    with oracle_connection() as c:
        q=c.cursor();q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=W);assert q.fetchone()==(250,0)
        q.execute("select RRL_TRADE_TOPUP_READ.protected_units(:w,'A','SNS',200)from dual",w=W);assert q.fetchone()==(20,)
    report['checks'].append('Own SAP-accepted hold released and synthetic external order cancelled; 250EA/HARD0 restored')
    report['status']='PASS'
finally:
    if pid:
        with oracle_connection() as c:
            q=c.cursor();q.execute("select STATUS,VERSION_NO from RRL_TRADE_TOPUP_PROPOSAL where PROPOSAL_ID=:p",p=pid);row=q.fetchone()
        if row and row[0]in('CONFIRMED','SAP_ACCEPTED'):
            report['cleanup_release']=call('POST',TRIP+f'/topup-proposals/{pid}/release',dict(operation_id=PREFIX+'.cleanup',expected_version=row[1]))
    if owner_version:
        owner(False,False)
    with oracle_connection() as c:
        q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=actor);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=actor);c.commit()
    report['qa_retired']=True
    out=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T08'/('topup-sap-'+PREFIX+'.json');out.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
print(json.dumps(dict(status=report['status'],checks=len(report['checks']),proposal=pid,evidence=str(out))))