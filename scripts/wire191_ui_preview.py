from pathlib import Path
import json
p=Path("wiki-raw/wms_admin_ui_reference/case-weighted-box.js");t=p.read_text(encoding="utf-8")
a='    const task = cpTsd.task, line = cpTsdCurrentLine();'
b=a+'''
    if (task && line) {
      const admission = document.createElement("p"); admission.textContent = "Расчёт допуска заказа...";
      panel.appendChild(admission);
      cpTsdFetch("/api/case-pick/tasks/" + task.case_pick_task_id + "/lines/" + line.case_pick_line_id + "/order-weight-preview")
        .then(data => {
          if (generation !== currentGeneration) return;
          admission.textContent = "Заказ: " + data.requested_quantity + " KG; отобрано: " + data.picked_quantity +
            " KG; допуск: " + data.tolerance_pct + "% (" + data.lower_quantity + "–" + data.upper_quantity + " KG). " +
            (data.within_tolerance ? "В пределах допуска. Для завершения требуется решение." : "Текущее количество вне допуска.");
        }).catch(error => { if (generation === currentGeneration) admission.textContent = error.message; });
    }
'''
assert t.count(a)==1
print(json.dumps({str(p):t.replace(a,b)},ensure_ascii=True))
