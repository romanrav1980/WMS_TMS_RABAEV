/* Доступ к ARM комплектации (C0121/C0122): плоское право legacy case_pick_view ИЛИ готовая native capability
   picking хотя бы одного склада (/api/access/workspaces через window.wmsNativeAccess). Любое ACTIVE назначение
   (например, только вход в оболочку) доступа к комплектации не даёт. Окончательно права проверяет сервер. */
(() => {
  const select = () => document.querySelector(".resource-top-select");

  async function check() {
    const auth = window.wmsAdminAuth;
    if (!auth?.state?.user) return { allowed: false, reason: "Войдите в систему." };
    let warehouses = [];
    try { warehouses = await window.wmsNativeAccess.warehouses("picking"); }
    catch (error) {
      if (auth.hasPermission("case_pick_view")) return { allowed: true, mode: "legacy", warehouses: [] };
      return { allowed: false, retry: !(error.status < 500), reason: error.status < 500
        ? "Нет доступа к комплектации (HTTP " + error.status + ")." : "Проверка доступа недоступна. Повторите после восстановления связи." };
    }
    if (auth.hasPermission("case_pick_view")) return { allowed: true, mode: "legacy", warehouses };
    if (!warehouses.length) return { allowed: false, reason: "Нет права просмотра комплектации ни по одному складу." };
    return { allowed: true, mode: "scoped", warehouses };
  }

  function banner(result) {
    let el = document.getElementById("caseAccessBanner");
    if (!el) {
      el = document.createElement("p"); el.id = "caseAccessBanner"; el.setAttribute("role", "status");
      (document.querySelector(".case-topbar") || document.querySelector("main"))?.after(el);
    }
    el.hidden = result.mode === "legacy";
    el.className = "case-access-banner" + (result.allowed ? "" : " bad");
    el.textContent = result.allowed ? "Доступ по области: склады " + result.warehouses.join(", ") + ". Данные и действия ограничит сервер." : result.reason;
    if (result.retry) {
      const b = document.createElement("button"); b.type = "button"; b.textContent = "Повторить проверку";
      b.title = "Повторить проверку доступа. Данные откроются только после ответа сервера"; b.dataset.helpId = "case.access.retry";
      b.addEventListener("click", () => caseSafe(window.caseAccess.start)); el.append(b);
    }
  }

  /** Склад страницы: список складов с picking; выбор пишется в адрес (warehouse_id) и фильтрует данные на сервере. */
  function fillWarehouses(result) {
    const el = select();
    if (!el) return;
    const current = window.wmsNativeAccess.warehouseFromUrl();
    const ids = [...new Set([...(current ? [current] : []), ...result.warehouses])];
    el.innerHTML = `<option value="">Все доступные склады</option>` + ids.map(id => `<option value="${escapeHtml(id)}">Склад ${escapeHtml(id)}</option>`).join("");
    el.value = current; el.title = "Склад комплектации. Выбор сохраняется в адресе; данные чужого склада сервер не покажет";
    el.dataset.helpId = "case.warehouse";
    el.onchange = () => {
      const url = new URL(location.href);
      if (el.value) url.searchParams.set("warehouse_id", el.value); else url.searchParams.delete("warehouse_id");
      url.searchParams.delete("task_id"); history.replaceState(history.state, "", url);
      caseState.selectedId = null; caseSafe(loadCaseData);
    };
  }

  /** Проверить доступ и только затем загрузить данные. Отказ очищает ранее показанные данные. */
  async function start() {
    const result = await check();
    banner(result);
    if (result.allowed) { fillWarehouses(result); return loadCaseData(); }
    caseState.tasks = []; caseState.shorts = []; caseState.selectedId = null; renderAll();
  }

  window.caseAccess = { check, start };
})();
