"""Resume a whole factory pallet through existing native wave/task commands."""
from datetime import datetime,timedelta,timezone
import json
import os
from pathlib import Path
import re
import sys
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
import live_factory_box as box
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-21/T06';FILE=OUT/'full-pallet.json'
s=json.loads(FILE.read_text())if FILE.exists()else dict(history=[])


def save():
    FILE.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')


def step(key,path,body,method='POST'):
    if key not in s:s[key]=expect(200,http(method,path,body));save()
    return s[key]


def prepare(attempt_rejected=True):
    if 'fixture'not in s:
        f=box.setup();s['fixture']={k:v for k,v in f.items()if k!='password'};save()
        box.split_box=lambda *_:dict(status='NOT_RUN',reason='Whole pallet retained for FULL_PALLET proof')
        s['receipt_proof']=box.run(f);save()
    f=s['fixture'];w=f['warehouse_id'];tag='FP21.'+str(w);base=f'/api/tradecase/warehouses/{w}'
    with oracle_connection()as c:
        q=c.cursor();q.execute("select NAME from RRL_WARES where ID=:w",w=w);assert q.fetchone()==('TRADECASE QA '+f['tag'],)
    receipt=next(x['response']for x in s['history']+CALLS if x['status']==201 and '/receiving/supply-orders/'in x['path'])
    step('putaway',f"/api/receiving/putaway/{receipt['task_id']}/complete",dict(scanned_pallet=f['pallet'],scanned_from_cell=f['receive'],scanned_to_cell=receipt['putaway_cell']))
    step('expedition',base+'/stock/cells/'+f['receive'],dict(operation_id=tag+'.expedition',expected_version=1,zone_kind='EXPEDITION',reason='Owned whole-pallet fixture staging zone'),'PUT')
    units=expect(200,http('GET',base+'/stock?pallet_identifier='+f['pallet']+'&limit=100'))['items']
    step('mark_valid',base+'/stock/mark-confirmations',dict(operation_id=tag+'.valid',skm_id='TC03.SKM',external_event_id=tag+'.valid',expected_site_version=1,occurred_at=datetime.now(timezone.utc).isoformat(),
        items=[dict(physical_unit_key=x['physical_unit_key'],expected_attribute_version=x['attribute_version'],verdict='VALID')for x in units]))
    if 'norm'in s:pass
    else:
        with oracle_connection()as c:
            q=c.cursor();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
            try:
                q.execute('update RRL_ARTICULS set NORMA_UKLADKI=1,COUNT_IN_ROW=1,ROWS_IN_PAL=1,COUNT_SHT_IN_KOR=10 where ACTICUL=:a',a=f['article']);assert q.rowcount==1;c.commit()
            finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
        s['norm']=True;save()
    customer=step('customer','/api/customers',dict(customer_code=tag,customer_name='Whole pallet QA',customer_type='LEGAL_ENTITY'))['customer_id']
    now=datetime.now(timezone.utc);ship=(now+timedelta(days=1)).isoformat()
    def send(kind,payload):
        return step(kind,'/api/tradecase/messages',dict(schema_version=1,event_id=tag+'.'+kind,source_id='TC03.SAP',warehouse_id=w,document_id=tag+'.'+kind,version=1,occurred_at=now.isoformat(),payload=dict(entity_type=kind,**payload)))
    send('RECIPIENT',dict(title='Whole pallet QA',wms_customer_id=customer,target_owner_id='SNS',permitted_source_owners=['SNS'],buyout_mode='BEFORE_PICK',min_osg_days=0,lead_time_days=0,allow_broken_box=False))
    send('ORDER',dict(recipient_id=tag+'.RECIPIENT',planned_ship_at=ship,lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='SNS',mrc='200',quantity='10',uom='EA',min_osg_days=0)]))
    if 'native_order'not in s:
        with oracle_connection()as c:
            q=c.cursor();q.callproc('RRL_STOCK_METADATA_TX.begin_change',['admin','warehouse_settings_edit'])
            try:
                q.execute('select RRL_CUSTOMER_ORDER_SQ.nextval,RRL_CUSTOMER_ORDER_ROW_SQ.nextval from dual');order,row=q.fetchone()
                q.execute("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID,SHIPMENT_DATE,STATUS,SOURCE_SYSTEM,CREATED_BY)values(:o,:n,:c,:w,trunc(sysdate)+1,'OPEN','QA_TRADECASE_ONLY','admin')",o=order,n=tag,c=customer,w=w)
                q.execute("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,PRODUCT_NAME,UNIT_CODE,ORDER_QTY,WARE_ID,STATUS,CREATED_BY)values(:r,:o,1,:a,'Whole pallet QA','EA',10,:w,'OPEN','admin')",r=row,o=order,a=f['article'],w=w);c.commit()
            finally:q.callproc('RRL_STOCK_METADATA_TX.end_change')
        s.update(native_order=order,native_row=row);save()
    step('binding',base+'/orders/'+tag+'.ORDER/binding',dict(operation_id=tag+'.bind',expected_order_version=1,customer_order_id=s['native_order'],lines=[dict(line_id='1',customer_order_row_id=s['native_row'])]))
    plan=step('plan','/api/picking/plans',dict(operation_id=tag+'.plan',customer_order_id=s['native_order']))['pick_plan_id']
    wave=step('wave','/api/picking/waves',dict(wave_code=tag,wave_name='Whole pallet QA',ware_id=w,planned_start_at=now.isoformat(),planned_finish_at=ship))['pick_wave_id'];s['wave_id']=wave;save()
    route=f'/api/picking/waves/{wave}'
    step('added',route+'/plans',dict(pick_plan_id=plan));step('calculated',route+'/calculate',{});step('launched',route+'/launch',dict(operation_id=tag+'.launch'))
    step('staging',route+'/staging/release',dict(to_cell=f['receive']))
    step('pick_release',route+'/release-picking',dict(operation_id=tag+'.release'))
    with oracle_connection()as c:
        q=c.cursor();q.execute("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=:w and TASK_TYPE='PICKING_MOVE'",w=wave);tasks=q.fetchall();assert len(tasks)==1,tasks;s['task']=list(tasks[0]);save()
    tid,pallet,src,dst,qty=s['task'];body=dict(operation_id=tag+'.complete.v2',scanned_pallet=pallet,scanned_from_cell=src,scanned_to_cell=dst,fact_qty=str(qty))
    s['complete_body']=body;save()
    if not attempt_rejected:return
    before=http('POST',f'/api/warehouse-tasks/{tid}/complete',body);s['admission_before']=before;save()
    assert before[0]==409 and 'TRADE_TASK_BINDING_REQUIRED'in str(before),before


if __name__=='__main__':
    os.environ.setdefault('TRADECASE_ADMIN_USER','admin');os.environ.setdefault('TRADECASE_ADMIN_PASSWORD',re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1])
    try:prepare()
    except Exception as exc:s['error']=str(exc);raise
    finally:
        if 'fixture'in s:
            with oracle_connection()as c:
                f=s['fixture'];q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=f['actor'])
                q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=f['role']);c.commit()
        s['history']+=CALLS;save()
