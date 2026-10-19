"""Real native planning on a new received stock fixture; customer-demand metadata is seeded, not SAP integration."""
import sys,json
from pathlib import Path
from uuid import uuid4
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
from live_stock_acceptance import setup,run as receive_stock
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-19/T04'

def run(f):
    ware=f['warehouse_id'];tag=f['tag'];base=f'/api/tradecase/warehouses/{ware}'
    if not f.get('current_cell'):receive_stock(f)
    with oracle_connection()as c:
        q=c.cursor();q.execute('select CUSTOMER_ID from RRL_CUSTOMER where CUSTOMER_CODE=upper(:code)',code='T4.'+tag);existing=q.fetchone()
    customer=existing[0]if existing else expect(200,http('POST','/api/customers',dict(customer_code='T4.'+tag,customer_name='TRADECASE QA '+tag,customer_type='LEGAL_ENTITY')))['customer_id']
    f['customer_id']=customer
    if not f.get('pick_face_id'):
        route=expect(200,http('POST','/api/picking/routes',dict(route_code='T4.'+tag,route_name='TRADECASE QA',ware_id=ware)))['pick_route_id']
        route_cell=expect(200,http('POST','/api/picking/route-cells',dict(pick_route_id=route,cell_code=f['pick'],pick_sequence=1)))['pick_route_cell_id']
        face=expect(200,http('POST','/api/picking/pick-faces',dict(ware_id=ware,cell_code=f['pick'],pick_face_code='T4.'+tag,pick_route_id=route,pick_route_cell_id=route_cell,pick_sequence=1,min_case_qty=0,max_case_qty=100,replenishment_trigger_qty=1)))['pick_face_id']
        expect(200,http('POST',f'/api/picking/pick-faces/{face}/articuls',dict(articul=f['article'],priority='1',min_qty='0',max_qty='100',replenishment_method='IMMEDIATE',replenishment_qty_mode='FILL_TO_VOLUME',use_articul_replenish_rule=0,boxes_per_layer='5',boxes_per_pallet='25',box_volume_m3='0.01')))
        f.update(pick_face_id=face,pick_route_id=route,pick_route_cell_id=route_cell)
    def send(kind,identifier,body,version=1):
        return expect(200,http('POST','/api/tradecase/messages',dict(schema_version=1,event_id=uuid4().hex,source_id='TC03.SAP',warehouse_id=ware,document_id=identifier,version=version,occurred_at=datetime.now(timezone.utc).isoformat(),payload=dict(entity_type=kind,**body))))
    send('SKU','A',dict(title='TRADECASE QA '+tag,wms_article_id=f['article'],units_per_box=10,permitted_mrc=['200','201']),2)
    with oracle_connection()as c:
        q=c.cursor();q.execute("select PHYSICAL_UNIT_KEY,VERSION_NO from RRL_TRADE_STOCK_ATTR where CAPTURE_WARE_ID=:w and MARK_STATE='PENDING'",w=ware);keys=q.fetchall()
    mark=dict(operation_id='T4.mark.'+tag,skm_id='TC03.SKM',external_event_id='T4.mark.'+tag,expected_site_version=1,occurred_at=datetime.now(timezone.utc).isoformat(),items=[dict(physical_unit_key=k,expected_attribute_version=v,verdict='VALID')for k,v in keys])
    if keys:expect(200,http('POST',base+'/stock/mark-confirmations',mark))
    def order(name,mode,qty=100,mrc='200',osg=0,binding=True):
        recipient='C.'+name
        send('RECIPIENT',recipient,dict(title='TRADECASE '+name,wms_customer_id=customer,target_owner_id='BLC',permitted_source_owners=['SNS'],buyout_mode=mode,min_osg_days=0,lead_time_days=0))
        send('ORDER',name,dict(recipient_id=recipient,planned_ship_at='2026-11-01T10:00:00+03:00',lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='BLC',mrc=mrc,quantity=str(qty),uom='EA',min_osg_days=osg)]))
        with oracle_connection()as c:
            q=c.cursor();q.callproc('RRL_STOCK_METADATA_TX.begin_change',['admin','warehouse_settings_edit'])
            try:
                q.execute('select RRL_CUSTOMER_ORDER_SQ.nextval,RRL_CUSTOMER_ORDER_ROW_SQ.nextval from dual');native,row=q.fetchone()
                q.execute("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID,SHIPMENT_DATE,STATUS,SOURCE_SYSTEM,CREATED_BY)values(:n,:code,:c,:w,to_date('2026-11-01','YYYY-MM-DD'),'OPEN','QA_TRADECASE_ONLY','admin')",n=native,code='T4.'+tag+'.'+name,c=customer,w=ware)
                q.execute("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,PRODUCT_NAME,UNIT_CODE,ORDER_QTY,WARE_ID,STATUS,CREATED_BY)values(:r,:n,1,:a,'TRADECASE QA','EA',:qty,:w,'OPEN','admin')",r=row,n=native,a=f['article'],qty=qty,w=ware)
                c.commit()
            finally:q.callproc('RRL_STOCK_METADATA_TX.end_change')
        if binding:
            body=dict(operation_id='T4.bind.'+tag+'.'+name,expected_order_version=1,customer_order_id=native,lines=[dict(line_id='1',customer_order_row_id=row)])
            result=expect(200,http('POST',base+'/orders/'+name+'/binding',body));assert result['bound_lines']==1 and result['stock_changed']is False
            assert expect(200,http('POST',base+'/orders/'+name+'/binding',body))['replayed']
        return int(native)
    def plan(native,name):return expect(200,http('POST','/api/picking/plans',dict(operation_id='T4.plan.'+tag+'.'+name,customer_order_id=native)))['pick_plan_id']
    def planned(plan_id):
        with oracle_connection()as c:
            q=c.cursor();q.execute("select nvl(sum(RESERVED_QTY),0)from RRL_PICK_RESERVATION where PICK_PLAN_ID=:p and RESERVATION_STATUS='ACTIVE'and RESERVATION_LEVEL='SOFT'",p=plan_id);return q.fetchone()[0]
    unbound=order('UNBOUND','AFTER_PICK',binding=False);assert planned(plan(unbound,'UNBOUND'))==0
    before=order('BEFORE','BEFORE_PICK');assert planned(plan(before,'BEFORE'))==0
    price=order('MRC','AFTER_PICK',mrc='201');assert planned(plan(price,'MRC'))==0
    expiry=order('OSG','AFTER_PICK',osg=3650);assert planned(plan(expiry,'OSG'))==0
    after=order('AFTER','AFTER_PICK');p=plan(after,'AFTER');assert planned(p)==100;assert plan(after,'AFTER')==p
    transit=order('TRANSIT','IN_TRANSIT',qty=40);tp=plan(transit,'TRANSIT');assert planned(tp)==40
    with oracle_connection()as c:
        q=c.cursor();q.execute('select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p and CELL=:c',p=f['pallet'],c=f['current_cell']);assert q.fetchone()==(250,0)
        q.execute("select count(*)from user_objects where status='INVALID'and object_name not like'BIN$%'");assert q.fetchone()[0]==0
        q.execute('select LOG_ID,ELAPSED_MS,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:n order by LOG_ID fetch first 60 rows only',n=f['slow_marker']);slow=[list(x)for x in q]
    f.update(customer_id=customer,after_order=after,after_plan=p,transit_order=transit,transit_plan=tp)
    return dict(status='PASS',source_demand='SEEDED_NATIVE_METADATA_NOT_SAP',physical_quantity=250,hard_reserved=0,soft_planned=140,unbound_blocked=True,before_buyout_blocked=True,wrong_mrc_blocked=True,osg_blocked=True,slow_sql=slow)

if __name__=='__main__':
    f=None;report={};OUT.mkdir(parents=True,exist_ok=True)
    try:
        f=json.loads(Path(sys.argv[1]).read_text())["fixture"]if len(sys.argv)>1 else setup()
        report=run(f)
    except Exception as e:report=dict(status='FAIL',error=str(e));raise
    finally:
        if f:
            with oracle_connection()as c:
                q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=f['actor']);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:r',r=f['role']);c.commit()
            f.pop('password',None);report['fixture']=f
        report['http']=CALLS;p=OUT/('planning-'+uuid4().hex[:8]+'.json');p.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],file=str(p),warehouse_id=f['warehouse_id'],http_calls=len(CALLS))))
