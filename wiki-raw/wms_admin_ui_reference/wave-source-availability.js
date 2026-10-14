(() => {
  let requestVersion = 0, context = null, next = null;
  const reasons = {
    SOURCE_STOCK_NOT_FOUND: "Остаток отсутствует", WAREHOUSE_LOCATION_CONFLICT: "Другой склад",
    SOURCE_ARTICLE_CONFLICT: "Другой товар", LOCATION_BLOCKED: "Ячейка недоступна",
    SOURCE_COMPOSITION_CONFLICT: "Не подтверждён состав единиц", SOURCE_BALANCE_INVALID: "Некорректный остаток", CASE_CARRIER_NOT_ALLOCATABLE: "Товар собран в грузовое место",
    SOURCE_REGULATORY_NOT_READY: "Партия не допущена", SOURCE_EXPIRED: "Срок годности истёк",
    SOURCE_SHELF_DAYS: "Недостаточный остаточный срок", SOURCE_SHELF_PERCENT: "Недостаточный процент срока",
    SOURCE_PUTAWAY_REQUIRED: "Требуется размещение", SOURCE_SYSTEM_LOCATION: "Служебная ячейка",
    SOURCE_PICK_FACE_UNPUBLISHED: "Адрес отбора не опубликован", SOURCE_RESERVATION_CONFLICT: "Резерв изменён",
    SOURCE_FREE_INSUFFICIENT: "Недостаточно свободного товара", SOURCE_ARGUMENT_INVALID: "Некорректные условия"
  };
  const target = document.getElementById("waveSourceAvailability");
  async function load(append = false) {
    const version = ++requestVersion, wave = waveReplenishmentState.selectedWave;
    if (!wave || !context) return;
    const waveId = wave.pick_wave_id;
    const params = new URLSearchParams({warehouse: String(wave.ware_id), article: context.articul,
      quantity: String(context.qty ?? 0), purpose: "REPLENISH", limit: "50"});
    if (context.min_shelf_life_days != null) params.set("min_days", context.min_shelf_life_days);
    if (context.min_shelf_life_percent != null) params.set("min_percent", context.min_shelf_life_percent);
    if (append && next) for (const [key, value] of Object.entries(next)) params.set(key, value);
    if (!append) target.querySelector("tbody").innerHTML = "";
    target.querySelector("[data-source-status]").textContent = "Загрузка источников...";
    try {
      const result = await waveRepFetch("/api/inventory/stock-posting/source-availability?" + params);
      if (version !== requestVersion || waveReplenishmentState.selectedWave?.pick_wave_id !== waveId) return;
      target.querySelector("tbody").insertAdjacentHTML("beforeend", result.items.map(row =>
        "<tr>" + [row.pallet_identifier, row.cell, row.physical_qty, row.hard_qty, row.free_qty,
          row.base_uom, row.eligible ? "Доступен" : (reasons[row.reason_code] || row.reason_code)]
          .map(value => "<td>" + escapeWaveRepHtml(value ?? "") + "</td>").join("") + "</tr>").join(""));
      next = result.next;
      target.querySelector("[data-source-next]").hidden = !next;
      target.querySelector("[data-source-status]").textContent = "Свободные источники для нового резерва: " + context.articul;
    } catch (error) {
      if (version === requestVersion) target.querySelector("[data-source-status]").textContent = error.message;
    }
  }
  document.getElementById("waveReplenishmentTaskRows").addEventListener("click", event => {
    const button = event.target.closest("[data-source-task]");
    if (!button) return;
    context = waveReplenishmentState.tasks.find(task => String(task.pick_wave_replenish_task_id) === button.dataset.sourceTask);
    next = null; target.hidden = false; load();
  });
  window.addEventListener('wms-wave-selection-loading',()=>{requestVersion++;context=null;next=null;target.hidden=true;});
  window.addEventListener('wms-wave-selected',()=>{requestVersion++;context=null;next=null;target.hidden=true;});
  window.addEventListener('wms-admin-auth-ready',()=>{requestVersion++;context=null;next=null;target.hidden=true;});
  target.querySelector("[data-source-next]").addEventListener("click", () => load(true));
})();
