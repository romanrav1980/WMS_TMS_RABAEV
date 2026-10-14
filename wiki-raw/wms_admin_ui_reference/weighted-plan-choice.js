(() => {
  let generation = 0;
  const panel = document.createElement("article");
  panel.className = "admin-window"; panel.hidden = true;
  document.querySelector("main").appendChild(panel);
  document.addEventListener("click", async event => {
    const button = event.target.closest("[data-weight-row]");
    if (!button) return;
    const row = Number(button.dataset.weightRow), request = ++generation;
    panel.hidden = false; panel.textContent = "Загрузка целых весовых коробок...";
    try {
      const data = await orderRequest("/api/picking/order-rows/" + row + (orderCan("case_pick_short_approve") ? "/weighted-box-approval-preview" : "/weighted-box-options"));
      if (generation !== request) return;
      panel.replaceChildren();
      const heading = document.createElement("h3"); heading.textContent = "Целые весовые коробки: " + data.article;
      const summary = document.createElement("p");
      summary.textContent = "Остаток строки: " + data.remaining_row_quantity + " KG; заказ по товару: " +
        data.requested_order_quantity + " KG; отобрано: " + data.picked_order_quantity + " KG; допуск: " + data.tolerance_pct +
        "%. Упаковка отбирается целиком.";
      panel.append(heading, summary);
      const table = document.createElement("table"); table.className = "rights-table";
      const header = document.createElement("tr");
      for (const text of ["Идентификатор паллеты", "Ячейка", "Нетто, KG", "Брутто, KG", "Объём, м³", "Условия"]) {
        const cell = document.createElement("th"); cell.textContent = text; header.appendChild(cell);
      }
      const head = document.createElement("thead"); head.appendChild(header); table.appendChild(head);
      const body = document.createElement("tbody");
      for (const box of data.boxes) {
        const tr = document.createElement("tr");
        for (const text of [box.pallet_identifier, box.source_cell, box.net_weight_kg,
          box.gross_weight_kg ?? "—", box.volume_m3 ?? "—",
          !box.measurements_ready ? "Нет подтверждённых измерений упаковки" :
          box.exception_required ? "Нужно согласовать исключение последней коробки" : "В пределах допуска заказа"]) {
          const cell = document.createElement("td"); cell.textContent = text; tr.appendChild(cell);
        }
        body.appendChild(tr);
      }
      table.appendChild(body); panel.appendChild(table);
      if (!data.boxes.length) { const empty = document.createElement("p"); empty.textContent = "Доступных целых коробок нет."; panel.appendChild(empty); }
      if (data.has_more) { const more = document.createElement("p"); more.textContent = "Показаны первые 100 доступных коробок."; panel.appendChild(more); }
      window.orderWeightedChoice = {row, source: data, panel, body};
      document.dispatchEvent(new CustomEvent("retailcase-weighted-options", {detail: window.orderWeightedChoice}));
    } catch (error) { if (generation === request) panel.textContent = error.message; }
  });
})();
