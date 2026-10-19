"""Repeat identical authorized reads; hashes detect changing results, not a production load test."""
import sys,os,json,hashlib,statistics
from pathlib import Path
sys.path[:0]=['.','tests/tradecase']
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
with oracle_connection()as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
paths=['/api/outgoing-quality/CP597000000001156','/api/tradecase/warehouses/215590763/stock/transit?load_operation_id=T7.LOAD.1156&limit=100','/api/tradecase/warehouses/215590763/buyouts/TC7.TRANSIT.1156','/api/tradecase/warehouses/211559882/stock?limit=100']
results=[]
for path in paths:
 hashes=[];times=[]
 for _ in range(6):
  r=expect(200,http('GET',path));hashes.append(hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest());times.append(CALLS[-1]['elapsed_ms'])
 assert len(set(hashes))==1,(path,hashes)
 results.append(dict(path=path,n=6,first_ms=times[0],warm_median_ms=statistics.median(times[1:]),max_ms=max(times),result_sha256=hashes[0],times_ms=times))
P=Path('runtime/test-evidence/tradecase/2026-10-19/T12');P.mkdir(parents=True,exist_ok=True);file=P/('reads-'+sys.argv[1]+'.json');file.write_text(json.dumps(dict(environment='local8088/OracleRABAEV, admin sequential reads, other UI reads possible',cache='existing warmed shared pool, no flush',results=results,http=CALLS),indent=2));print(json.dumps(results))
