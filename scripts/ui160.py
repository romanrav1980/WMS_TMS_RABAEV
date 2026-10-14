import json
from pathlib import Path
out={}
p=Path("wiki-raw/wms_admin_ui_reference/slotting-demand.html");s=p.read_text(encoding="utf-8").replace('<label>Заявленная масса целой паллеты,', '<label>Опубликованный маршрут кандидатов, необязательно<input id="sdCandidateRoute" type="number" min="1"></label>\n<p>Маршрут ограничивает новые ячейки-кандидаты. Спрос, старый запас и прежний диапазон учитываются по всему артикулу на складе.</p>\n<label>Заявленная масса целой паллеты,')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/slotting-demand.js");s=p.read_text(encoding="utf-8")
s=s.replace('"sdPalletWeight", "sdCosts"','"sdPalletWeight", "sdCosts", "sdCandidateRoute"')
s=s.replace('      if (el("sdPalletWeight").value.trim())', '''      if (el("sdCandidateRoute").value.trim()) {
        const route = Number(el("sdCandidateRoute").value);
        if (!Number.isSafeInteger(route) || route <= 0) throw Error("Укажите целочисленный идентификатор маршрута.");
        body.candidate_pick_route_id = route;
      }
      if (el("sdPalletWeight").value.trim())''')
s=s.replace('row.cell + " · объёмный бюджет: "', 'row.cell + " · режим: " + (row.range_mode || "LEGACY_ACTIVE") + " · новое пополнение: " + (row.new_replenishment_allowed === false ? "запрещено" : "по обычным правилам") + " · объёмный бюджет: "')
s=s.replace('text("Рекомендация диапазона: " + recommendation.status', 'text("Кандидаты: " + (recommendation.candidate_pick_route_id ? "маршрут " + recommendation.candidate_pick_route_id : "склад") + "; прежний диапазон и спрос — весь артикул склада.");\n        text("Рекомендация диапазона: " + recommendation.status')
s=s.replace('el("sdDraftMessage").textContent = "Отправляется исходная команда " + record.body.operation_id + ". При сбое повторите её без изменений.";',
'''const source = record.path.match(/\\/warehouses\\/(\\d+)\\/articles\\/([^/]+)/);
        el("sdDraftMessage").textContent = "Исходная команда " + record.body.operation_id + (source ? " · склад " + source[1] +
          " · артикул " + decodeURIComponent(source[2]) : "") + ". При сбое повторите её без изменений.";''')
pos=s.index('  window.addEventListener("wms-admin-auth-ready"')
s=s[:pos]+'''  ["sdWare", "sdArticle"].forEach(id => el(id).addEventListener("input", () => {
    el("sdDraftResult").textContent = ""; el("sdDraftMessage").textContent = "";
    el("sdProposal").value = ""; el("sdDrainMapping").value = "";
  }));
'''+s[pos:]
out[str(p)]=s
print(json.dumps(out))
