"""Independent read-only comparison of pre-C0169 and released SQL, plus actual HTTP before/after restart."""
import sys,os,json,time,statistics,subprocess,hashlib
from pathlib import Path
sys.path[:0]=['scripts','api/wms_api_server','tests/tradecase','.']
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.services.warehouse_service import WarehouseService
from app.oracle_gateway import OracleGateway
from live_document_acceptance import http,expect
os.environ.setdefault('TRADECASE_ADMIN_USER','admin');os.environ.setdefault('TRADECASE_ADMIN_PASSWORD','admin123')
OUT=Path('runtime/test-evidence/tradecase/2026-10-23/T12/warehouse-selectors')
old_source=subprocess.check_output(['git','show','3c2ad441:api/wms_api_server/app/services/warehouse_service.py']).decode('utf-8')
ns=dict(__name__='app.services._before_C0169',__package__='app.services');exec(compile(old_source,'historical-warehouse-service','exec'),ns)
class Capture:
 def fetch_all(self,sql,params):return sql,params
cases=dict(all500=dict(limit=500),default200={},small5=dict(limit=5),role=dict(role='FINISHED_GOODS',limit=500),mes1=dict(mes_enabled=1,limit=500),mes0=dict(mes_enabled=0,limit=500))
def canonical(v):return json.dumps(v,sort_keys=True,default=str)
if sys.argv[1]=='sql':
 report=dict(status='FAIL',cases={},baseline_commit='3c2ad441',samples_per_variant=5)
 gateway=OracleGateway()
 for name,args in cases.items():
  queries={k:cls(Capture()).list_warehouses(**args)for k,cls in [('before',ns['WarehouseService']),('candidate',WarehouseService)]}
  results={};timings={}
  for k,(sql,params)in queries.items():
   times=[];rows=[]
   for _ in range(5):
    start=time.perf_counter();result=gateway.fetch_all(sql,params);times.append(round((time.perf_counter()-start)*1000,2));rows.append(result)
   assert all(canonical(r)==canonical(rows[0])for r in rows),name
   results[k]=rows[0];timings[k]=dict(first_ms=times[0],warm_ms=times[1:],warm_median_ms=statistics.median(times[1:]))
  assert canonical(results['before'])==canonical(results['candidate']),name
  report['cases'][name]=dict(rows=len(results['before']),equal_in_order=True,result_hash=hashlib.sha256(canonical(results['before']).encode()).hexdigest(),timings=timings)
 report['status']='PASS';(OUT/'sql-comparison.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
else:
 from urllib.parse import urlencode
 report=dict(status='FAIL',cases={})
 for name,args in cases.items():
  path='/api/admin/warehouses?'+urlencode(args);times=[];rows=[]
  for _ in range(4):
   start=time.perf_counter();rows.append(expect(200,http('GET',path)));times.append(round((time.perf_counter()-start)*1000,2))
  assert all(canonical(r)==canonical(rows[0])for r in rows),name
  report['cases'][name]=dict(rows=len(rows[0]),first_ms=times[0],warm_ms=times[1:],warm_median_ms=statistics.median(times[1:]),result_hash=hashlib.sha256(canonical(rows[0]).encode()).hexdigest())
 report['status']='PASS';(OUT/(sys.argv[1]+'.json')).write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
