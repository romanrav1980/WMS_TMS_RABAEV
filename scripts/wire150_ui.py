from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/resource-workload.html");text=p.read_text(encoding="utf-8")
needle='<button id="rwAttend">Добавить плановый выход</button>'
assert text.count(needle)==1
text=text.replace(needle,needle+'<p id="rwReplaceLabel">План для изменения не выбран.</p><button id="rwReplace" disabled>Сохранить изменение выбранного выхода</button><button id="rwReplaceClear">Снять выбор</button>')
out[str(p)]=text
p=Path("wiki-raw/wms_admin_ui_reference/resource-workload.js");text=p.read_text(encoding="utf-8")
text=text.replace('config = null, windows = [];','config = null, windows = [], replacement = null;',1)
needle='  function reset() { ++sequence;'
assert text.count(needle)==1
text=text.replace(needle,'  function reset() { clearReplacement(); ++sequence;')
needle='  function renderConfiguration(result) {'
text=text.replace(needle,'''  function clearReplacement() {
    replacement = null; el("rwReplace").disabled = true;
    el("rwReplaceLabel").textContent = "План для изменения не выбран.";
  }
'''+needle)
needle='    config = result;'
text=text.replace(needle,'    clearReplacement(); config = result;',1)
needle='        block.appendChild(button);'
assert text.count(needle)==1
text=text.replace(needle,needle+'''
        const change = document.createElement("button"); change.textContent = "Выбрать для изменения";
        change.addEventListener("click", () => {
          if (!config || config.warehouse_id !== ware()) {message("Загрузите текущие планы выбранного склада."); return;}
          replacement = {source: row.plan_operation_id, warehouse: row.ware_id, owner: owner()};
          el("rwPerson").value = String(row.resource_id);
          el("rwReplaceLabel").textContent = "Изменяется выход " + row.person_id + " · " + row.site_code + " · " + row.start_at + " — " + row.finish_at;
          el("rwReplace").disabled = false;
          message("Введите будущий интервал, подсклад и основание. Прежний план заменится только вместе с новым.");
        });
''')
needle='      const block = document.createElement("div"); text(block, row.person_id + " · " + row.site_code + " · " + row.start_at + " — " + row.finish_at);'
assert text.count(needle)==1
text=text.replace(needle,needle+'''
      if (row.replaced_plan_operation_id) text(block, "Сохранён вместо предыдущего выхода; прежняя запись остаётся в истории.");
''')
needle='  ["rwWare", "rwSite"].forEach'
assert text.count(needle)==1
text=text.replace(needle,'''  el("rwReplaceClear").addEventListener("click", clearReplacement);
  el("rwReplace").addEventListener("click", () => {
    try {
      if (!replacement || replacement.owner !== owner() || replacement.warehouse !== ware()) throw Error("Заново выберите действующий план этого склада.");
      mutate("/api/resources/workload/attendance/replace", {warehouse_id: ware(), plan_operation_id: replacement.source,
        site_code: el("rwSite").value, resource_id: Number(el("rwPerson").value),
        start_at: at("rwStart"), finish_at: at("rwFinish"), reason: el("rwAttendReason").value});
    } catch (error) {message(error.message);}
  });
'''+needle)
# Existing durable result retry retained across reload and reopened same-origin windows.
text=text.replace("sessionStorage","localStorage")
out[str(p)]=text
print(json.dumps(out,ensure_ascii=True))
