from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/case_pick_policy.py");t=p.read_text(encoding="utf-8")
t=t.replace("select l.ARTICUL,nvl(",'''select l.ARTICUL,
          case when exists(select 1 from RRL_ARTICULS a where a.ACTICUL=l.ARTICUL and a.TYPE_W in(2,3,5,6,7))
            and exists(select 1 from RRL_STOCK_UOM_CONVERSION c where c.ARTICUL=l.ARTICUL and c.INPUT_UOM='KG'and c.BASE_UOM='KG'and c.NUMERATOR=1 and c.DENOMINATOR=1)then 1 else 0 end WEIGHTED_KG,
          nvl(''',1)
t=t.replace('"serialized_weight_boxes": bool(rows[0]["serialized_weight_boxes"])}','"serialized_weight_boxes": bool(rows[0]["serialized_weight_boxes"]),\n            "loose_weight_kg": bool(rows[0]["weighted_kg"]) and not bool(rows[0]["marking_required"]) and not bool(rows[0]["serialized_weight_boxes"])}')
out[str(p)]=t
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py");t=p.read_text(encoding="utf-8")
t=t.replace('select RESULT_JSON from RRL_WH_SCALE_CAPTURE\n                    where CASE_PICK_TASK_ID=:p_task and CASE_PICK_LINE_ID=:p_line\n                    order by RECEIVED_AT desc,CAPTURE_KEY desc', 'select c.RESULT_JSON,c.CAPTURE_KEY,u.STOCK_OPERATION_ID from RRL_WH_SCALE_CAPTURE c\n                    left join RRL_WH_SCALE_USE u on u.CAPTURE_KEY=c.CAPTURE_KEY\n                    where c.CASE_PICK_TASK_ID=:p_task and c.CASE_PICK_LINE_ID=:p_line\n                    order by c.RECEIVED_AT desc,c.CAPTURE_KEY desc')
t=t.replace('"has_older": len(rows) > 50}', '"has_older": len(rows) > 50,\n                        "use_by_capture": {row[1]: {"operation_id": row[2]} for row in rows[:50] if row[2] is not None}}')
out[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/case-weighted-box.js");t=p.read_text(encoding="utf-8")
t=t.replace('panel.hidden = !policy.serialized_weight_boxes;','panel.hidden = !policy.serialized_weight_boxes && !policy.loose_weight_kg;')
t=t.replace('if (!policy.serialized_weight_boxes) return;','if (panel.hidden) return;')
t=t.replace('note.textContent = "Отсканируйте', 'note.textContent = policy.serialized_weight_boxes ? "Отсканируйте')
t=t.replace('по её массе нетто.";','по её массе нетто." : "Для товара на развес выберите архивное нетто-показание. Количество рассчитает система.";')
t=t.replace('    label.appendChild(select); panel.appendChild(label);','    select.addEventListener("change", () => { fact.disabled = Boolean(policy.serialized_weight_boxes || select.value); });\n    label.appendChild(select); panel.appendChild(label);')
t=t.replace('        for (const item of data.items) select.appendChild(new Option(','        for (const item of data.items) {\n          if (data.use_by_capture?.[item.capture_key] || item.basis !== (policy.serialized_weight_boxes ? "GROSS" : "NET")) continue;\n          select.appendChild(new Option(')
t=t.replace('          item.capture_key));','          item.capture_key));\n        }')
t=t.replace('  return { show, payload };','''  function selectedScale() { return panel?.querySelector("select[data-scale]")?.value || ""; }
  function netPayload(operation, cell, container) {
    const capture = selectedScale();
    if (!capture) throw new Error("Выберите нетто-показание весового поста.");
    return {operation_id: operation, warehouse_scale_capture: capture, scan_cell: cell, scan_container: container};
  }
  return { show, payload, selectedScale, netPayload };''')
out[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/case-pick-posting.js");t=p.read_text(encoding="utf-8")
t=t.replace('        const weighted = Boolean(currentPolicy.serialized_weight_boxes);','        const weighted = Boolean(currentPolicy.serialized_weight_boxes);\n        const weighed = Boolean(currentPolicy.loose_weight_kg && window.cpWeightedBox.selectedScale());')
t=t.replace('if(!weighted && !/','if(!weighted && !weighed && !/')
t=t.replace('        intent={task:', '        if(weighed)payload=window.cpWeightedBox.netPayload(payload.operation_id,payload.scan_cell,payload.scan_container);\n        intent={task:')
t=t.replace('route:weighted?"weighted-box":"confirm"','route:weighted?"weighted-box":weighed?"weigh-line":"confirm"')
out[str(p)]=t
print(json.dumps(out,ensure_ascii=True))
