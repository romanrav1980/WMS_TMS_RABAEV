from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/case-weighted-box.js");t=p.read_text(encoding="utf-8")
t=t.replace("  let panel;","  let panel, generation = 0;")
t=t.replace("    panel.replaceChildren();","    const currentGeneration = ++generation;\n    panel.replaceChildren();")
a="    panel.appendChild(note);"
t=t.replace(a,a+"""
    const label = document.createElement("label");
    label.textContent = "Архив весового поста: ";
    const select = document.createElement("select");
    select.dataset.scale = "capture";
    select.appendChild(new Option("Без показания весового поста", ""));
    label.appendChild(select); panel.appendChild(label);
    const task = cpTsd.task, line = cpTsdCurrentLine();
    if (task && line) cpTsdFetch("/api/inventory/warehouse-scales/captures?task=" + task.case_pick_task_id + "&line=" + line.case_pick_line_id)
      .then(data => {
        if (generation !== currentGeneration) return;
        for (const item of data.items) select.appendChild(new Option(
          item.weight_kg + " KG " + item.basis + " / " + item.device_mode + " / " + item.measured_at,
          item.capture_key));
      }).catch(error => { if (generation === currentGeneration) cpTsdSetState(error.message); });
""")
t=t.replace('    return { operation_id: operation, weighted_box_barcode: barcode, scan_cell: cell,','    const scale = panel.querySelector("select[data-scale]").value;\n    return { ...(scale ? {warehouse_scale_capture: scale} : {}), operation_id: operation, weighted_box_barcode: barcode, scan_cell: cell,')
out[str(p)]=t
print(json.dumps(out,ensure_ascii=True))
