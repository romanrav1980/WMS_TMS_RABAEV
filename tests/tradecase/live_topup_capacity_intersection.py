"""Real capacity intersection after SAP includes an approved top-up in its trip."""
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import sys
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests/tradecase'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
os.environ.setdefault('TRADECASE_ADMIN_USER','admin')
os.environ.setdefault('TRADECASE_ADMIN_PASSWORD','admin123')
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection

FILE=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T08/topup-capacity-intersection.json'
s=json.loads(FILE.read_text(encoding='utf-8')) if FILE.exists() else dict(tag='TCI22.'+uuid4().hex[:9],requests={},results={},checks=[],history=[])
W=215266197;BASE=f'/api/tradecase/warehouses/{W}';TRIP=BASE+'/trips/T1';TAG=s['tag']


def save():FILE.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')


def query(sql,**args):
    with oracle_connection() as conn:
        q=conn.cursor();q.execute(sql,args)
        return [tuple(v.read()if hasattr(v,'read')else v for v in r)for r in q.fetchall()]


def doc(kind,key):
    body,version=query("select BODY_JSON,VERSION_NO from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE=:k and EXTERNAL_ID=:e and STATUS='ACCEPTED'",w=W,k=kind,e=key)[0]
    return body if isinstance(body,dict)else json.loads(body),version


def step(key,path,body):
    if key not in s['requests']:s['requests'][key]=dict(path=path,body=body);save()
    if key not in s['results']:
        request=s['requests'][key]
        s['results'][key]=expect(200,http('POST',request['path'],request['body']));save()
    return s['results'][key]


def send(key,kind,identifier,body,version):
    return step(key,'/api/tradecase/messages',dict(schema_version=1,event_id=TAG+'.'+key,source_id='TC03.SAP',warehouse_id=W,
        document_id=identifier,version=version,occurred_at=datetime.now(timezone.utc).isoformat(),payload=dict(body,entity_type=kind)))


def run():
    if s.get('status')=='PASS':return
    if 'trip_before'not in s:
        assert query('select NAME from RRL_WARES where ID=:w',w=W)==[('TRADECASE QA 505b15a0',)]
        assert query('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=W)==[(1000,0)]
        s['trip_before'],s['trip_version']=doc('TRIP','T1')
        s['need_before'],s['need_version']=doc('NEED','N1')
        s['slow_marker']=query('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG')[0][0]
        save()
    saved=step('saved',TRIP+'/topup-proposals',dict(operation_id=TAG+'.save',need_ids=['N1'],max_age_minutes=1440))
    p=saved['proposals'][0];assert p['approved_boxes']==40,p
    pid=p['proposal_id'];s['proposal_id']=pid;save()
    confirmed=step('confirmed',TRIP+f'/topup-proposals/{pid}/confirm',dict(operation_id=TAG+'.confirm',expected_version=p['version']))
    order=TAG+'.ORDER'
    accepted=step('sap',TRIP+f'/topup-proposals/{pid}/sap-reply',dict(operation_id=TAG+'.sap',source_id='TC03.SAP',event_id=TAG+'.ACK',
        expected_version=confirmed['version'],outcome='ACCEPTED',sap_order_id=order))
    send('order','ORDER',order,dict(order_kind='TOPUP',parent_trip_id='T1',recipient_id='C1',planned_ship_at=s['trip_before']['planned_departure_at'],
        lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='SNS',mrc='200',quantity='40',uom='BOX',min_osg_days=0)]),1)
    send('trip_updated','TRIP','T1',dict(s['trip_before'],orders=s['trip_before']['orders']+[dict(order_id=order,line_id='1',quantity='40')]),s['trip_version']+1)
    need=dict(s['need_before'],supplies=s['need_before']['supplies']+[dict(supply_id=order,version=1,quantity='40',uom='BOX',status='PLANNED',confirmed=True,current_trip=True,expected_at=s['trip_before']['planned_departure_at'])])
    send('need_updated','NEED','N1',need,s['need_version']+1)
    first=step('first_need_preview',TRIP+'/topup-preview',dict(need_ids=['N1'],max_age_minutes=1440))
    assert first['proposed_boxes']==0 and first['items'][0]['already_confirmed_boxes']=='0',first
    second=step('second_need_preview',TRIP+'/topup-preview',dict(need_ids=['N2'],max_age_minutes=1440))
    assert second['proposed_boxes']==20,second
    assert second['items'][0]['capacity']['planned_volume_m3']=='4.2',second
    s['checks'].append('Updated trip counts forty approved boxes once; other recipient still gets remaining twenty')
    assert query('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=W)==[(1000,400)]
    step('released',TRIP+f'/topup-proposals/{pid}/release',dict(operation_id=TAG+'.release',expected_version=accepted['version']))
    send('trip_restored','TRIP','T1',s['trip_before'],s['trip_version']+2)
    order_body,version=doc('ORDER',order)
    send('order_cancelled','ORDER',order,dict(order_body,cancelled=True),version+1)
    send('need_restored','NEED','N1',s['need_before'],s['need_version']+2)
    assert query('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=W)==[(1000,0)]
    s['checks'].append('Own hold released, source trip/need restored and synthetic top-up order cancelled; no new receipt')
    s['slow_sql']=query('select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:n order by LOG_ID fetch first 25 rows only',n=s['slow_marker'])
    s['status']='PASS';s.pop('error',None);save()


if __name__=='__main__':
    try:run()
    except Exception as exc:s.update(status='FAIL',error=str(exc));raise
    finally:s['history']+=CALLS;save()
    print(json.dumps(dict(status=s['status'],proposal=s['proposal_id'],checks=len(s['checks']),evidence=str(FILE))))
