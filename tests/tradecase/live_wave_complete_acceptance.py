"""Native replenishment movement and exact replay on the owned wave fixture."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-19/T04/wave-554eebf3-complete.json'
source=json.loads((OUT.parent/'wave-554eebf3.json').read_text());task=source['tasks'][0];tid,_,_,pallet,from_cell,to_cell,qty=task
s=dict(warehouse_id=source['warehouse_id'],wave_id=source['wave_id'],task_id=tid,status='RUNNING')
body=dict(operation_id='T4.complete.554eebf3',scanned_pallet=pallet,scanned_from_cell=from_cell,scanned_to_cell=to_cell,fact_qty=str(qty))
s['body']=body;OUT.write_text(json.dumps(s,indent=2),encoding='utf-8')
try:
    bad=dict(body,operation_id='T4.bad.complete.554eebf3',scanned_to_cell='WRONG.T4')
    expect(409,http('POST',f'/api/warehouse-tasks/{tid}/complete',bad))
    s['result']=expect(200,http('POST',f'/api/warehouse-tasks/{tid}/complete',body))
    s['replay']=expect(200,http('POST',f'/api/warehouse-tasks/{tid}/complete',body))
    with oracle_connection()as c:
        q=c.cursor();q.execute('select CELL,REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p order by CELL',p=pallet);s['stock']=[list(x)for x in q];assert sum(x[1]for x in s['stock'])==250 and sum(x[2]for x in s['stock'])==100
        q.execute("select CURRENT_CELL,count(*)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p and STOCK_STATUS<>'ISSUED'group by CURRENT_CELL",p=pallet);s['composition']=[list(x)for x in q];assert s['composition']==[[to_cell,250]]
        q.execute("select count(*)from user_objects where status='INVALID'and object_name not like'BIN$%'");assert q.fetchone()[0]==0
    s['status']='PASS';print(json.dumps({k:s[k]for k in['status','stock','composition']}))
except Exception as e:s.update(status='FAIL',error=str(e));raise
finally:s['http']=CALLS;OUT.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')
