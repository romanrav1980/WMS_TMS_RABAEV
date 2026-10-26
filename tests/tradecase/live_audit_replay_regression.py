"""Existing committed operation replay after audit concurrency changes; no new warehouse operation."""
import base64,json,os,re,sys
from urllib.request import Request,urlopen
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import live_shipment_events as p

def main():
    assert p.s['phase']=='CLOSED'
    password=re.search(r'PASS=(\S+?)[\x60,)\s]',(p.qa.ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=password
    auth='Basic '+base64.b64encode(('admin:'+password).encode()).decode()
    op=p.s['steps']['depart']['body']['operation_id'];trip=p.s['transport']['transport_task_id']
    with p.qa.oracle_connection()as c:
        q=c.cursor();before=p.events(q,op)
    request=Request(f'http://127.0.0.1:8088/api/transport/loading/{trip}/depart',data=json.dumps(dict(operation_id=op)).encode(),headers={'Authorization':auth,'Content-Type':'application/json'},method='POST')
    with urlopen(request,timeout=35)as response:
        body=json.loads(response.read());call_id=int(response.headers['X-WMS-API-Call-Id']);request_id=response.headers['X-WMS-Request-Id']
    assert body==p.s['steps']['depart']['result']
    changed=p.qa.expect(409,p.qa.http('POST',f"/api/transport/loading/{p.s['next_trip']}/depart",dict(operation_id=op)))
    assert 'CONFLICT'in json.dumps(changed),changed
    detail_request=Request(f'http://127.0.0.1:8088/api/admin/api-calls/{call_id}',headers={'Authorization':auth})
    with urlopen(detail_request,timeout=35)as response:
        detail=json.loads(response.read());admin_call_id=int(response.headers['X-WMS-API-Call-Id'])
    with p.qa.oracle_connection()as c:
        q=c.cursor();assert p.events(q,op)==before
        q.execute('select REQUEST_ID,RESPONSE_STATUS,REPLAYABLE,STATUS from RRL_API_CALL_LOG where API_CALL_ID=:i',i=call_id);assert q.fetchone()==(request_id,200,1,'DONE')
        q.execute('select REPLAYABLE,RESPONSE_STATUS,STATUS from RRL_API_CALL_LOG where API_CALL_ID=:i',i=admin_call_id);assert q.fetchone()==(0,200,'DONE')
        q.execute('select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:o and STATE=\'APPLIED\'',o=op);assert q.fetchone()[0]==1
        q.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'");assert q.fetchone()[0]==0
    r=dict(status='PASS',call_id=call_id,request_id=request_id,admin_call_id=admin_call_id,changed_rejected=changed,events_unchanged=True,stock=p.qa.stock())
    assert tuple(r['stock'])==(0,0,0)
    (p.qa.ROOT/'runtime/test-evidence/tradecase/2026-10-26/T12/audit-replay-regression.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r))

if __name__=='__main__':main()
