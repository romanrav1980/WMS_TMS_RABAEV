"""Independent pending deals and competing financial claims on fresh actual receipt stock."""
import sys,json
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
from live_stock_acceptance import setup,run as receive_stock
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-19/T05';f=None;report={}
def run(f):
    receive_stock(f);ware=f['warehouse_id'];tag=f['tag'];root=f'/api/tradecase/warehouses/{ware}';base=root+'/buyouts';stamp=datetime.now(timezone.utc).isoformat()
    def send(kind,id,body):return expect(200,http('POST','/api/tradecase/messages',dict(schema_version=1,event_id='TC5R.'+id,source_id='TC03.SAP',warehouse_id=ware,document_id=id,version=1,occurred_at=stamp,payload=dict(entity_type=kind,**body))))
    with oracle_connection()as c:
        q=c.cursor();q.execute('select a.PHYSICAL_UNIT_KEY,a.VERSION_NO from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY where a.CAPTURE_WARE_ID=:w order by to_number(u.UNIT_ID)',w=ware);rows=q.fetchall()
    keys=[x[0]for x in rows]
    expect(200,http('POST',root+'/stock/mark-confirmations',dict(operation_id='TC5R.mark.'+tag,skm_id='TC03.SKM',external_event_id='TC5R.mark.'+tag,expected_site_version=1,occurred_at=stamp,items=[dict(physical_unit_key=k,expected_attribute_version=v,verdict='VALID')for k,v in rows])))
    send('RECIPIENT','BUYER',dict(title='TRADECASE concurrency QA',target_owner_id='BLC',permitted_source_owners=['SNS'],buyout_mode='BEFORE_PICK',lead_time_days=0,min_osg_days=0))
    for name,qty in [('MAIN',250),('C1',50),('C2',50)]:
        send('ORDER',name,dict(recipient_id='BUYER',order_kind='BUYOUT',buyout_mode='BEFORE_PICK',planned_ship_at=stamp,lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='BLC',mrc='200',quantity=str(qty),uom='EA',min_osg_days=0)]))
    def body(name,basis,units):return dict(operation_id='TC5R.request.'+tag+'.'+name,buyout_id='TC5R.'+tag+'.'+name,basis_order_id=basis,basis_line_id='1',expected_basis_version=1,unit_keys=units)
    a,b=body('A','MAIN',keys[:100]),body('B','MAIN',keys[100:200]);f['buyout_requests']=[a,b]
    with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(lambda v:http('POST',base,v),(a,b)))
    assert [r[0]for r in results]==[200,200],results
    c1,c2=body('C1','C1',keys[200:]),body('C2','C2',keys[200:])
    with ThreadPoolExecutor(max_workers=2)as pool:race=list(pool.map(lambda v:http('POST',base,v),(c1,c2)))
    assert sorted(r[0]for r in race)==[200,409],race
    winner=c1 if race[0][0]==200 else c2;f['buyout_requests'].append(winner)
    mixed=expect(200,http('POST',base+'/results',dict(operation_id='TC5R.result.'+tag,buyout_id=a['buyout_id'],expected_version=1,skm_id='TC03.SKM',external_event_id='TC5R.result.'+tag,external_document_id='TC5R.doc.'+tag,occurred_at=stamp,items=[dict(physical_unit_key=k,outcome='CONFIRMED')for k in keys[:80]]+[dict(physical_unit_key=k,outcome='REJECTED',reason='QA refused subset')for k in keys[80:100]])))
    assert mixed['confirmed_units']==80 and mixed['rejected_units']==20 and mixed['requires_sorting']is True,mixed
    with oracle_connection()as c:
        q=c.cursor();q.execute("select RRL_STOCK_ELIGIBILITY.reason(:p,:c,:w,0,null,null,'ALLOCATE')from dual",p=f['pallet'],c=f['current_cell'],w=ware);reason=q.fetchone()[0];assert reason=='TRADE_MIXED_PALLET_BLOCKED',reason
        q.execute('select count(*)from RRL_TRADE_BUYOUT_UNIT bu join RRL_TRADE_BUYOUT b on b.BUYOUT_ID=bu.BUYOUT_ID where b.WARE_ID=:w and bu.HOLD_ACTIVE=1',w=ware);assert q.fetchone()[0]==150
        q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=ware);assert q.fetchone()==(250,0)
    f['confirmed_unit_keys']=keys[:80];f['pending_unit_keys']=keys[100:];f['financial_partials']=[a['buyout_id']]
    return dict(status='PASS',independent_pending=[r[0]for r in results],same_codes_race=[r[0]for r in race],physical_quantity=250,hard_reserved=0,owner_counts=dict(BLC=80,SNS=170),buyout_held=150,admission_reason=reason,provider='LOCAL_SYNTHETIC_ONLY')
if __name__=='__main__':
    try:f=setup();report=run(f)
    except Exception as e:report=dict(status='FAIL',error=str(e));raise
    finally:
        if f:
            with oracle_connection()as c:
                q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:u and USER_GROUP='TC03QA'",u=f['actor']);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:r',r=f['role']);c.commit()
            f.pop('password',None);report['fixture']=f
        report['http']=CALLS;p=OUT/('buyout-race-'+(f['tag']if f else'failed')+'.json');p.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],file=str(p),warehouse_id=f['warehouse_id'],http_calls=len(CALLS))))
