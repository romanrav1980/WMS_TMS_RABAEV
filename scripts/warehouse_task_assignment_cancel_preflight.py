"""Preflight canonical zero-fact task cancellation in caller-owned rollback."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from warehouse_task_assignment_native import RUNTIME,REPORT,state
from warehouse_task_scoped_complete_smoke import RollbackTrial
from app.oracle_gateway import OracleGateway
from app.transaction_gateway import TransactionGateway
from app.services.warehouse_task_service import WarehouseTaskService
from app.schemas import WarehouseTaskStatusRequest


def run():
 g=OracleGateway();ctx=json.loads(RUNTIME.read_text());before=state(g,ctx)
 assert all((r['fact_qty']or 0)==0 for r in before['tasks'])
 for task in(ctx['task'],ctx['mixed_task']):
  try:
   with g.transaction('Canonical owned TASK cancel preflight rollback')as c:
    try:
     c.callproc('RRL_STOCK_METADATA_TX.begin_change',['admin','warehouse_task_edit'])
     c.execute('select TASK_ID from RRL_WAREHOUSE_TASK where TASK_ID=:id for update',id=task)
     WarehouseTaskService(TransactionGateway(c)).cancel_task(task,WarehouseTaskStatusRequest(updated_by='admin',reason='Preflight owned metadata-only fixture cancellation; no physical facts'))
     c.execute('select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:id',id=task);assert c.fetchone()[0]=='CANCELLED'
    finally:c.callproc('RRL_STOCK_METADATA_TX.end_change')
    raise RollbackTrial()
  except RollbackTrial:pass
  assert state(g,ctx)==before
 (REPORT/'cleanup-preflight.json').write_text(json.dumps(dict(status='PASS',tasks=[ctx['task'],ctx['mixed_task']],canonical_cancellation='CALLER_ROLLBACK',before=before,after=state(g,ctx),goods_commit=False),indent=2,default=str),encoding='utf-8');print('TASK_CANONICAL_CANCEL_PREFLIGHT_2_PASS')


if __name__=='__main__':run()
