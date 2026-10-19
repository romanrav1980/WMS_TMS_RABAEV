"""Local synthetic SKM responses against native stock; not external interoperability proof."""
import sys,json,os
from pathlib import Path
from uuid import uuid4
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-19/T03'
WARE=225837931

def run():
    with oracle_connection()as c:
        q=c.cursor();q.execute("select PHYSICAL_UNIT_KEY,VERSION_NO from RRL_TRADE_STOCK_ATTR where CAPTURE_WARE_ID=:w and MARK_STATE='PENDING'order by PHYSICAL_UNIT_KEY",w=WARE);keys=q.fetchall()
        q.execute('select VERSION_NO from RRL_TRADE_SITE where WARE_ID=:w',w=WARE);version=q.fetchone()[0]
        q.execute('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG');marker=q.fetchone()[0]
    assert len(keys)>=6,keys
    tag=uuid4().hex[:10];path=f'/api/tradecase/warehouses/{WARE}/stock/mark-confirmations'
    def body(indices,op=None):return dict(operation_id=op or 'T3.mark.'+uuid4().hex,skm_id='TC03.SKM',external_event_id='SKM.'+uuid4().hex,expected_site_version=version,occurred_at=datetime.now(timezone.utc).isoformat(),items=[dict(physical_unit_key=keys[i][0],expected_attribute_version=keys[i][1],verdict='VALID')for i in indices])
    wrong=body([0]);wrong['skm_id']='WRONG.SKM';expect(409,http('POST',path,wrong))
    wrong=body([0]);wrong['expected_site_version']=version+1;expect(409,http('POST',path,wrong))
    # First update must roll back when a later member is stale.
    failed=body([0,1]);failed['items'][1]['expected_attribute_version']+=10
    expect(409,http('POST',path,failed))
    with oracle_connection()as c:
        q=c.cursor();q.execute('select MARK_STATE,VERSION_NO from RRL_TRADE_STOCK_ATTR where PHYSICAL_UNIT_KEY=:k',k=keys[0][0]);assert q.fetchone()==('PENDING',keys[0][1])
        q.execute('select count(*)from RRL_TRADE_MARK_EVENT where OPERATION_ID=:op',op=failed['operation_id']);assert q.fetchone()[0]==0
    valid=body([0,1]);r=expect(200,http('POST',path,valid));assert r['confirmed_units']==2 and r['stock_changed']is False and r['owner_changed']is False
    assert expect(200,http('POST',path,valid))['replayed']
    changed=deepcopy(valid);changed['items'][0]['verdict']='REJECTED';changed['items'][0]['external_reason']='QA negative';expect(409,http('POST',path,changed))
    duplicate=deepcopy(valid);duplicate['operation_id']='T3.alias.'+tag;expect(409,http('POST',path,duplicate))
    stale=body([0]);expect(409,http('POST',path,stale))
    left,right=body([2]),body([2])
    with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(lambda b:http('POST',path,b),(left,right)))
    assert sorted(x[0]for x in results)==[200,409],results
    rejected=body([3]);rejected['items'][0].update(verdict='REJECTED',external_reason='QA invalid mark')
    expect(200,http('POST',path,rejected))
    # An unprivileged legacy user cannot use the integration endpoint.
    with oracle_connection()as c:
        q=c.cursor();q.execute("select ID from RUSERS where nvl(DELETED,0)=0 and USER_GROUP<>'GLOBAL_ADMIN'and rownum=1");unused=q.fetchone()
        q.execute('select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=(select CURRENT_UID from RRL_WMS_RECEIPT_UNIT where PHYSICAL_UNIT_KEY=:k)and CELL=(select CURRENT_CELL from RRL_WMS_RECEIPT_UNIT where PHYSICAL_UNIT_KEY=:k)',k=keys[0][0]);assert q.fetchone()==(250,0)
        q.execute("select count(*)from user_objects where status='INVALID'and object_name not like'BIN$%'");assert q.fetchone()[0]==0
        q.execute('select LOG_ID,ELAPSED_MS,OPERATION_KIND,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:n order by LOG_ID fetch first 40 rows only',n=marker);slow=[list(x)for x in q]
    return dict(status='PASS',warehouse_id=WARE,validated=3,rejected=1,pending=len(keys)-4,physical_quantity=250,hard_reserved=0,external_provider='LOCAL_SYNTHETIC_ONLY',slow_sql=slow)

if __name__=='__main__':
    report={}
    try:report=run()
    except Exception as e:report=dict(status='FAIL',error=str(e));raise
    finally:
        report['http']=CALLS;p=OUT/('mark-acceptance-'+uuid4().hex[:8]+'.json');p.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],file=str(p),http_calls=len(CALLS))))
