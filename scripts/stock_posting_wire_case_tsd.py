"""Use existing CASE TSD page with real scans and durable posting."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];files={}
def edit(path,old,new):
 text=files.get(path,(ROOT/path).read_text(encoding="utf-8"))
 if text.count(old)!=1:raise RuntimeError("Missing unique anchor "+path+" "+old[:35])
 files[path]=text.replace(old,new,1)
path="api/wms_api_server/app/modules/inventory/public.py"
files[path]=(ROOT/path).read_text(encoding="utf-8")+"""

def existing_case_pick_policy(gateway, task_id: int, line_id: int):
    from .infrastructure.case_pick_policy import case_pick_policy
    return case_pick_policy(gateway, task_id, line_id)
"""
path="api/wms_api_server/app/routers/case_pick.py"
edit(path,'@router.post("/tasks/{case_pick_task_id}/lines/{line_id}/confirm")',
"""@router.get("/tasks/{case_pick_task_id}/lines/{line_id}/marking-policy")
def case_line_marking_policy(case_pick_task_id: int, line_id: int,
    user: AdminUser = Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION))) -> dict:
    from ..modules.inventory.public import existing_case_pick_policy
    from ..oracle_gateway import OracleGateway
    try:
        return existing_case_pick_policy(OracleGateway(), case_pick_task_id, line_id)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


@router.post("/tasks/{case_pick_task_id}/lines/{line_id}/confirm")""")
path="wiki-raw/wms_admin_ui_reference/case-pick-tsd.html"
edit(path,'<label>Товар / ШК<input id="cpTsdScanProduct"',
 '<label>Идентификатор паллеты отбора<input id="cpTsdScanContainer" autocomplete="off" /></label>\n          <label>Товар / ШК<input id="cpTsdScanProduct"')
edit(path,'<section class="tsd-actions" data-permission="case_pick_execute">',
"""<section id="cpTsdMarking" hidden><label>Профиль маркировки<select id="cpTsdMarkProfile"></select></label><label>Уникальные коды фактически взятых единиц, по одному на строку<textarea id="cpTsdUnitCodes" rows="4" autocomplete="off"></textarea></label></section>
        <section class="tsd-actions" data-permission="case_pick_execute">""")
edit(path,'<button id="cpTsdShort" class="danger"',
 '<button id="cpTsdRetryPosting" type="button" hidden>Повторить незавершённую команду</button>\n          <button id="cpTsdShort" class="danger"')
edit(path,'<script src="case-pick-tsd.js"></script>','<script src="case-pick-tsd.js"></script>\n    <script src="case-pick-posting.js"></script>')
path="wiki-raw/wms_admin_ui_reference/case-pick-tsd.js"
text=(ROOT/path).read_text(encoding="utf-8")
old='    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));'
if old not in text:
 start=text.index("  if (!response.ok)");raise RuntimeError("Fetch error anchor")
files[path]=text.replace(old,'''    const error = new Error(typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail || body));
    error.detail = body.detail;error.status = response.status;throw error;''',1)
edit(path,'const picked = Number(cpTsdEl("cpTsdFactQty").value || 0);',
 'const picked = cpTsdEl("cpTsdFactQty").value || "0";')
print(json.dumps(files,ensure_ascii=True))
