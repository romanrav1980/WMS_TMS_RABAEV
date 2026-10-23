/* Durable warehouse confirmations; replay always uses the stored request. */
(() => {
  const prefix = () => "wms.task.complete.v1:" + encodeURIComponent(
    (window.wmsAdminAuth?.state?.apiBase || "") + ":" +
    (window.wmsAdminAuth?.state?.user?.username || "")) + ":";
  const key = taskId => prefix() + taskId;
  const pending = () => Object.keys(localStorage).filter(k => k.startsWith(prefix()))
    .map(k => JSON.parse(localStorage.getItem(k))).sort((a, b) => a.task_id - b.task_id);
  let fetchCommand;
  let busy = false;
  function render() {
    const panel = document.getElementById("warehouseTaskRecovery");
    if (!panel) return;
    const saved = pending()[0];
    panel.hidden = !saved;
    panel.querySelector("span").textContent = saved
      ? "Нет подтверждённого ответа по заданию #" + saved.task_id +
        ". Повтор отправит сохранённые сканы и количество." : "";
    panel.querySelector("button").disabled = busy;
  }
  async function send(saved) {
    if (busy) throw new Error("Подтверждение уже отправляется.");
    const storageKey=key(saved.task_id),raw=localStorage.getItem(storageKey);
    if(raw!==JSON.stringify(saved))throw new Error("Сохранённая команда изменилась. Перечитайте задание.");
    const current=()=>key(saved.task_id)===storageKey&&localStorage.getItem(storageKey)===raw;
    busy = true; render();
    try {
      const response = await fetchCommand("/api/warehouse-tasks/" + saved.task_id + "/complete", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify(saved.payload)
      });
      const result=response.result||response;
      if(result.operation_id!==saved.payload.operation_id||(result.task_id!==undefined&&result.task_id!==saved.task_id)||(result.physical_task_id!==undefined&&result.physical_task_id!==saved.task_id))
        throw new Error("Ответ не подтверждает исходное задание и операцию. Повторите сохранённую команду.");
      if(!current())throw new Error("Пользователь или сохранённая команда изменились. Результат перечитывается в исходной сессии.");
      localStorage.removeItem(storageKey);
      window.dispatchEvent(new CustomEvent("warehouse-task-confirmed",
        {detail: {task_id: saved.task_id, result}}));
      return response;
    } catch (error) {
      // Only explicit validation/rule rejection proves no new task fact was committed.
      if (current()&&([400, 422].includes(error.status) ||
          (error.code === "STOCK_RULE_REJECTED" && [20881, 20886, 20887].includes(error.oracleCode)) ||
          (error.code === "STOCK_RULE_REJECTED" && error.oracleCode === 20890 &&
           error.outcomeConfirmed === true && error.operationId === saved.payload.operation_id))) {
        localStorage.removeItem(storageKey);
      }
      throw error;
    } finally { busy = false; render(); }
  }
  window.warehouseTaskRecovery = {
    init(fetcher) {
      fetchCommand = fetcher;
      if (document.getElementById("warehouseTaskRecovery")) { render(); return; }
      const panel = document.createElement("div");
      panel.id = "warehouseTaskRecovery";
      panel.className = "rights-summary";
      panel.setAttribute("role", "status");
      panel.innerHTML = '<span></span><button type="button">Повторить подтверждение</button>';
      (document.querySelector("main") || document.body).prepend(panel);
      panel.querySelector("button").addEventListener("click", async () => {
        try { const saved = pending()[0]; if (saved) await send(saved); }
        catch (error) { panel.querySelector("span").textContent = error.message; }
      });
      render();
    },
    async complete(taskId, payload) {
      const previous = localStorage.getItem(key(taskId));
      if (previous) throw new Error("Сначала повторите сохранённое подтверждение задания #" + taskId + ".");
      const saved = {task_id: taskId, payload: {...payload,
        operation_id: payload.operation_id || "TASK.UI:" + crypto.randomUUID()}};
      localStorage.setItem(key(taskId), JSON.stringify(saved));
      return send(saved);
    }
  };
})();
