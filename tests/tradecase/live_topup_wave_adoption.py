"""Owned HTTP/Oracle top-up-to-wave transfer proof, without new physical receipts."""
from datetime import datetime, timedelta, timezone
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

OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T08'
FILE=OUT/'topup-wave-adoption-live.json'
s=json.loads(FILE.read_text(encoding='utf-8')) if FILE.exists() else dict(tag='TA22.'+uuid4().hex[:9],warehouse_id=210564699,requests={},results={},checks=[],history=[])
W=s['warehouse_id'];TAG=s['tag'];BASE=f'/api/tradecase/warehouses/{W}';TRIP=BASE+'/trips/T1'


def save():
    OUT.mkdir(parents=True,exist_ok=True)
    FILE.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')


def query(sql,**binds):
    with oracle_connection() as conn:
        q=conn.cursor();q.execute(sql,binds)
        return [tuple(x.read() if hasattr(x,'read') else x for x in row) for row in q.fetchall()]


def doc(kind,key):
    body,version=query("select BODY_JSON,VERSION_NO from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE=:k and EXTERNAL_ID=:e and STATUS='ACCEPTED'",w=W,k=kind,e=key)[0]
    return body if isinstance(body,dict) else json.loads(body),version


def step(key,path,body=None,method='POST',status=200):
    if key not in s['requests']:
        s['requests'][key]=dict(path=path,body=body,method=method,status=status);save()
    if key not in s['results']:
        r=s['requests'][key]
        s['results'][key]=expect(r['status'],http(r['method'],r['path'],r['body']));save()
    return s['results'][key]


def send(key,kind,identifier,body,version=1):
    return step(key,'/api/tradecase/messages',dict(schema_version=1,event_id=TAG+'.'+key,source_id='TC03.SAP',warehouse_id=W,
        document_id=identifier,version=version,occurred_at=datetime.now(timezone.utc).isoformat(),payload=dict(body,entity_type=kind)))


