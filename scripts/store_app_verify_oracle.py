"""Compare live package bodies with the final migration chain; no schema or business writes."""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway

LATEST={
 'RRL_STOCK_WAVE_CMD':'2026-10-15_wave_launch_continuation/wave_sources.sql',
 'RRL_WAVE_CONTINUE_API':'2026-10-15_wave_launch_continuation/continuation_api.sql',
 'RRL_STOCK_POSTING_API':'2026-10-15_wave_launch_continuation/posting.sql',
 'RRL_STOCK_STORE_RECEIPT_READ':'2026-10-15_store_app_final_leg/body.sql',
 'RRL_STOCK_STORE_RECEIPT_CMD':'2026-10-15_scoped_command_lock_order/rrl_stock_store_receipt_cmd.sql',
 'RRL_STOCK_STORE_WEIGHT_CORE':'2026-10-15_store_app_strategies/rrl_stock_store_weight_core.sql',
 'RRL_WAVE_EXEC_ACCESS':'2026-10-15_wave_launch_continuation/wave_access.sql',
 'RRL_STOCK_WAVE_LAUNCH_CMD':'2026-10-15_wave_launch_scope/rrl_stock_wave_launch_cmd.sql',
 'RRL_WAREHOUSE_TASK_ACCESS':'2026-10-15_warehouse_task_scoped_complete/access_body.sql',
 'RRL_TASK_RESOURCE_POLICY':'2026-10-15_warehouse_task_scoped_complete/resource_policy.sql',
 'RRL_STOCK_TASK_CORE':'2026-10-15_warehouse_task_scoped_complete/task_core.sql',
 'RRL_STOCK_TASK_PLAN':'2026-10-15_warehouse_task_scoped_complete/task_plan.sql'}
SPECS={
 'RRL_WAVE_CONTINUE_API':'2026-10-15_wave_launch_continuation/continuation_api.sql',
 'RRL_WAREHOUSE_TASK_ACCESS':'2026-10-15_warehouse_task_scoped_complete/access_spec.sql',
 'RRL_STOCK_TASK_PLAN':'2026-10-15_warehouse_task_scoped_complete/task_plan_spec.sql'}


def normalized(value):
 value=re.sub(r'^create\s+or\s+replace\s+','',value.replace('\r','').strip(),flags=re.I)
 return value[:-1].strip()if value.endswith('/')else value


def main():
 g=OracleGateway();checks=[]
 for name,kind,path in [(name,'PACKAGE BODY',path)for name,path in LATEST.items()]+[(name,'PACKAGE',path)for name,path in SPECS.items()]:
  actual=normalized(''.join(r['text']for r in g.fetch_all("select TEXT from USER_SOURCE where NAME=:name and TYPE=:kind order by LINE",{'name':name,'kind':kind})))
  source=(ROOT/'db/migrations'/path).read_text(encoding='utf-8-sig')
  if name=='RRL_WAVE_CONTINUE_API':source=source.split('\n/\n')[1 if kind=='PACKAGE BODY'else 0]
  expected=normalized(source)
  assert actual==expected,name
  assert not g.fetch_all('select LINE,TEXT from USER_ERRORS where NAME=:name',{'name':name}),name
  checks.append(dict(package=name,kind=kind,source_matches=path,sha256=hashlib.sha256(actual.encode()).hexdigest()))
 invalid=g.fetch_all("select count(*) N from USER_OBJECTS where STATUS='INVALID'")[0]['n'];assert invalid==0
 constraint=g.fetch_all("select STATUS,SEARCH_CONDITION_VC from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_STORE_RECEIPT_MODE_CK'")[0]
 assert constraint['status']=='ENABLED'and 'PAPER_COUNT'in constraint['search_condition_vc']
 result=dict(status='PASS',source_checks=checks,invalid_count=invalid,three_mode_constraint=constraint)
 target=ROOT/'reports/retailcase/2026-10-15/store-app';target.mkdir(exist_ok=True)
 (target/'oracle-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(json.dumps(dict(status='PASS',source_matches=len(checks),invalid_count=invalid,three_mode_constraint=constraint['status'])))
if __name__=='__main__':main()
