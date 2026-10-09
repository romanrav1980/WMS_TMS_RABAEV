"""Wire measured shortage approval to existing posting boundary."""
import json
from pathlib import Path
from stock_posting_sql_json_binds import transform
D=Path("db/migrations/2026-10-08_stock_posting_core")
out={}
for name in ("020_reservations.sql","039_unit_core.sql","160_case_pick_command.sql"):
 s=(D/name).read_text(encoding="utf-8")
 s=s.replace("accessible by(package ", "accessible by(package RRL_STOCK_CASE_SHORT_CMD,package ",1)
 out[str(D/name)]=s
s=(D/"171_case_short_command.sql").read_text(encoding="utf-8")
out[str(D/"171_case_short_command.sql")]=transform(s)[0]
s=(D/"024_posting.sql").read_text(encoding="utf-8")
s=s.replace("elsif g_kind='CASE_CARRIER_MOVE'", "elsif g_kind='CASE_SHORT_APPROVE' then RRL_STOCK_CASE_SHORT_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n   elsif g_kind='CASE_CARRIER_MOVE'",1)
needle="elsif g_kind='CASE_CARRIER_MOVE' then RRL_STOCK_CASE_MOVE_CMD.execute_command"
assert needle in s
s=s.replace(needle,"elsif g_kind='CASE_SHORT_APPROVE' then RRL_STOCK_CASE_SHORT_CMD.execute_command(g_request,g_actor,p_result);\n  "+needle,1)
out[str(D/"024_posting.sql")]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_stock.py")
s=p.read_text(encoding="utf-8").replace('"CASE_PICK_CONFIRM",','"CASE_SHORT_APPROVE", "CASE_PICK_CONFIRM",')
# Literal set may use single quotes; fail rather than silently omitting handler.
if "CASE_SHORT_APPROVE" not in s:
 s=s.replace("'CASE_PICK_CONFIRM',","'CASE_SHORT_APPROVE', 'CASE_PICK_CONFIRM',")
assert "CASE_SHORT_APPROVE" in s
out[str(p)]=s
p=Path("api/wms_api_server/app/schemas.py");s=p.read_text(encoding="utf-8")
s=s.replace("class CasePickShortDecisionRequest(BaseModel):","class CasePickShortDecisionRequest(BaseModel):\n    operation_id: str | None = Field(default=None, min_length=1, max_length=100)",1);out[str(p)]=s
p=Path("api/wms_api_server/app/services/case_pick_service.py");s=p.read_text(encoding="utf-8")
s=s.replace("return CasePickService(bound)._short_line_locked(case_pick_task_id, line_id, request)","return CasePickService(bound)._short_line_locked(case_pick_task_id, line_id, request, approval_pending=True)")
s=s.replace("def _short_line_locked(self, case_pick_task_id: int, line_id: int, request: CasePickLineShortRequest)","def _short_line_locked(self, case_pick_task_id: int, line_id: int, request: CasePickLineShortRequest, approval_pending: bool = False)")
s=s.replace("set STATUS = 'SHORT_PICKED',\n                   PICKED_QTY = :picked_qty,","set STATUS = :line_status,\n                   PICKED_QTY = :picked_qty,")
s=s.replace('{"line_id": line_id, "picked_qty": picked_qty, "actor": actor},','{"line_id": line_id, "picked_qty": picked_qty, "actor": actor,\n                "line_status": "SHORT_PENDING_APPROVAL" if approval_pending else "SHORT_PICKED"},',1)
s=s.replace('        actor = request.actor or "SHIFT_LEAD"\n        rows = self.gateway.fetch_all(','''        from ..modules.inventory.public import post_existing_case_short_approval
        posted = post_existing_case_short_approval(self.gateway, short_id, request)
        if posted is not None:
            return posted
        actor = request.actor or "SHIFT_LEAD"
        rows = self.gateway.fetch_all(''',1)
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8")
s+='\n\ndef post_existing_case_short_approval(gateway, short_id: int, request):\n    from .infrastructure.case_short_commands import post_short_approval\n    return post_short_approval(gateway, short_id, request)\n'
out[str(p)]=s
m=json.loads((D/"current_runtime_manifest.json").read_text(encoding="utf-8"))
m["components"].insert(m["components"].index("024_posting.sql"),"171_case_short_command.sql")
m["packages"].append("RRL_STOCK_CASE_SHORT_CMD")
out[str(D/"current_runtime_manifest.json")]=json.dumps(m,indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
