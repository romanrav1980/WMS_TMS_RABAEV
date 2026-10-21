"""Commit/replay the prepared native whole-pallet move, preserving failed responses."""
import json
import os
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-21/T06'


def run():
    s=json.loads((OUT/'full-pallet.json').read_text());f=s['fixture']
    assert f['warehouse_id']==221164919 and f['tag']=='aa5cf70d'
    with oracle_connection()as c:
        q=c.cursor();q.execute("select NAME from RRL_WARES where ID=:w",w=f['warehouse_id']);assert q.fetchone()==('TRADECASE QA aa5cf70d',)
    body=dict(s['complete_body'],operation_id='FP21.221164919.complete.context-fixed')
    result=expect(200,http('POST',f"/api/warehouse-tasks/{s['task'][0]}/complete",body))
    assert expect(200,http('POST',f"/api/warehouse-tasks/{s['task'][0]}/complete",body))==result
    report=dict(status='PASS',body=body,result=result)
    with oracle_connection()as c:
        q=c.cursor();q.execute('select r.UID_POLETA,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE from RRL_REMAINS r join RRL_CELLS l on l.CELL=r.CELL where l.WARE_ID=:w',w=f['warehouse_id']);report['stock']=[list(x)for x in q]
        assert sum(x[2]for x in report['stock'])==10
        q.execute('select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:t',t=s['task'][0]);report['task_status']=q.fetchone()[0];assert report['task_status']=='DONE'
        q.execute("select PALLET_UID,STATUS from RRL_PICK_TASK where PICK_TASK_ID in(select PICK_TASK_ID from RRL_PICK_WAVE_TASK where PICK_WAVE_ID=:w)",w=s['wave_id']);report['pick_tasks']=[list(x)for x in q]
        q.execute('select LEGACY_SBORKA_PALLET_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:o',o=s['native_order']);report['fulfillments']=[list(x)for x in q]
        q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:o and STATE='APPLIED'",o=body['operation_id']);assert q.fetchone()[0]==1
    return report


if __name__=='__main__':
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    report=dict(status='FAIL')
    try:report.update(run())
    except Exception as exc:report['error']=str(exc);raise
    finally:
        report['history']=CALLS;(OUT/'fullpal-move-result.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items()if k!='history'},default=str))
