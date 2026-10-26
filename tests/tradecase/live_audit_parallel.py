"""Read-only 5 sequential / 8 concurrent real requests and verify both audit journals remain complete."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json,os,re,statistics,sys
from pathlib import Path
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).parent))
import live_shipment_events as p

def main():
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[\x60,)\s]',(p.qa.ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    marker='TC26.AUDIT.'+uuid4().hex[:10]
    path=f"/api/tradecase/warehouses/{p.s['fixture']['warehouse_id']}/trips/T60/coverage?qa_batch="+marker
    responses=[p.qa.expect(200,p.qa.http('GET',path))for _ in range(5)]
    with ThreadPoolExecutor(max_workers=8)as pool:responses+=list(pool.map(lambda _:p.qa.expect(200,p.qa.http('GET',path)),range(8)))
    baseline=json.loads((p.qa.ROOT/'runtime/test-evidence/tradecase/2026-10-26/T12/coverage-http-concurrency.json').read_text())
    assert all(response==baseline['response']for response in responses)
    with p.qa.oracle_connection()as c:
        q=c.cursor();q.execute("select API_CALL_ID,REQUEST_ID,STATUS,RESPONSE_STATUS,LOCAL_LOG_PATH from RRL_API_CALL_LOG where QUERY_STRING=:query order by API_CALL_ID",query='qa_batch='+marker);rows=q.fetchall()
        assert len(rows)==13 and all(row[2:4]==('DONE',200)for row in rows),rows
        request_ids={row[1]for row in rows};assert len(request_ids)==13
    local=[]
    for name in {row[4]for row in rows}:
        file=Path(name).resolve();file.relative_to(p.qa.ROOT)
        for line in file.read_text(encoding='utf-8').splitlines():
            value=json.loads(line)
            if value.get('request_id')in request_ids:local.append(value)
    assert len(local)==26
    for call_id,request_id,_,_,_ in rows:
        pair=[value for value in local if value['request_id']==request_id]
        assert {value['phase']for value in pair}=={'STARTED','FINISHED'}
        finish=next(value for value in pair if value['phase']=='FINISHED');assert finish['api_call_id']==call_id and finish['response_status']==200
    values=[call['elapsed_ms']for call in p.qa.CALLS]
    r=dict(status='PASS',query_marker=marker,response_hash=sha256(json.dumps(responses[0],sort_keys=True).encode()).hexdigest(),http=p.qa.CALLS,audit_rows=[list(row)for row in rows],local_records=len(local),sequential_ms=values[:5],parallel_ms=values[5:])
    (p.qa.ROOT/'runtime/test-evidence/tradecase/2026-10-26/T12/audit-threadpool-after.json').write_text(json.dumps(r,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status=r['status'],sequential_ms=values[:5],parallel_ms=values[5:],parallel_median_ms=statistics.median(values[5:]),oracle_records=len(rows),local_records=len(local))))

if __name__=='__main__':main()
