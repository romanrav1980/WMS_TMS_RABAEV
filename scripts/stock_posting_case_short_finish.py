import json
from pathlib import Path
D=Path("db/migrations/2026-10-08_stock_posting_core");out={}
p=D/"171_case_short_command.sql";s=p.read_text(encoding="utf-8")
s=s.replace("or l.STATUS!='SHORT_PENDING_APPROVAL'","or l.STATUS is null or l.STATUS!='PARTIAL'")
out[str(p)]=s
p=D/"160_case_pick_command.sql";s=p.read_text(encoding="utf-8").replace("'NEW','IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT'","'NEW','ACTIVE','SKIPPED','IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT'")
out[str(p)]=s
p=Path("api/wms_api_server/app/services/case_pick_service.py");s=p.read_text(encoding="utf-8")
s=s.replace('"line_status": "SHORT_PENDING_APPROVAL" if approval_pending else "SHORT_PICKED"','"line_status": "PARTIAL" if approval_pending else "SHORT_PICKED"')
old='    def close_task(self, case_pick_task_id: int, request: CasePickTaskActionRequest) -> dict[str, Any]:'
new=old+'''
        from ..modules.inventory.public import warehouse_metadata_transaction
        from ..transaction_gateway import TransactionGateway
        state = self.gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
        if state and state[0]["state"] == "PREPARED":
            return self._close_task_locked(case_pick_task_id, request)
        with warehouse_metadata_transaction(self.gateway, "CASE carrier close", request.actor, "case_pick_execute") as cursor:
            bound = TransactionGateway(cursor)
            bound.fetch_all("select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id for update", {"id": case_pick_task_id})
            pending = bound.fetch_all("select 1 from RRL_CASE_PICK_SHORT where CASE_PICK_TASK_ID=:id and STATUS in ('CREATED','PENDING_APPROVAL') and rownum=1", {"id": case_pick_task_id})
            if pending:
                raise HTTPException(409, detail="Approve or reject the pending shortage before closing the carrier")
            return CasePickService(bound)._close_task_locked(case_pick_task_id, request)

    def _close_task_locked(self, case_pick_task_id: int, request: CasePickTaskActionRequest) -> dict[str, Any]:'''
assert old in s;s=s.replace(old,new,1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
