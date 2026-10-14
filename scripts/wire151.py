from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/resources/infrastructure/workload_history.py");text=p.read_text(encoding="utf-8")
text=text.replace("connect by nocycle prior parent.PLAN_OPERATION_ID=a.PLAN_OPERATION_ID","connect by nocycle prior parent.PLAN_OPERATION_ID=a.PLAN_OPERATION_ID and a.WARE_ID=:ware and level<=:count")
needle='            selected=rows[:limit]'
text=text.replace(needle,'''            if any(rows[i]["replaced_plan_operation_id"]!=rows[i+1]["plan_operation_id"]for i in range(len(rows)-1)):
                raise WorkloadError("WORKLOAD_HISTORY_LINK_MISSING","Нарушена связь истории")
            if len(rows)<=limit and rows[-1]["replaced_plan_operation_id"]is not None:
                raise WorkloadError("WORKLOAD_HISTORY_LINK_MISSING","Предыдущая запись этого склада отсутствует")
'''+needle)
out[str(p)]=text
p=Path("wiki-raw/wms_admin_ui_reference/resource-workload.html");text=p.read_text(encoding="utf-8")
needle='<div id="rwAttendance"></div>'
assert text.count(needle)==1
out[str(p)]=text.replace(needle,needle+'<h3>История выбранного выхода</h3><p>Плановые интервалы и их утверждение; фактическая явка ведётся отдельно.</p><div id="rwHistory"></div>')
p=Path("wiki-raw/wms_admin_ui_reference/resource-workload.js");text=p.read_text(encoding="utf-8")
text=text.replace('let sequence = 0,','let historySequence = 0;\n  let sequence = 0,',1)
text=text.replace('function reset() { clearReplacement(); ++sequence;','function reset() { clearReplacement(); ++historySequence; ++sequence;',1)
text=text.replace('["rwResult", "rwWindows", "rwNormRows", "rwAttendance", "rwPerson"]','["rwResult", "rwWindows", "rwNormRows", "rwAttendance", "rwPerson", "rwHistory"]',1)
needle='      el("rwAttendance").appendChild(block);'
assert text.count(needle)==1
text=text.replace(needle,'''      const history = document.createElement("button"); history.textContent = "Показать историю";
      history.addEventListener("click", () => showHistory(row.plan_operation_id));
      block.appendChild(history);
'''+needle)
needle='  async function refresh() {'
text=text.replace(needle,'''  async function showHistory(plan, append = false, continuation = null) {
    const serial = ++historySequence, selected = scope();
    if (!append) el("rwHistory").replaceChildren();
    if (continuation) continuation.disabled = true;
    try {
      const result = await request("/api/resources/workload/warehouses/" + ware() + "/attendance/" + encodeURIComponent(plan) + "/history?limit=20");
      if (serial !== historySequence || selected !== scope()) return;
      if (continuation) continuation.remove();
      result.rows.forEach(row => {
        const block = document.createElement("div");
        text(block, row.person_id + " · " + row.site_code + " · " + row.start_at + " — " + row.finish_at);
        text(block, "Утверждён " + row.planned_by + " · " + row.recorded_at + " · основание: " + row.reason);
        if (row.cancel_operation_id) text(block, "Прежний план отменён " + row.cancelled_by + " · " + row.cancel_recorded_at + " · " + row.cancel_reason);
        el("rwHistory").appendChild(block);
      });
      if (result.has_more) {
        const more = document.createElement("button"); more.textContent = "Предыдущие изменения";
        more.addEventListener("click", () => showHistory(result.next_plan_operation_id, true, more));
        el("rwHistory").appendChild(more);
      }
      message("История плановых изменений прочитана; фактическая явка не изменена.");
    } catch (error) {
      if (serial === historySequence && selected === scope()) {message(error.message); if (continuation) continuation.disabled = false;}
    }
  }
'''+needle)
out[str(p)]=text
print(json.dumps(out,ensure_ascii=True))
