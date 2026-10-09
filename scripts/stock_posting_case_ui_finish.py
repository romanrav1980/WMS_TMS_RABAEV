import json
from pathlib import Path
out={}
for filename,other in (("case-pick-posting.js","nicora.caseCarrierMove"),("case-carrier-move.js","nicora.casePickIntent")):
 p=Path("wiki-raw/wms_admin_ui_reference")/filename;s=p.read_text(encoding="utf-8")
 if filename=="case-pick-posting.js":
  s=s.replace("if (busy) return;","if (busy || window.cpTsdStockBusy) return;")
  s=s.replace("busy = true;","busy = true;window.cpTsdStockBusy = true;",1)
  s=s.replace("storageKey = key();","storageKey = key();\n      if(localStorage.getItem(JSON.stringify(['"+other+"',cpTsdApiBase(),cpTsdUser()])))throw new Error('Сначала повторите сохранённое перемещение паллеты.');",1)
  s=s.replace('cpTsdSetState(error.message+" Неизвестный исход: повторяйте сохранённую команду.");','let unresolved = false;\n      try { unresolved = !!(storageKey && localStorage.getItem(storageKey)); } catch (_) {}\n      cpTsdSetState(error.message + (unresolved ? " Исход не подтверждён: повторите сохранённую команду." : ""));')
  s=s.replace("busy=false;","busy=false;window.cpTsdStockBusy=false;",1)
 else:
  s=s.replace("if(busy)return;busy=true;","if(busy||window.cpTsdStockBusy)return;busy=true;window.cpTsdStockBusy=true;",1)
  s=s.replace("storageKey=key();","storageKey=key();\n      if(localStorage.getItem(JSON.stringify(['"+other+"',cpTsdApiBase(),cpTsdUser()])))throw new Error('Сначала повторите сохранённый отбор товара.');",1)
  s=s.replace("finally{busy=false;","finally{busy=false;window.cpTsdStockBusy=false;",1)
 out[str(p)]=s
p=Path("api/wms_api_server/app/services/case_pick_service.py");s=p.read_text(encoding="utf-8")
needle='            return CasePickService(bound)._short_line_locked(case_pick_task_id, line_id, request, approval_pending=True)'
replacement='''            existing = bound.fetch_all("select OFFLINE_EVENT_ID from RRL_CASE_PICK_SHORT where CASE_PICK_LINE_ID=:id and STATUS in ('CREATED','PENDING_APPROVAL')", {"id": line_id})
            if existing and (not request.offline_event_id or existing[0]["offline_event_id"] != request.offline_event_id):
                raise HTTPException(409, detail="A shortage already awaits approval for this line")
'''+needle
assert needle in s;s=s.replace(needle,replacement,1)
needle='    def reject_short(self, short_id: int, request: CasePickShortDecisionRequest) -> dict[str, str]:'
replacement=needle+'''
        from ..modules.inventory.public import warehouse_metadata_transaction
        from ..transaction_gateway import TransactionGateway
        state = self.gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
        if state and state[0]["state"] == "PREPARED":
            return self._reject_short_locked(short_id, request)
        with warehouse_metadata_transaction(self.gateway, "CASE shortage rejection", request.actor, "case_pick_short_approve") as cursor:
            bound = TransactionGateway(cursor)
            rows = bound.fetch_all("select STATUS from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:id for update", {"id": short_id})
            if not rows:
                raise HTTPException(404, detail="Shortage not found")
            if rows[0]["status"] == "REJECTED":
                return {"status": "REJECTED"}
            if rows[0]["status"] not in ("CREATED", "PENDING_APPROVAL"):
                raise HTTPException(409, detail="The shortage has already been accepted")
            return CasePickService(bound)._reject_short_locked(short_id, request)

    def _reject_short_locked(self, short_id: int, request: CasePickShortDecisionRequest) -> dict[str, str]:'''
assert needle in s;s=s.replace(needle,replacement,1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
