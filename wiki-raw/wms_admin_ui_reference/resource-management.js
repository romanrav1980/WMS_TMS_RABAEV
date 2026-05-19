const resourceRows = [
  { code: "RT-01", type: "REACHTRUCK", typeLabel: "Ричтрак", equipment: "RTH-01 (BT Reflex)", operator: "Иванов И.И.", shift: "Дневная (08:00 - 20:00)", zone: "A1, A2, A3", status: "В работе", current: "REPL-2026-05-19-0456", currentKind: "Пополнение", next: "STAGE-2026-05-19-0781", nextKind: "Стаджинг", progress: 65 },
  { code: "RT-02", type: "REACHTRUCK", typeLabel: "Ричтрак", equipment: "RTH-02 (Jungheinrich)", operator: "Петров П.П.", shift: "Дневная (08:00 - 20:00)", zone: "A1, A2", status: "В работе", current: "PUTAWAY-2026-05-19-0342", currentKind: "Размещение", next: "REPL-2026-05-19-0460", nextKind: "Пополнение", progress: 40 },
  { code: "RT-03", type: "REACHTRUCK", typeLabel: "Ричтрак", equipment: "RTH-03 (Crown)", operator: "Сидоров С.С.", shift: "Дневная (08:00 - 20:00)", zone: "B1, B2", status: "В простое", current: "-", currentKind: "Перерыв", next: "REPL-2026-05-19-0488", nextKind: "Пополнение", progress: 15 },
  { code: "KIKA-01", type: "KIKA", typeLabel: "KIKA", equipment: "KIKA-01", operator: "Алексеев А.А.", shift: "Дневная (08:00 - 20:00)", zone: "B1, B2, C1", status: "В работе", current: "MOVE-2026-05-19-0551", currentKind: "Перемещение", next: "MOVE-2026-05-19-0552", nextKind: "Перемещение", progress: 70 },
  { code: "FL-01", type: "FORKLIFT", typeLabel: "Погрузчик", equipment: "FL-01 (Toyota)", operator: "Кузнецов К.К.", shift: "Дневная (08:00 - 20:00)", zone: "Зона погрузки", status: "В работе", current: "LOAD-2026-05-19-0221", currentKind: "Погрузка", next: "LOAD-2026-05-19-0222", nextKind: "Погрузка", progress: 55 },
  { code: "TR-01", type: "TROLLEY", typeLabel: "Тележка", equipment: "EPT-01", operator: "Михайлов М.М.", shift: "Дневная (08:00 - 20:00)", zone: "C1, C2", status: "Доступен", current: "-", currentKind: "Ожидание задач", next: "CASE-2026-05-19-0560", nextKind: "Коробочный отбор", progress: 5 },
  { code: "CP-01", type: "CASE_PICKER", typeLabel: "Комплектовщик", equipment: "TR-02", operator: "Орлова Н.Н.", shift: "Дневная (08:00 - 20:00)", zone: "C1", status: "В работе", current: "CASE-2026-05-19-0601", currentKind: "Коробочный отбор", next: "CASE-2026-05-19-0602", nextKind: "Коробочный отбор", progress: 52 },
  { code: "LOAD-TEAM-01", type: "LOADING_TEAM", typeLabel: "Бригада погрузки", equipment: "Док 3", operator: "Бригада 1", shift: "Дневная (08:00 - 20:00)", zone: "Док 3", status: "В работе", current: "TRUCK-2026-05-19-0007", currentKind: "Отгрузка фуры", next: "TRUCK-2026-05-19-0008", nextKind: "Отгрузка", progress: 48 },
  { code: "COOK-01", type: "COOKING", typeLabel: "Варка", equipment: "Котел 1", operator: "Оператор варки", shift: "Дневная (08:00 - 20:00)", zone: "Производство", status: "В работе", current: "PO-44-COOK", currentKind: "Варка", next: "PO-45-COOK", nextKind: "Варка", progress: 62 },
  { code: "PACK-01", type: "PACKING", typeLabel: "Фасовка", equipment: "Линия фасовки 1", operator: "Оператор фасовки", shift: "Дневная (08:00 - 20:00)", zone: "Производство", status: "Доступен", current: "-", currentKind: "Ожидание выпуска", next: "PO-44-PACK", nextKind: "Фасовка", progress: 12 },
  { code: "RT-04", type: "REACHTRUCK", typeLabel: "Ричтрак", equipment: "RTH-04 (BT Reflex)", operator: "-", shift: "-", zone: "-", status: "Недоступен", current: "-", currentKind: "Нет сессии", next: "-", nextKind: "-", progress: 0 }
];