def run():
    if s.get('status')=='TRANSFER_PASS_RECONCILIATION_OPEN':
        return
    if 'before' not in s:
        assert query('select NAME from RRL_WARES where ID=:w',w=W)==[('TRADECASE QA 089ddb36',)]
        s['before']=query('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE) from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=W)
        assert s['before']==[(250,0)],s['before']
        s['slow_marker']=query('select nvl(max(LOG_ID),0) from RRL_SQL_SLOW_LOG')[0][0]
        s['trip_before'],s['trip_version']=doc('TRIP','T1')
        s['recipient_before'],s['recipient_version']=doc('RECIPIENT','C1')
        save()
    saved=step('saved',TRIP+'/topup-proposals',dict(operation_id=TAG+'.save',need_ids=['N1'],max_age_minutes=1440))
    proposal=saved['proposals'][0];pid=proposal['proposal_id'];s['proposal_id']=pid;save()
    assert proposal['approved_boxes']==4,proposal
    confirmed=step('confirmed',TRIP+f'/topup-proposals/{pid}/confirm',dict(operation_id=TAG+'.confirm',expected_version=proposal['version']))
    assert query('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE) from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=W)==[(250,40)]
    if 'held_units' not in s:
        s['held_units']=query("select u.PHYSICAL_UNIT_KEY,u.HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_TOPUP_HOLD h on h.RESERVATION_ID=u.HARD_RESERVATION_ID where h.PROPOSAL_ID=:p order by u.PHYSICAL_UNIT_KEY",p=pid)
        assert len(s['held_units'])==40 and len({r[0]for r in s['held_units']})==40
        save()
    order=TAG+'.ORDER'
    accepted=step('sap',TRIP+f'/topup-proposals/{pid}/sap-reply',dict(operation_id=TAG+'.sap',expected_version=confirmed['version'],source_id='TC03.SAP',event_id=TAG+'.SAP',outcome='ACCEPTED',sap_order_id=order))
    customer=step('customer','/api/customers',dict(customer_code=TAG,customer_name='Owned top-up adoption proof',customer_type='LEGAL_ENTITY'))['customer_id']
    send('recipient','RECIPIENT','C1',dict(s['recipient_before'],wms_customer_id=customer),s['recipient_version']+1)
    send('order','ORDER',order,dict(order_kind='TOPUP',parent_trip_id='T1',recipient_id='C1',planned_ship_at=s['trip_before']['planned_departure_at'],
        lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='SNS',mrc='200',quantity='40',uom='EA',min_osg_days=0)]))
    if 'native_order' not in s:
        with oracle_connection() as conn:
            q=conn.cursor();q.callproc('RRL_STOCK_METADATA_TX.begin_change',['admin','warehouse_settings_edit'])
            try:
                q.execute('select RRL_CUSTOMER_ORDER_SQ.nextval,RRL_CUSTOMER_ORDER_ROW_SQ.nextval from dual');native,row=q.fetchone()
                q.execute("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID,SHIPMENT_DATE,STATUS,SOURCE_SYSTEM,CREATED_BY)values(:o,:code,:c,:w,to_date(:day,'YYYY-MM-DD'),'OPEN','QA_TRADECASE_ONLY','admin')",o=native,code=TAG,c=customer,w=W,day=s['trip_before']['planned_departure_at'][:10])
                q.execute("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,PRODUCT_NAME,UNIT_CODE,ORDER_QTY,WARE_ID,STATUS,CREATED_BY)values(:r,:o,1,'TC03089DDB36','Owned top-up adoption proof','EA',40,:w,'OPEN','admin')",r=row,o=native,w=W)
                conn.commit();s.update(native_order=native,native_row=row);save()
            finally:q.callproc('RRL_STOCK_METADATA_TX.end_change')
    step('binding',BASE+'/orders/'+order+'/binding',dict(operation_id=TAG+'.bind',expected_order_version=1,customer_order_id=s['native_order'],lines=[dict(line_id='1',customer_order_row_id=s['native_row'])]))
    # An accepted separate order alone is insufficient: the updated trip is required.
    if 'trip_updated' not in s['results']:
        assert query('select RRL_TRADE_TOPUP_ADOPT.line_proposal(:r) from dual',r=s['native_row'])==[(-1,)]
        s['checks'].append('No updated TRIP: native adoption denied')
        step('no_updated_trip','/api/picking/plans',dict(operation_id=TAG+'.missing.trip.plan',customer_order_id=s['native_order']),status=409)
    step_trip=dict(s['trip_before'],orders=s['trip_before']['orders']+[dict(order_id=order,line_id='1',quantity='40')])
    send('trip_updated','TRIP','T1',step_trip,s['trip_version']+1)
    if 'launched' not in s['results']:
        assert query('select RRL_TRADE_TOPUP_ADOPT.line_proposal(:r) from dual',r=s['native_row'])==[(pid,)]
    if 'face' not in s['results']:
        route=step('route','/api/picking/routes',dict(route_code=TAG,route_name=TAG,ware_id=W))['pick_route_id']
        cell=step('route_cell','/api/picking/route-cells',dict(pick_route_id=route,cell_code='T3P089ddb36',pick_sequence=1))['pick_route_cell_id']
        step('face','/api/picking/pick-faces',dict(ware_id=W,cell_code='T3P089ddb36',pick_face_code=TAG,pick_route_id=route,pick_route_cell_id=cell,pick_sequence=1,min_case_qty=0,max_case_qty=100,replenishment_trigger_qty=1))
    face=s['results']['face']['pick_face_id']
    step('face_article',f'/api/picking/pick-faces/{face}/articuls',dict(articul='TC03089DDB36',priority='1',min_qty='0',max_qty='100',replenishment_method='IMMEDIATE',replenishment_qty_mode='FILL_TO_VOLUME',use_articul_replenish_rule=0,boxes_per_layer='5',boxes_per_pallet='25',box_volume_m3='0.1'))
    plan=step('plan','/api/picking/plans',dict(operation_id=TAG+'.plan',customer_order_id=s['native_order']))['pick_plan_id'];s['plan']=plan;save()
    wave=step('wave','/api/picking/waves',dict(wave_code=TAG,wave_name=TAG,ware_id=W,planned_start_at=datetime.now(timezone.utc).isoformat(),planned_finish_at=(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()))['pick_wave_id'];s['wave']=wave;save()
    wave_path=f'/api/picking/waves/{wave}'
    step('added',wave_path+'/plans',dict(pick_plan_id=plan))
    step('calculated',wave_path+'/calculate',{})
    launched=step('launched',wave_path+'/launch',dict(operation_id=TAG+'.launch'))
    assert expect(200,http('POST',wave_path+'/launch',s['requests']['launched']['body']))==launched
    after=query("select u.PHYSICAL_UNIT_KEY,u.HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_TOPUP_ADOPTION a on a.RESERVATION_ID=u.HARD_RESERVATION_ID where a.PROPOSAL_ID=:p order by u.PHYSICAL_UNIT_KEY",p=pid)
    assert [list(r)for r in after]==[list(r)for r in s['held_units']],after
    assert query('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE) from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=W)==[(250,40)]
    s['checks'].append('Wave takes same forty unit keys and same HARD reservation; replay does not reserve twice')
    step('release_denied',TRIP+f'/topup-proposals/{pid}/release',dict(operation_id=TAG+'.cannot.release.adopted',expected_version=accepted['version']),status=409)
    step('wave_cancelled',wave_path+'/cancel',dict(operation_id=TAG+'.wave.cancel',reason='End owned unpicked transfer proof without moving physical goods'))
    assert query('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE) from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=W)==[(250,0)]
    s['adopted_after_cancel']=query('select h.RESERVATION_ID,h.STATUS,r.STATUS,r.BASE_QTY from RRL_TRADE_TOPUP_HOLD h join RRL_STOCK_RESERVATION r on r.RESERVATION_ID=h.RESERVATION_ID where h.PROPOSAL_ID=:p',p=pid)
    s['checks'].append('Unpicked native wave cancellation releases all forty units; physical stock stays250')
    # The dispatcher must not silently release an adopted hold. Reconciliation
    # after a native cancellation remains an explicit open product scenario.
    s['status']='TRANSFER_PASS_RECONCILIATION_OPEN';save()


def reconcile():
    assert 'wave_cancelled' in s['results']
    pid=s['proposal_id']
    for task,case_id,carrier,version in query('select t.PICK_TASK_ID,c.CASE_PICK_TASK_ID,c.SSCC,c.CONTENT_VERSION from RRL_PICK_TASK t join RRL_CASE_PICK_TASK c on c.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID where t.PICK_PLAN_ID=:p and c.STATUS<>\'CANCELLED\'',p=s['plan']):
        assert query('select count(*)from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=:t',t=case_id)==[(0,)]
        step('empty_case_cancelled_'+str(case_id),f'/api/case-pick/tasks/{case_id}/return-carrier',dict(operation_id=TAG+'.empty.case.cancel',scan_container=carrier,expected_content_version=version,destinations={},allow_empty=True,reason='Cancel empty own carrier after unpicked native wave cancellation'))
    version=query('select VERSION_NO from RRL_TRADE_TOPUP_PROPOSAL where PROPOSAL_ID=:p',p=pid)[0][0]
    result=step('reconciled',TRIP+f'/topup-proposals/{pid}/release',dict(operation_id=TAG+'.reconcile.cancelled.wave',expected_version=version))
    assert result['status']=='CANCELLED',result
    repeated=expect(200,http('POST',s['requests']['reconciled']['path'],s['requests']['reconciled']['body']))
    assert repeated['proposal_id']==pid and repeated['status']=='CANCELLED'
    order=TAG+'.ORDER'
    send('trip_restored','TRIP','T1',s['trip_before'],s['trip_version']+2)
    current,order_version=doc('ORDER',order)
    # The earlier source event was definitively rejected while still assigned.
    # After a new trip revision this is a new business attempt; keep that old
    # rejected event immutable rather than changing its stored outcome.
    send('order_cancelled_after_trip','ORDER',order,dict(current,cancelled=True),order_version+1)
    # The recipient now has its real native test customer mapping; refresh the
    # source NEED's reference version without changing forecast/quantity.
    need,need_version=doc('NEED','N1')
    _,recipient_version=doc('RECIPIENT','C1')
    send('need_refreshed','NEED','N1',dict(need,recipient_version=recipient_version),need_version+1)
    assert query('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE) from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=W)==[(250,0)]
    assert query("select STATUS from RRL_TRADE_TOPUP_HOLD where PROPOSAL_ID=:p",p=pid)==[('RELEASED',)]
    assert query('select count(*) from RRL_TRADE_TOPUP_ADOPTION where PROPOSAL_ID=:p',p=pid)==[(1,)]
    s['checks'].append('Proven unpicked wave cancellation reconciles proposal; exact retry preserves250/H0 and adoption history')
    s['slow_sql']=query('select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:n order by LOG_ID fetch first 35 rows only',n=s['slow_marker'])
    s.pop('error',None);s.pop('error_type',None)
    s['status']='PASS';save()


if __name__=='__main__':
    try:reconcile() if '--reconcile' in sys.argv else run()
    except Exception as exc:s.update(status='FAIL',error_type=type(exc).__name__,error=str(exc));raise
    finally:s['history']+=CALLS;save()
    print(json.dumps(dict(status=s['status'],proposal=s['proposal_id'],wave=s.get('wave'),evidence=str(FILE))))
