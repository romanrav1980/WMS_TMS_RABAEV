(() => {
  const panel = document.createElement("details");
  panel.className = "panel count-task-queue";
  panel.open = !matchMedia("(max-width:760px)").matches;
  panel.innerHTML = '<summary title="Открыть или свернуть доступные задания инвентаризации" data-help-id="inventory.tasks.toggle">Задания инвентаризации</summary><button type="button" title="Перечитать доступные задания инвентаризации" data-help-id="inventory.tasks.refresh">Обновить задания</button><p role="status"></p><div></div>';
  (document.querySelector("main") || document.body).prepend(panel);
  const message = panel.querySelector("p");
  const api = async (path, post = false) => {
    const auth = window.wmsAdminAuth;
    const response = await fetch(auth.state.apiBase.replace(/\/$/, "") + path,
      {method: post ? "POST" : "GET", headers: auth.headers()});
    const data = await response.json();
    if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail));
    return data;
  };
  async function load() {
    if (!window.wmsAdminAuth?.hasPermission("inventory_task_view")) { panel.hidden = true; panel.querySelector("div").replaceChildren(); return; }
    panel.hidden = false;
    try {
      const selected = new URLSearchParams(location.search).get("inventory_task_id");
      const tasks = await api("/api/inventory/tasks?limit=50" + (selected ? "&task_id=" + encodeURIComponent(selected) : ""));
      if (selected && tasks.length === 1) {
        const task = tasks[0];
        document.getElementById("countWarehouse").value = task.warehouse_id;
        document.getElementById("countCell").value = task.cell;
        document.getElementById("countInventoryTask").value = task.inventory_task_id;
        document.getElementById("countArticle").value = task.article;
        document.getElementById("countRevision").value = task.revision_id || "";
      }
      const rows = tasks.map(task => {
        const row = document.createElement("p");
        const title = document.createElement("span");
        title.textContent = "#" + task.inventory_task_id + " — " + task.cell + " / " + task.article +
          " — " + task.status + " — " + (task.assigned_to || "не назначен") + " ";
        const button = document.createElement("button");
        button.type = "button"; button.textContent = "Взять и пересчитать";
        button.title = "Принять это задание и подставить его склад, ячейку и артикул в пересчёт";
        button.dataset.helpId = "inventory.tasks.claim";
        button.disabled = !window.wmsAdminAuth.hasPermission("inventory_task_execute") ||
          !window.wmsAdminAuth.hasPermission("stock_inventory_count");
        button.addEventListener("click", async () => {
          button.disabled = true;
          try {
            const claimed = await api("/api/inventory/tasks/" + task.inventory_task_id + "/claim", true);
            document.getElementById("countWarehouse").value = claimed.warehouse_id;
            document.getElementById("countCell").value = claimed.cell;
            document.getElementById("countInventoryTask").value = claimed.inventory_task_id;
            document.getElementById("countRevision").value = claimed.revision_id || "";
            document.getElementById("countArticle").value = claimed.article;
            document.getElementById("countReason").value = "Пересчёт по недостаче #" + claimed.short_id;
            message.textContent = "Задание принято. Откройте документ пересчёта, загрузите партии и подтвердите фактический остаток.";
          } catch (error) { message.textContent = error.message; }
          finally { button.disabled = false; }
        });
        row.append(title, button); return row;
      });
      panel.querySelector("div").replaceChildren(...rows);
      message.textContent = rows.length ? "Срочные задания показаны первыми." : "Открытых заданий нет.";
    } catch (error) { panel.querySelector("div").replaceChildren(); message.textContent = error.message; }
  }
  panel.querySelector("button").addEventListener("click", load);
  window.addEventListener("wms-admin-auth-ready", load);
  if (window.wmsAdminAuth?.state?.user) load();
})();
