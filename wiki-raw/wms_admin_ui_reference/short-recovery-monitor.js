(() => {
  const panel = document.createElement("section");
  panel.className = "case-panel";
  panel.innerHTML = '<h2>Восстановление отбора</h2><p role="status"></p><table class="case-mini-table"><tbody></tbody></table>';
  (document.querySelector("main") || document.body).append(panel);
  const names = {WAIT_INVENTORY:"Инвентаризация",WAIT_REPLENISHMENT:"Пополнение",READY:"Можно продолжить",FAILED:"Требуется решение"};
  let rows = [], loadedAt = 0, generation = 0;
  const scope = () => JSON.stringify([window.wmsAdminAuth?.state?.apiBase, window.wmsAdminAuth?.state?.user?.username]);
  function render() {
    const elapsed = Math.floor((Date.now() - loadedAt) / 1000);
    const nodes = rows.map(row => {
      const tr = document.createElement("tr");
      const remaining = Number(row.remaining_seconds) - elapsed;
      tr.style.backgroundColor = remaining < 0 ? "#fee2e2" : "#fff7ed";
      const values = ["#" + row.short_id, row.cell + " / " + row.article,
        row.picker, (names[row.recovery_state] || row.status)+" / восстановлено "+(row.restored_quantity||"0")+", остаток "+(row.order_remaining_quantity||"0"),
        (remaining >= 0 ? "Осталось " : "Просрочено ") + Math.abs(remaining) + " сек.",
        row.auditor || "Аудитор не назначен", row.recovery_last_error || row.wait_reason || ""];
      for (const value of values) { const td = document.createElement("td"); td.textContent = value || ""; tr.append(td); }
      const actions = document.createElement("td");
      if (row.inventory_task_id) {
        const link = document.createElement("a"); link.href = "inventory-count.html?inventory_task_id=" + row.inventory_task_id +
          "&cell=" + encodeURIComponent(row.cell) + "&article=" + encodeURIComponent(row.article);
        link.textContent = "Инвентаризация "; actions.append(link);
      }
      if (row.warehouse_task_id) {
        const link = document.createElement("a"); link.href = "warehouse-tasks.html?task_id=" + row.warehouse_task_id;
        link.textContent = "Задание #" + row.warehouse_task_id; actions.append(link);
      }
      if(window.wmsAdminAuth?.hasPermission("inventory_task_view")){
        const link=document.createElement("a");link.href="short-investigation.html?short_id="+row.short_id;
        link.textContent=" Расследование / камера";actions.append(link);
      }
      if (row.recovery_state === "READY" && /^[1-9]\d*$/.test(String(row.case_pick_task_id))) {
        const link = document.createElement("a");
        link.href = "case-pick-tsd.html?case_task_id=" + encodeURIComponent(row.case_pick_task_id);
        link.textContent = " Продолжить сборку #" + row.case_pick_task_id;
        link.title = "Открыть исходное задание; допуск и текущий остаток проверяются сервером";
        actions.append(link);
      }
      tr.append(actions); return tr;
    });
    panel.querySelector("tbody").replaceChildren(...nodes);
  }
  async function load() {
    const token=++generation, identity=scope();
    if (!window.wmsAdminAuth?.hasPermission("case_pick_view")) { panel.hidden = true; return; }
    panel.hidden = false;
    try {
      const auth = window.wmsAdminAuth;
      const response = await fetch(auth.state.apiBase.replace(/\/$/, "") + "/api/inventory/recovery-shorts?limit=50",
        {headers: auth.headers()});
      if (!response.ok) throw new Error("Не удалось получить состояние восстановления: HTTP " + response.status);
      const result = await response.json();
      if(token!==generation||identity!==scope())return;
      rows=result; loadedAt = Date.now(); render();
      panel.querySelector("p").textContent = rows.length ? "Срок считается от сообщения; передача задания его не продлевает." : "Открытых проблем нет.";
    } catch (error) { if(token===generation&&identity===scope())panel.querySelector("p").textContent = error.message; }
  }
  window.addEventListener("wms-admin-auth-ready", () => { generation++; rows=[]; loadedAt=0; panel.querySelector("tbody").replaceChildren(); panel.querySelector("p").textContent=""; void load(); });
  if (window.wmsAdminAuth?.state?.user) load();
  setInterval(() => { if (!document.hidden && loadedAt) render(); }, 1000);
  setInterval(() => { if (!document.hidden && window.wmsAdminAuth?.state?.user) load(); }, 10000);
})();
