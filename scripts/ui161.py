import json
from pathlib import Path
p=Path("wiki-raw/wms_admin_ui_reference/resource-workload.js");s=p.read_text(encoding="utf-8")
pos=s.index("  async function preview()")
helper="""  function localSecond(iso, finish = false) {
    const match = el("rwOffset").value.match(/^([+-])(\\d{2}):(\\d{2})$/);
    if (!match) throw Error("Выберите часовой пояс ввода.");
    const minutes = (Number(match[2]) * 60 + Number(match[3])) * (match[1] === "+" ? 1 : -1);
    const instant = Date.parse(iso);
    if (!Number.isFinite(instant)) throw Error("Некорректное время рекомендации.");
    const rounded = (finish ? Math.ceil(instant / 1000) : Math.floor(instant / 1000)) * 1000;
    return new Date(rounded + minutes * 60000).toISOString().slice(0, 19);
  }
  function renderRecommendations(result, serial, selected) {
    const proposal = result.recommendations;
    if (!proposal) return;
    text(el("rwResult"), "Рекомендации по плановому ресурсу: " + proposal.status + ". Доступность конкретного сотрудника ещё не подтверждена.");
    (proposal.capacity_actions || []).forEach(row => {
      const block = document.createElement("div");
      text(block, row.from_utc + " — " + row.to_utc + ": добавить " + row.additional_planned_person_hours +
        " плановых человеко-часов; при полном покрытии интервала — ещё " + row.additional_full_interval_people + " сотрудников.");
      if (auth().hasPermission("resource_shift_edit")) {
        const button = document.createElement("button"); button.textContent = "Подставить интервал в план выхода";
        button.addEventListener("click", () => {
          if (serial !== sequence || selected !== scope()) {message("Пересчитайте текущий вариант."); return;}
          clearReplacement(); el("rwStart").value = localSecond(row.from_utc);
          el("rwFinish").value = localSecond(row.to_utc, true);
          el("rwAttendReason").value = "Покрытие рассчитанного дефицита плановой CASE-комплектации";
          message("Интервал подставлен. Выберите квалифицированного сотрудника и отдельно сохраните план; явка не создана.");
        });
        block.appendChild(button);
      }
      el("rwResult").appendChild(block);
    });
    (proposal.wave_duration_scenarios || []).forEach(row => {
      if (!row.one_person_to_utc) {text(el("rwResult"), "Волна " + row.wave_id + ": требуется актуальная норма и единое окно."); return;}
      text(el("rwResult"), "Волна " + row.wave_id + ": с одним сотрудником по норме нужно " + row.known_remaining_person_hours +
        " ч; окончание сценария " + row.one_person_to_utc + ". Сотрудник, подача и стык с рейсом не проверены.");
      const button = document.createElement("button"); button.textContent = "Подставить окно одного сотрудника в предварительный расчёт";
      button.addEventListener("click", () => {
        if (serial !== sequence || selected !== scope()) {message("Пересчитайте текущий вариант."); return;}
        el("rwWave").value = String(row.wave_id); el("rwWaveStart").value = localSecond(row.current_from_utc);
        el("rwWaveFinish").value = localSecond(row.one_person_to_utc, true);
        message("Сценарий подставлен. Добавьте окно и пересчитайте нагрузку; план волны не утверждён.");
      });
      el("rwResult").appendChild(button);
    });
    text(el("rwResult"), "Рекомендация не назначает людей и не переносит утверждённую волну. Подача, перерывы, оборудование и срок рейса проверяются отдельно.");
  }
"""
s=s[:pos]+helper+s[pos:]
s=s.replace('      message("Предварительный расчёт выполнен; планы и задания не изменены.");', '      renderRecommendations(result,serial,selected);\n      message("Предварительный расчёт выполнен; планы и задания не изменены.");')
s=s.replace('  ["rwViewStart", "rwViewFinish", "rwInterval"]', '  ["rwViewStart", "rwViewFinish", "rwInterval", "rwOffset"]')
print(json.dumps({str(p):s}))
