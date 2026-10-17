"""Bounded read timings and slow-SQL review for the store application."""
import json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.delivery.infrastructure.store_app_reads import StoreAppReads

def main():
 g=OracleGateway();app=StoreAppReads(g);timings=[]
 for trial in range(2):
  started=time.perf_counter();session=app.session('admin');timings.append(dict(operation='session',trial=trial+1,ms=round((time.perf_counter()-started)*1000,2),stores=len(session['stores'])))
  own=next(row for row in session['stores']if row['address']=='Own full-pallet ST')
  started=time.perf_counter();page=app.deliveries('admin',own['store_id'],'',50);timings.append(dict(operation='deliveries',trial=trial+1,ms=round((time.perf_counter()-started)*1000,2),rows=len(page['items'])))
  started=time.perf_counter();app.preview('admin',own['store_id'],page['items'][0]['load_operation_id']);timings.append(dict(operation='native_preview',trial=trial+1,ms=round((time.perf_counter()-started)*1000,2)))
 slow=g.fetch_all("""select LOG_ID,to_char(CREATED_AT,'YYYY-MM-DD HH24:MI:SS') CREATED_AT,ELAPSED_MS,API_PATH,dbms_lob.substr(SQL_TEXT,500,1) SQL_SAMPLE
 from RRL_SQL_SLOW_LOG where CREATED_AT>=systimestamp-interval'1'hour order by CREATED_AT desc fetch first 12 rows only""")
 result=dict(status='REVIEWED',timings=timings,recent_slow=slow,decision='Keep destination predicates before limit and keyset pages <=200; no speculative index. Dictionary inspection is migration verification, not an interactive endpoint. Track repeated source/profile queries above 1000ms with plan and attribution before indexing; owner Codex.',stock_effect='NONE')
 (ROOT/'reports/retailcase/2026-10-15/store-app/slow-sql.json').write_text(json.dumps(result,indent=2,default=str),encoding='utf-8')
 print(json.dumps(dict(timings=timings,slow=[{key:row[key]for key in('log_id','elapsed_ms','api_path')}for row in slow])))
if __name__=='__main__':main()
