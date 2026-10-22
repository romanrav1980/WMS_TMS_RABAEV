"""Owned native top-up holds and replay proof; real HTTP/Oracle, synthetic external messages."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
from uuid import uuid4
import secrets
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests/tradecase'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
os.environ.setdefault('TRADECASE_ADMIN_USER','admin')
os.environ.setdefault('TRADECASE_ADMIN_PASSWORD','admin123')
import live_stock_acceptance as stock
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T08'


def run(f,r):
    w=f['warehouse_id'];tag=f.get('run_tag','TP22.'+f['tag']);base=f'/api/tradecase/warehouses/{w}';trip=base+'/trips/T1';qa=(f['actor'],f['password'])
    now=datetime.now(timezone.utc);depart=now+timedelta(hours=6)
    def send(kind,key,payload):
        return expect(200,http('POST','/api/tradecase/messages',dict(schema_version=1,event_id=tag+'.'+kind+'.'+key,source_id='TC03.SAP',warehouse_id=w,document_id=key,version=1,occurred_at=now.isoformat(),payload=dict(entity_type=kind,**payload))))
    def query(sql,**binds):
        with oracle_connection() as c:
            q=c.cursor();q.execute(sql,binds);return q.fetchall()
    def grant(version,operate):
        if f.get('resume'): version=f['owner_version']
        expect(200,http('PUT',base+'/stock/owner-grants',dict(operation_id=tag+'.owner.'+str(version),expected_version=version,username=f['actor'],owner_id='SNS',can_view=operate,can_operate=operate,reason='Owned top-up replay scope verification')))
        f['owner_version']=version+1
    if not f.get('resume'):
        r['receipt']=stock.run(f)
        r['fixture'].update({k:v for k,v in f.items()if k!='password'})
        with oracle_connection() as c:
            q=c.cursor();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
            try:
                q.execute('update RRL_ARTICULS set COUNT_SHT_IN_KOR=10,BRUTTO_WEIGHT_OF_KOR=10,DIMKOR_X=0.4,DIMKOR_Y=0.5,DIMKOR_Z=0.5 where ACTICUL=:a',a=f['article']);assert q.rowcount==1;c.commit()
            finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
            for permission in ['tradecase_topup_approve','tradecase_topup_result']:
                q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION) values(:r,:p)',r=f['role'],p=permission)
            q.execute('select PHYSICAL_UNIT_KEY,VERSION_NO from RRL_TRADE_STOCK_ATTR where CAPTURE_WARE_ID=:w',w=w)
            items=[dict(physical_unit_key=k,expected_attribute_version=v,verdict='VALID')for k,v in q]
            c.commit()
        expect(200,http('POST',base+'/stock/mark-confirmations',dict(operation_id=tag+'.valid',skm_id='TC03.SKM',external_event_id=tag+'.valid',expected_site_version=1,occurred_at=now.isoformat(),items=items)))
        grant(3,True)
        for n in (1,2):
            send('RECIPIENT','C'+str(n),dict(title='Top-up recipient '+str(n),target_owner_id='SNS',permitted_source_owners=['SNS'],buyout_mode='IN_TRANSIT',min_osg_days=0,lead_time_days=0))
            send('ORDER','O'+str(n),dict(recipient_id='C'+str(n),planned_ship_at=depart.isoformat(),lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='SNS',mrc='200',quantity='1',uom='BOX',min_osg_days=0)]))
        vehicle=expect(201,http('POST','/api/admin/transport/vehicles',dict(num_plat=tag,transtype_id='10',max_weight_kg=8000,max_pallets=33,sobstvennyy=True)))['id']
        profile=expect(200,http('GET',f'/api/admin/transport/vehicles/{vehicle}/profile'))
        expect(200,http('POST','/api/admin/transport/vehicle-profiles',dict(operation_id=tag+'.profile',vehicle_id=vehicle,expected_source_hash=profile['base_hash'],expected_version=profile['version'],vehicle_size_class='QA_TOPUP',cargo_length_mm=13200,cargo_width_mm=2500,cargo_height_mm=2000,outer_height_mm=3000,outer_length_mm=14000,floor_variants=[dict(code='QA33',limits=[dict(pallet_type_id=1,max_places=33)])],reason='Synthetic capacity fixture',evidence_reference='TEST_NOT_HARDWARE')))
        send('TRIP','T1',dict(vehicle_id=tag,planning_source='SAP',planned_departure_at=depart.isoformat(),capacity_kg='8000',capacity_m3='0.6',orders=[dict(order_id='O'+str(n),line_id='1',quantity='1')for n in(1,2)]))
        for n in (1,2):
            send('NEED','N'+str(n),dict(recipient_id='C'+str(n),sku_id='A',recipient_version=1,sku_version=1,snapshot_at=now.isoformat(),period_from=now.isoformat(),period_until=(now+timedelta(days=1)).isoformat(),uom='BOX',forecast_quantity='5',target_quantity='0',available_quantity='0',received_in_available=True,supplies=[dict(supply_id='MAIN'+str(n),version=1,quantity='1',uom='BOX',status='PLANNED',confirmed=True,current_trip=True,expected_at=depart.isoformat())]))
    else:
        grant(0,True)
    preview=expect(200,http('POST',trip+'/topup-preview',dict(need_ids=['N1'],max_age_minutes=1440),*qa))
    assert preview['items'][0]['proposed_boxes']==4,preview
    r['checks'].append('Capacity holds four boxes; unadmitted main orders protect twenty EA')
    assert query('select RRL_TRADE_TOPUP_READ.protected_units(:w,\'A\',\'SNS\',200) from dual',w=w)==[(20,)]
    bodies=[dict(operation_id=tag+'.save.'+str(n),need_ids=['N'+str(n)],max_age_minutes=1440)for n in (1,2)]
    saved=[expect(200,http('POST',trip+'/topup-proposals',b,*qa))for b in bodies]
    ids=[s['proposals'][0]['proposal_id']for s in saved];r['proposal_ids']=ids
    assert all(s['proposals'][0]['approved_boxes']==4 for s in saved),saved
    confirms=[dict(operation_id=tag+'.confirm.'+str(n),expected_version=1)for n in(1,2)]
    with ThreadPoolExecutor(max_workers=2) as pool:
        replies=list(pool.map(lambda pair:http('POST',trip+f'/topup-proposals/{pair[0]}/confirm',pair[1],*qa),zip(ids,confirms)))
    assert sorted(x[0]for x in replies)==[200,409],replies
    winner=next(i for i,x in enumerate(replies)if x[0]==200);pid=ids[winner]
    r['confirmed_proposal']=pid;r['confirm_body']=confirms[winner]
    assert query('select sum(REMAIN),sum(HARD_RESERVED_BASE) from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=w)==[(250,40)]
    r['checks'].append('Concurrent four-plus-four cannot exceed four free places; forty EA reserved once')
    repeated=expect(200,http('POST',trip+f'/topup-proposals/{pid}/confirm',confirms[winner],*qa))
    assert repeated['proposal_id']==pid
    replay=expect(200,http('POST',trip+'/topup-proposals',bodies[winner],*qa))
    assert replay['replayed'] and replay['proposals']==saved[winner]['proposals'],replay
    expect(409,http('POST',trip+'/topup-proposals',dict(bodies[winner],max_age_minutes=61),*qa))
    r['checks'].append('Saved request replays after capacity changed; changed original request conflicts')
    grant(4,False)
    expect(403,http('POST',trip+f'/topup-proposals/{pid}/confirm',confirms[winner],*qa))
    expect(403,http('POST',trip+'/topup-proposals',bodies[winner],*qa))
    grant(5,True)
    with oracle_connection() as c:
        q=c.cursor();q.execute("delete from RRL_ACCESS_ROLE_RIGHT where ROLE_ID=:r and PERMISSION='tradecase_topup_approve'",r=f['role']);c.commit()
    expect(403,http('POST',trip+f'/topup-proposals/{pid}/confirm',confirms[winner],*qa))
    r['checks'].append('Current owner and command rights apply to cached confirmations and saves')
    release=expect(200,http('POST',trip+f'/topup-proposals/{pid}/release',dict(operation_id=tag+'.release',expected_version=repeated['version'])))
    assert release['status']=='CANCELLED'
    assert query('select sum(REMAIN),sum(HARD_RESERVED_BASE) from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=w)==[(250,0)]
    r['checks'].append('Only own hold released; stock restored to 250 EA and HARD zero')
    r['status']='PASS'


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True);f=None;r=dict(status='FAIL',checks=[])
    try:
        if len(sys.argv)>1:
            previous=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'));f=dict(previous['fixture'])
            actor='TPR22'+uuid4().hex[:9];password=secrets.token_hex(24)
            with oracle_connection() as c:
                q=c.cursor();q.execute('select NAME from RRL_WARES where ID=:w',w=f['warehouse_id']);assert q.fetchone()==('TRADECASE QA '+f['tag'],)
                q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Top-up scoped retry','TC03QA',:w,0,1)",a=actor,p=password,w=f['warehouse_id'])
                q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Top-up scoped retry',1,1)",a=actor)
                for permission in ('tradecase_view','tradecase_topup_approve','tradecase_topup_result'):
                    q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)',a=actor,p=permission)
                q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Owned top-up resume',1)",a=actor,w=str(f['warehouse_id']));c.commit()
                q.execute('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG');f['slow_marker']=q.fetchone()[0]
            f.update(actor=actor,role=actor,password=password,resume=True,owner_version=0,run_tag='TP22.RESUME.'+uuid4().hex[:10])
            r['resumed_from']=str(Path(sys.argv[1]))
        else:
            f=stock.setup()
        r['fixture']={k:v for k,v in f.items()if k!='password'}
        run(f,r)
    except Exception as exc:r.update(error_type=type(exc).__name__,error=str(exc));raise
    finally:
        if f:
            w=f['warehouse_id'];base=f'/api/tradecase/warehouses/{w}/trips/T1'
            with oracle_connection() as c:
                q=c.cursor();q.execute("select PROPOSAL_ID,VERSION_NO from RRL_TRADE_TOPUP_PROPOSAL where WARE_ID=:w and STATUS in('CONFIRMED','SAP_ACCEPTED')",w=w);active=q.fetchall()
            for pid,version in active:
                r.setdefault('cleanup',[]).append(http('POST',base+f'/topup-proposals/{pid}/release',dict(operation_id='TP22.CLEANUP.'+str(pid),expected_version=version)))
            with oracle_connection() as c:
                q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=f['actor']);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp) where ASSIGNMENT_ID=:r',r=f['role']);c.commit()
                q.execute('select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:n order by LOG_ID fetch first 40 rows only',n=f['slow_marker']);r['slow_sql']=[list(row)for row in q]
            r['qa_retired']=True
        r['http']=CALLS;target=OUT/('topup-live-'+str(f['warehouse_id']if f else uuid4().hex)+('-'+f['run_tag']if f and f.get('resume')else'')+'.json');target.write_text(json.dumps(r,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status=r['status'],checks=len(r['checks']),evidence=str(target))))