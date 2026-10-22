"""Resume the retained ten-unit factory receipt; prepare two native CASE orders."""
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
import live_factory_case as case
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T07'
FILE=OUT/'bulk-source-state.json'
PROOF=ROOT/'runtime/test-evidence/tradecase/2026-10-21/T03/factory-box-220793322.json'
old=json.loads(PROOF.read_text(encoding='utf-8'));f=old['fixture'];w=f['warehouse_id']
s=json.loads(FILE.read_text(encoding='utf-8'))if FILE.exists()else dict(fixture=f,created_at=datetime.now(timezone.utc).isoformat(),requests={},results={},history=[])


def save():FILE.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')


def step(key,path,body):
    if key not in s['requests']:s['requests'][key]=dict(path=path,body=body);save()
    request=s['requests'][key]
    if key not in s['results']:s['results'][key]=expect(200,http('POST',request['path'],request['body']));save()
    return s['results'][key]


def source():
    with oracle_connection()as c:
        q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==('RABAEV','orcl')
        q.execute('select NAME from RRL_WARES where ID=:w',w=w);assert q.fetchone()==('TRADECASE QA a4b16acd',)
        q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=w)
        if 'baseline'not in s:s['baseline']=list(q.fetchone());assert s['baseline']==[10,0];save()
        q.execute('select c.SYSTEM_CODE,c.RAW_CODE from RRL_WMS_RECEIPT_CODE c where c.UID_PALLET=:p order by c.UNIT_ID',p=f['pallet'])
        codes=[dict(system_code=a,profile_code='TOBACCO',code=b.read()if hasattr(b,'read')else b)for a,b in q];assert len(codes)==10
    received=next(x for x in old['http']if x['status']==201)
    native_order=re.search('/supply-orders/([^/]+)/pallets',received['path'])[1]
    base=f'/api/tradecase/warehouses/{w}'
    step('supply','/api/tradecase/messages',dict(schema_version=1,event_id='BULK22.SUPPLY.'+str(w),source_id='TC03.SAP',warehouse_id=w,document_id='BULK22.SUPPLY',version=1,occurred_at=s['created_at'],
        payload=dict(entity_type='SUPPLY',wms_article_id=f['article'],sap_order_id=native_order,sap_line_id='1',sku_id='A',owner_id='SNS',mrc='200',pallet_identifier=f['pallet'],supplier_batch='BOX.'+f['tag'],expiry_date='2030-01-01',composition_source='SAP',codes=codes)))
    step('bound',base+'/stock/bind',dict(operation_id='BULK22.BIND.'+str(w),supply_id='BULK22.SUPPLY',expected_supply_version=1,scanned_pallet=f['pallet']))
    receipt=received['response']
    step('putaway',f"/api/receiving/putaway/{receipt['task_id']}/complete",dict(scanned_pallet=f['pallet'],scanned_from_cell=f['receive'],scanned_to_cell=receipt['putaway_cell']))
    with oracle_connection()as c:
        q=c.cursor();q.execute('select PHYSICAL_UNIT_KEY,VERSION_NO from RRL_TRADE_STOCK_ATTR where CAPTURE_WARE_ID=:w order by PHYSICAL_UNIT_KEY',w=w);items=list(q);assert len(items)==10
    step('mark_valid',base+'/stock/mark-confirmations',dict(operation_id='BULK22.VALID.'+str(w),skm_id='TC03.SKM',external_event_id='BULK22.VALID.'+str(w),expected_site_version=1,occurred_at=s['created_at'],
        items=[dict(physical_unit_key=k,expected_attribute_version=v,verdict='VALID')for k,v in items]))
    s['source_status']='RESUMED_NO_NEW_RECEIPT';save()


def prepare_cases():
    for i in range(2):
        case.OUT=OUT;case.FILE=OUT/f'bulk-case-{i}.json';case.w=w;case.base=f'/api/tradecase/warehouses/{w}';case.tag=f'BULK22.{i}.{w}'
        case.s=json.loads(case.FILE.read_text(encoding='utf-8'))if case.FILE.exists()else dict(warehouse_id=w,article=f['article'],pick=f['pick'],history=[])
        case.prepare()
        assert case.s['admission_before']==1,case.s['case']
    s['cases_prepared']=True;save()


if __name__=='__main__':
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    try:source();prepare_cases()
    except Exception as exc:s['error']=str(exc);save();raise
    finally:s['history']+=CALLS;save()
