import sys,json
from pathlib import Path
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from warehouse_task_assignment_native import RUNTIME,REPORT,state,intent
from warehouse_task_scoped_complete_smoke import RollbackTrial
from app.oracle_gateway import OracleGateway
import httpx
g=OracleGateway();ctx=json.loads(RUNTIME.read_text());cases={
 'HU':g.fetch_all('select TASK_ID from RRL_WAREHOUSE_TASK where HU_CONTENT_VERSION is not null order by TASK_ID desc fetch first 1 rows only'),
 'MES':g.fetch_all("select TASK_ID from RRL_WAREHOUSE_TASK where TASK_SOURCE='MES_RAW_SUPPLY'order by TASK_ID desc fetch first 1 rows only"),
 'CASE':g.fetch_all('select TASK_ID from RRL_ST_DEFER_WAIT_PLAN where CASE_TASK_ID is not null order by TASK_ID desc fetch first 1 rows only')}
results=[]
with httpx.Client(base_url='http://127.0.0.1:8088',auth=('admin','admin123'),timeout=25)as client:
 for kind,rows in cases.items():
  assert rows,(kind,'Missing live negative source')
  task=rows[0]['task_id'];body=intent(g,ctx,'ASSIGN',task);body['target']='admin';before=g.fetch_all('select STATUS,ASSIGNED_TO,RESOURCE_ID,RESOURCE_SESSION_ID from RRL_WAREHOUSE_TASK where TASK_ID=:id',{'id':task})
  response=client.post('/api/warehouse-tasks/'+str(task)+'/resource-commands',json=body)
  assert response.status_code==403 and 'WTASK_CURRENT_SCOPED_AUTHORITY_REQUIRED'in response.text,(kind,response.status_code,response.text[:500])
  assert g.fetch_all('select STATUS,ASSIGNED_TO,RESOURCE_ID,RESOURCE_SESSION_ID from RRL_WAREHOUSE_TASK where TASK_ID=:id',{'id':task})==before
  assert not g.fetch_all('select OPERATION_ID from RRL_WTASK_RESOURCE_COMMAND where OPERATION_ID=:op',{'op':body['operation_id']})
  results.append(dict(kind=kind,task_id=task,status=403,source_unchanged=True,receipt_created=False))
(REPORT/'unsupported-contexts.json').write_text(json.dumps(dict(status='PASS',checks=results,admin_rights_do_not_override_ordinary_path=True,goods_commit=False),indent=2),encoding='utf-8');print('ACTUAL_HTTP_HU_MES_CASE_NEW_PATH_DENIED_3_PASS')
