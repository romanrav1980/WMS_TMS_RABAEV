"""Bind real full-pallet movement to an explicitly synthetic logical shipment fixture."""
import json
import os
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-21/T06';FILE=OUT/'fullpal-shipment.json'
s=json.loads(FILE.read_text())if FILE.exists()else dict(history=[])


def run():
    f=json.loads((OUT/'full-pallet.json').read_text());w=f['fixture']['warehouse_id'];assert w==221164919
    uid='FP21.ST.'+str(w);task=f['task'][0]
    if 'shipment_id'not in s:
        with oracle_connection()as c:
            q=c.cursor();q.execute("select NAME from RRL_WARES where ID=:w",w=w);assert q.fetchone()==('TRADECASE QA aa5cf70d',)
            q.callproc('RRL_STOCK_METADATA_TX.begin_change',['admin','warehouse_settings_edit'])
            try:
                q.execute('select count(*)from RRL_SBORKA_PALLETS where PALLET_UID=:u',u=uid);assert q.fetchone()[0]==0
                q.execute('select trunc(sysdate)+1 from dual');day=q.fetchone()[0]
                st=q.callfunc('RRL_SBORKA_PALLETS_ADD2',int,['FP21.QA','FP21.QA.ADDRESS',1,uid,'1',day,'','admin',w]);assert st>0
                q.execute('update RRL_SBORKA_PALLETS set CONDITION=0 where ID=:s',s=st)
                row=q.callfunc('RRL_SBORKA_PALLET_ROWS_ADD4',int,[uid,f['fixture']['article'],'Whole pallet QA','','EA',0,'',10,'',10,0,None,'FP21.QA',w,1]);assert row>0
                q.execute("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,ADDRESS_TEXT,STATUS,FACT_QTY,FACT_WEIGHT,SOURCE_SYSTEM,CREATED_AT,CREATED_BY)values(RRL_CUSTOMER_ORDER_FULF_SQ.nextval,:o,:s,:u,'FP21.QA.ADDRESS','PLANNED',0,0,'QA_TRADECASE_ONLY',sysdate,'admin')",o=f['native_order'],s=st,u=uid);c.commit()
            finally:q.callproc('RRL_STOCK_METADATA_TX.end_change')
        s.update(shipment_id=st,shipment_identifier=uid);FILE.write_text(json.dumps(s,indent=2),encoding='utf-8')
    path=f'/api/warehouse-tasks/{task}/full-pallet-shipment'
    current=expect(200,http('GET',path));s['preview']=current
    body=dict(operation_id='FP21.221164919.bind',shipment_identifier=uid,scanned_pallet=current['pallet_identifier'],expected_stock_version=current['stock_version'])
    s['body']=body;value=expect(200,http('POST',path,body));s['result']=value
    assert expect(200,http('POST',path,body))==value
    with oracle_connection()as c:
        q=c.cursor();q.execute('select STATUS,FACT_QTY,PICKED_PALLET_UID,PICKED_WAREHOUSE_TASK_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=:s',s=s['shipment_id']);s['fulfillment']=list(q.fetchone());assert s['fulfillment'][0]=='PICKED'and s['fulfillment'][1]==10
        q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS l on l.CELL=r.CELL where l.WARE_ID=:w',w=w);s['physical']=list(q.fetchone());assert s['physical']==[10,10]
    s['status']='PASS'


if __name__=='__main__':
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    try:run()
    except Exception as exc:s['error']=str(exc);s['status']='FAIL';raise
    finally:s['history']+=CALLS;FILE.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')
    print(json.dumps({k:v for k,v in s.items()if k!='history'},default=str))
