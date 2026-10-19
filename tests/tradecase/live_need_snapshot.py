"""Native journal and read-only recipient demand: source, versions, dedup, age and scope."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
from uuid import uuid4
import sys,os,json,secrets
sys.path[:0]=['.','tests/tradecase']
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
P=Path('runtime/test-evidence/tradecase/2026-10-19/T09/need-fixture.json')
assert not P.exists(),'Factory fixture already exists; do not overwrite or rerun'
w=224274301;tag='T9'+uuid4().hex[:9];now=datetime.now(timezone.utc);checks=[];requests=[];s={'warehouse_id':w,'tag':tag};actor=None

def send(kind,id,payload,version=1,status=200,source='TC03.SAP',event=None):
    body=dict(schema_version=1,event_id=event or tag+'.'+id+'.'+str(version),source_id=source,warehouse_id=w,document_id=id,version=version,occurred_at=now.isoformat(),payload=dict(entity_type=kind,**payload));requests.append(body);return expect(status,http('POST','/api/tradecase/messages',body))
def supply(id,**changes):
    row=dict(supply_id=id,version=1,quantity='50',uom='BOX',status='PLANNED',confirmed=True,current_trip=True,expected_at=(now+timedelta(hours=1)).isoformat());row.update(changes);return row

def preview(id,status=200,**kwargs):return expect(status,http('GET',f'/api/tradecase/warehouses/{w}/needs/{id}?max_age_minutes=60',**kwargs))
try:
    with oracle_connection()as c:
        q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
        q.execute("select count(*)from user_objects where STATUS='INVALID'and OBJECT_NAME not like'BIN$%'");assert q.fetchone()[0]==0
        q.execute("select EXTERNAL_ID,VERSION_NO from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE='SKU'",w=w);versions=dict(q.fetchall())
    for r in ['C2','C3']:
        send('RECIPIENT',tag+'.'+r,dict(title='QA recipient '+r,target_owner_id='BLC',permitted_source_owners=['SNS'],buyout_mode='BEFORE_PICK',min_osg_days=0,lead_time_days=0))
    def need(recipient,sku,forecast='100',available='30',supplies=None,**changes):
        value=dict(recipient_id=tag+'.'+recipient,sku_id=sku,recipient_version=1,sku_version=versions[sku],snapshot_at=now.isoformat(),period_from=now.isoformat(),period_until=(now+timedelta(days=1)).isoformat(),uom='BOX',forecast_quantity=forecast,target_quantity='20',available_quantity=available,received_in_available=True,supplies=supplies or []);value.update(changes);return value
    a=need('C2','A',supplies=[supply('S2')]);b=need('C3','B',forecast='80',supplies=[supply('S3',quantity='40')]);aid=tag+'.C2A';bid=tag+'.C3B';s.update(a_id=aid,b_id=bid)
    accepted=send('NEED',aid,a);original=requests[-1];duplicate=expect(200,http('POST','/api/tradecase/messages',original));assert duplicate['replayed'] and duplicate['outbox_id']==accepted['outbox_id'];checks+=['unchanged_event_one_outbox']
    ar=preview(aid);br=send('NEED',bid,b);br=preview(bid);assert ar['additional_boxes']=='40'and br['additional_boxes']=='30';checks+=['C2A40_C3B30']
    # Nothing omitted by this next delta is erased.
    a2=dict(a,supplies=[supply('S2'),supply('S2',version=2,status='IN_TRANSIT')]);send('NEED',aid,a2,2);ar2=preview(aid);assert ar2['additional_boxes']=='40'and len(ar2['supplies'])==1 and ar2['current_trip_quantity']=='500';assert preview(bid)['additional_boxes']=='30';checks+=['same_supply_planned_to_transit_once','omitted_other_snapshot_preserved']
    a3=dict(a,available_quantity='80',supplies=[supply('S2',version=3,status='RECEIVED')]);send('NEED',aid,a3,3);assert preview(aid)['additional_boxes']=='40';checks+=['received_only_in_available']
    send('NEED',aid,dict(a3,forecast_quantity='0'),4);assert preview(aid)['additional_boxes']=='0';checks+=['zero_forecast_clears_value_and_zero_floor']
    send('NEED',aid,a2,5);s['a_current']=preview(aid);s['b_current']=preview(bid)
    send('NEED',tag+'.STALE',dict(a,snapshot_at=(now-timedelta(minutes=61)).isoformat()));assert preview(tag+'.STALE')['expired'];checks+=['age61_exceeds_explicit60']
    result=send('NEED',tag+'.UNKNOWN',dict(a,recipient_id='NOT_KNOWN'),status=409);assert result['detail']['code'].startswith('MASTER_MISSING');checks+=['unknown_recipient_rejected']
    send('NEED',tag+'.WRONG_UOM',dict(a,uom='KG'),status=422);send('NEED',tag+'.WRONG_SOURCE',a,status=409,source='OTHER');send('NEED',aid,dict(a,sku_id='B',sku_version=versions['B']),6,status=409);checks+=['unit_source_identity_rejected']
    actor=tag+'R';password=secrets.token_hex(24)
    with oracle_connection()as c:
        q=c.cursor();q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'QA demand reader','TC03QA',:w,0,1)",a=actor,p=password,w=w)
        q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'QA demand reader',1,1)",a=actor);q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'tradecase_view')",a=actor)
        q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Recipient demand read only QA',1)",a=actor,w=str(w));c.commit()
    assert preview(aid,actor=actor,password=password)['additional_boxes']=='40';expect(403,http('POST','/api/tradecase/messages',original,actor,password));expect(403,http('GET',f'/api/tradecase/warehouses/211559882/needs/{aid}?max_age_minutes=60',None,actor,password));checks+=['warehouse_read_only','import_and_foreign_denied']
    with oracle_connection()as c:
        q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp,VERSION_NO=VERSION_NO+1 where ASSIGNMENT_ID=:a',a=actor);c.commit()
    preview(aid,403,actor=actor,password=password);checks+=['revocation_denies_read']
    s.update(status='PASS',checks=checks,limits='External snapshot calculation only; no sender stock, automatic route, proposal, approval, SAP order or physical shipment accepted')
    print(json.dumps(dict(status=s['status'],checks=checks,a_id=aid,b_id=bid)))
except Exception as e:s.update(status='FAIL',error=str(e),checks=checks);raise
finally:
    if actor:
        with oracle_connection()as c:
            q=c.cursor();q.execute('update RUSERS set DELETED=1 where ID=:a',a=actor);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=nvl(REVOKED_AT,systimestamp),VERSION_NO=VERSION_NO+1 where ASSIGNMENT_ID=:a',a=actor);c.commit();s['actor_retired']=True
    s.update(http=CALLS,requests=requests);P.write_text(json.dumps(s,indent=2,default=str))
