from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-11_ni072_review/002_api.sql");s=p.read_text(encoding="utf-8")
s=s.replace("if material.get_number('warehouse_id')!=v_ware","if material.get_number('warehouse_id')is null or material.get_string('business_date')is null or material.get_string('timezone_region')is null or material.get_boolean('consistent_snapshot')is null or material.get_boolean('day_closed')is null then raise_application_error(-20886,'DAY_REVIEW_CAPTURE_FIELDS_REQUIRED');end if;\n  if material.get_number('warehouse_id')!=v_ware")
s=s.replace("r.put('report',material);p_result",'''r.put('captured_at_utc',to_char(sys_extract_utc(p_captured),'YYYY-MM-DD"T"HH24:MI:SS.FF6"Z"'));r.put('report',material);p_result''')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/day-review.js");s=p.read_text(encoding="utf-8")
s=s.replace("el('drReviewSave').disabled=!context||!!value;}","el('drReviewSave').disabled=!context||!!value;el('drReviewPending').textContent=value?'Сохранена команда '+value.operation_id+' для склада '+value.warehouse_id+', даты '+value.business_date+', пояса '+value.timezone_region+'. Повтор относится к этим данным.':'';}")
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.html");s=p.read_text(encoding="utf-8").replace('<p id="drReviewMessage"','<p id="drReviewPending" role="status"></p><p id="drReviewMessage"',1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
