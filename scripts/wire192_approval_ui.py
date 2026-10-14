from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/contracts_weighted_case.py");t=p.read_text(encoding="utf-8").replace("class WeightedCasePort(Protocol):","class WeightedCasePort(Protocol):\n    def short_weight_preview(self, short: int, actor: str) -> dict[str, Any]: ...");out[str(p)]=t
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/weighted_case_pick.py");t=p.read_text(encoding="utf-8")
a="    def weight_preview(self,"
insert='''    def short_weight_preview(self, short: int, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("CASE short approver weight source READ ONLY") as q:
                q.execute("set transaction read only")
                q.execute("select CASE_PICK_TASK_ID,CASE_PICK_LINE_ID from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:p_short", p_short=short)
                row = q.fetchone()
                if row is None:
                    raise StockPostingError("ORDER_WEIGHT_SHORT_NOT_FOUND", None, 20886)
                q.callproc("RRL_CASE_TASK_ACCESS.assert_scope", [int(row[0]), actor, "case_pick_short_approve"])
                return read_oracle_json(q.callfunc("RRL_ORDER_WEIGHT_READ.snapshot_json", oracledb.DB_TYPE_CLOB, [int(row[0]), int(row[1]), actor]))
        except oracledb.DatabaseError as exc:
            code = exc.args[0].code
            if code in {20882, 20886, 20881, 1403, 1422}:
                raise StockPostingError("ORDER_WEIGHT_PREVIEW_REJECTED", None, code) from exc
            raise

'''
assert t.count(a)==1;out[str(p)]=t.replace(a,insert+a)
p=Path("api/wms_api_server/app/modules/inventory/api/weighted_case_routes.py");t=p.read_text(encoding="utf-8");t+='''

@router.get("/shorts/{short}/weight-preview")
def short_weight_preview(short: int,
                         user: AdminUser = Depends(require_permission("case_pick_short_approve")),
                         service: WeightedCasePort = Depends(weighted_case_service)) -> dict:
    return service.short_weight_preview(short, user.username)
''';out[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/case-pick-management.js");t=p.read_text(encoding="utf-8")
a='<button id="caseAcceptShort" type="button">Принять недобор</button>';assert a in t
t=t.replace(a,a+'<button id="caseAcceptWeight" type="button">Завершить по допуску массы</button>')
a='  document.getElementById("caseAcceptShort")?.addEventListener("click", () => caseSafe(() => approveSelectedShort(task, "ACCEPT_SHORT")));'
t=t.replace(a,a+'\n  document.getElementById("caseAcceptWeight")?.addEventListener("click", () => caseSafe(() => approveSelectedShort(task, "WEIGHT_TOLERANCE")));')
a='  if (body.decision !== decision) throw new Error("Сначала повторите сохранённое решение: " + body.decision);'
t=t.replace(a,a+'''
  if (!saved && decision === "WEIGHT_TOLERANCE") {
    const preview = await caseFetch("/api/case-pick/shorts/" + short.case_pick_short_id + "/weight-preview");
    if (!preview.within_tolerance) throw new Error("Масса заказа вне допуска: " + preview.picked_quantity + " из " + preview.requested_quantity + " KG.");
    const reason = prompt("Заказ: " + preview.requested_quantity + " KG; факт: " + preview.picked_quantity +
      " KG; допуск: " + preview.tolerance_pct + "%. Основание завершения:");
    if (reason === null) return;
    if (reason.trim().length < 3) throw new Error("Укажите основание завершения.");
    body.reason_text = reason.trim();
    body.expected_weight_policy_version = preview.policy_version;
    body.expected_content_version = preview.content_version;
    body.expected_order_weight_signature = preview.order_weight_signature;
  }
''')
out[str(p)]=t
print(json.dumps(out,ensure_ascii=True))