const ganttRows = [
  { code: "RT-01", person: "Иванов И.И.", tasks: 7, bars: [{ label: "REPL-0456", start: 8, end: 11.2, cls: "fact" }, { label: "STAGE-0781", start: 11.2, end: 12.7, cls: "fact" }, { label: "", start: 12.7, end: 18.6, cls: "plan" }] },
  { code: "RT-02", person: "Петров П.П.", tasks: 6, bars: [{ label: "PUTAWAY-0342", start: 8, end: 11, cls: "plan" }, { label: "REPL-0460", start: 11, end: 12, cls: "fact" }, { label: "", start: 12, end: 18.6, cls: "plan" }] },
  { code: "RT-03", person: "Сидоров С.С.", tasks: 3, bars: [{ label: "Перерыв", start: 8, end: 9.3, cls: "idle" }, { label: "", start: 9.4, end: 14.5, cls: "future" }] },
  { code: "KIKA-01", person: "Алексеев А.А.", tasks: 8, bars: [{ label: "MOVE-0551", start: 8, end: 10.7, cls: "fact" }, { label: "MOVE-0552", start: 10.7, end: 18.6, cls: "plan" }] },
  { code: "CP-01", person: "Орлова Н.Н.", tasks: 12, bars: [{ label: "CASE-0601", start: 8.2, end: 12.4, cls: "fact" }, { label: "CASE-0602", start: 12.4, end: 17.2, cls: "late" }] },
  { code: "COOK-01", person: "Варка", tasks: 2, bars: [{ label: "PO-44", start: 8, end: 12, cls: "fact" }, { label: "PO-45", start: 13, end: 17, cls: "plan" }] },
  { code: "PACK-01", person: "Фасовка", tasks: 2, bars: [{ label: "PO-44", start: 12.5, end: 16, cls: "future" }] }
];

let activeTab = "all";

function statusClass(status) {
  if (status === "В работе") return "green";
  if (status === "Доступен") return "blue";
  if (status === "В простое") return "amber";
  return "";
}

function renderResources() {
  const zone = document.getElementById("resourceZoneFilter").value;
  const status = document.getElementById("resourceStatusFilter").value;
  const rows = resourceRows.filter((row) => {
    const tabOk = activeTab === "all" || row.type === activeTab;
    const zoneOk = !zone || row.zone.includes(zone);
    const statusOk = !status || row.status === status;
    return tabOk && zoneOk && statusOk;
  });

  document.getElementById("resourceRows").innerHTML = rows.map((row) => `
    <tr>
      <td><span class="resource-code">${escapeHtml(row.code)}</span></td>
      <td>${escapeHtml(row.typeLabel)}</td>
      <td>${escapeHtml(row.equipment)}</td>
      <td>${escapeHtml(row.operator)}</td>
      <td>${escapeHtml(row.shift)}</td>
      <td>${escapeHtml(row.zone)}</td>
      <td><span class="tag ${statusClass(row.status)}">${escapeHtml(row.status)}</span></td>
      <td><b>${escapeHtml(row.current)}</b><small>${escapeHtml(row.currentKind)}</small></td>
      <td><b>${escapeHtml(row.next)}</b><small>${escapeHtml(row.nextKind)}</small></td>
      <td><span class="resource-progress"><i style="width:${row.progress}%"></i></span><em>${row.progress}%</em></td>
      <td class="resource-menu">...</td>
    </tr>
  `).join("");
  document.getElementById("resourceTotal").textContent = `Всего: ${rows.length} ресурсов`;
}

function renderGantt() {
  const hours = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"];
  const head = `<div class="resource-gantt-head"><span>Ресурс</span><span>Задач</span>${hours.map((hour) => `<b>${hour}</b>`).join("")}</div>`;
  const rows = ganttRows.map((row) => `
    <div class="resource-gantt-row">
      <span><b>${escapeHtml(row.code)}</b><small>${escapeHtml(row.person)}</small></span>
      <strong>${row.tasks}</strong>
      <div class="resource-gantt-lane">
        ${row.bars.map((bar) => `<i class="${bar.cls}" style="left:${toStartPercent(bar.start)}%;width:${toWidthPercent(bar.end - bar.start)}%">${escapeHtml(bar.label)}</i>`).join("")}
      </div>
    </div>
  `).join("");
  document.getElementById("resourceGantt").innerHTML = head + rows + '<div class="resource-now" style="left:62.5%">15:30</div>';
}

function toStartPercent(hourValue) {
  return ((hourValue - 8) / 12) * 100;
}

function toWidthPercent(hourDuration) {
  return (hourDuration / 12) * 100;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

document.getElementById("resourceTabs").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-resource-tab]");
  if (!button) return;
  activeTab = button.dataset.resourceTab;
  document.querySelectorAll("#resourceTabs button").forEach((item) => item.classList.toggle("active", item === button));
  renderResources();
});

document.getElementById("resourceZoneFilter").addEventListener("change", renderResources);
document.getElementById("resourceStatusFilter").addEventListener("change", renderResources);
document.getElementById("resourceReset").addEventListener("click", () => {
  document.getElementById("resourceZoneFilter").value = "";
  document.getElementById("resourceStatusFilter").value = "";
  activeTab = "all";
  document.querySelectorAll("#resourceTabs button").forEach((item) => item.classList.toggle("active", item.dataset.resourceTab === "all"));
  renderResources();
});

renderResources();
renderGantt();
