import sys,json
from pathlib import Path
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from warehouse_task_assignment_native import RUNTIME,REPORT,state,intent
from warehouse_task_scoped_complete_smoke import RollbackTrial
from app.oracle_gateway import OracleGateway
g=OracleGateway();ctx=json.loads(RUNTIME.read_text());before=state(g,ctx);checks=[]
for sql,bind,message in [
 ('delete from RRL_WTASK_RESOURCE_COMMAND where OPERATION_ID=:op',{'op':ctx['assign_body']['operation_id']},'WTASK_COMMAND_APPEND_ONLY'),
 ('update RRL_WTASK_RESOURCE_COMMAND set TARGET_ID=TARGET_ID where OPERATION_ID=:op',{'op':ctx['assign_body']['operation_id']},'WTASK_COMMAND_APPEND_ONLY'),
 ('delete from RRL_WTASK_ASSIGN_VERSION where TASK_ID=:id',{'id':ctx['task']},'WTASK_VERSION_SERVER_DERIVED'),
 ('begin RRL_WTASK_VERSION_API.derive(:id,false);end;',{'id':ctx['task']},'PLS-00904'),
 ("begin dbms_session.set_context('RRL_WTASK_ASSIGN_CTX','TX_ID','FORGED');end;",{},'ORA-01031')]:
 try:
  with g.transaction('Native TASK history/capability guard caller rollback')as c:
   try:c.execute(sql,bind)
   except oracledb.DatabaseError as e:assert message in str(e),(message,str(e))
   else:raise AssertionError('Native capability/history guard bypassed')
   raise RollbackTrial()
 except RollbackTrial:pass
 assert state(g,ctx)==before;checks.append(message)
(REPORT/'history-capability-guards.json').write_text(json.dumps(dict(status='PASS',checks=checks,task_receipt_version_stock_unchanged=True,goods_commit=False),indent=2),encoding='utf-8');print('NATIVE_HISTORY_AND_TRUSTED_CAPABILITY_5_PASS')
