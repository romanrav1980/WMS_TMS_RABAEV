"""Native rollback and concurrent reverse facts on the retained TRADECASE full pallet."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'api/wms_api_server'),str(Path(__file__).parent)]
from app.modules.inventory.contracts_stock import StockCommand
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
import oracledb

PATH=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T07/full-pallet-reload.json'
s=json.loads(PATH.read_text(encoding='utf-8'))


def save():PATH.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')


def stock(q):
    q.execute('select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=s['warehouse_id'])
    return list(q.fetchone())


if __name__=='__main__':
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    assert s['warehouse_id']==221164919 and s['carrier']=='690000000582192776'
    try:
        if 'unload_body'not in s:
            load=s['load_body'];s['unload_body']=dict(operation_id='TFP22.UNLOAD.1219',load_operation_id=load['operation_id'],expected_version=load['expected_version'],scan_container=load['scan_container'],scan_cell=load['scan_cell'],scan_vehicle=load['scan_vehicle'],scan_dock=load['scan_dock'],reason='Synthetic QA physical removal before departure');save()
        body=s['unload_body'];url='/api/transport/loading/unload'
        if 'unloaded'not in s:
            if 'unload_rollback'not in s:
                with oracle_connection()as conn:
                    q=conn.cursor();assert stock(q)==[0,0]
                    canonical=StockCommand(operation_id=body['operation_id'],command_type='UNLOAD_SHIPMENT',actor='admin',source=dict(load_operation_id=body['load_operation_id']),lines=(),metadata={k:v for k,v in body.items()if k not in ('operation_id','load_operation_id')}).canonical_json()
                    out=q.var(oracledb.DB_TYPE_CLOB)
                    try:
                        q.callproc('RRL_STOCK_POSTING_API.prepare_command',[canonical,'admin',out,None]);assert out.getvalue()is None
                        q.callproc('RRL_STOCK_POSTING_API.execute_prepared',[out]);assert stock(q)==[10,10]
                    finally:conn.rollback();q.callproc('RRL_STOCK_POSTING_API.reset_connection')
                    assert stock(q)==[0,0]
                s['unload_rollback']='PASS';save()
            expect(409,http('POST',url,dict(body,scan_vehicle='OTHER')))
            expect(422,http('POST',url,dict(body,quantity='1')))
            s['unload_attempts']=[body,dict(body,operation_id=body['operation_id']+'.RACE')];save()
            with ThreadPoolExecutor(2)as pool:responses=list(pool.map(lambda x:http('POST',url,x),s['unload_attempts']))
            s['unload_race']=responses;save();assert sorted(x[0]for x in responses)==[200,409],responses
            s['unloaded']=next(x[1]for x in responses if x[0]==200)
            s['unload_body']=next(x for x in s['unload_attempts']if x['operation_id']==s['unloaded']['operation_id']);save()
        assert expect(200,http('POST',url,s['unload_body']))==s['unloaded']
        with oracle_connection()as conn:
            q=conn.cursor();assert stock(q)==[10,10]
            q.execute('select STATUS,FACT_QTY,PICKED_STOCK_VERSION from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=(select ID from RRL_SBORKA_PALLETS where PALLET_UID=:p)',p=s['st_pallet']);s['unload_fulfillment']=list(q.fetchone());assert s['unload_fulfillment'][0]=='PICKED'and s['unload_fulfillment'][1]==10
            q.execute('select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:o',o=s['unloaded']['operation_id']);assert q.fetchone()[0]==10
            q.execute("select STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:o",o=s['load_body']['operation_id']);assert q.fetchone()[0]=='UNLOADED'
        s['unload_stage']='PASS';print(json.dumps(dict(status='PASS',stock=[10,10],operation=s['unloaded']['operation_id'],concurrent_statuses=[x[0]for x in s['unload_race']])))
    finally:s['http']+=CALLS;save()
