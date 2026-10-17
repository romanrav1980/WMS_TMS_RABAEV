const WMS_ADMIN_NAV_ITEMS = [
  { key: 'tare-load-recovery', label: 'Тара возвращённой погрузки', href: 'tare-load-recovery.html', icon: 'orders', permission: 'tare_view' },
  { key: 'slotting-demand', label: 'Потребность для диапазона', href: 'slotting-demand.html', icon: 'orders', permission: 'pick_topology_view' },
  { key: 'resource-workload', label: 'Нагрузка и выход персонала', href: 'resource-workload.html', icon: 'orders', permission: 'resource_shift_view' },
  { key: 'warehouse-forecast', label: 'Прогноз складской нагрузки', href: 'warehouse-forecast.html', icon: 'orders', permission: 'transport_dispatch_view' },
  { key: 'pallet-composition', label: 'Состав и происхождение паллеты', href: 'pallet-composition.html', icon: 'orders', permission: 'traceability_view' },
  { key: 'trace-manifests', label: 'Состав маркированного груза', href: 'trace-manifests.html', icon: 'orders', permission: 'wms_admin_login' },
  { key: 'day-reconciliation', label: 'Сверка исполнения', href: 'day-reconciliation.html', icon: 'orders', permission: 'transport_dispatch_view' },
  { key: 'logistics-expenses', label: 'Дополнительные расходы', href: 'logistics-expenses.html', icon: 'orders', permission: 'transport_dispatch_view' },
  { key: 'logistics-costs', label: 'Складские затраты', href: 'logistics-costs.html', icon: 'orders', permission: 'transport_dispatch_view' },
  { key: 'return-disposal', label: 'Утилизация возврата', href: 'return-disposal.html', icon: 'orders', permission: 'warehouse_return_dispatch' },
  { key: 'interwarehouse-groups', label: 'Межскладские грузовые места', href: 'interwarehouse-groups.html', icon: 'orders', permission: 'transport_dispatch_view' },
  { key: 'interwarehouse', label: 'Межскладской поток', href: 'interwarehouse.html', icon: 'orders', permission: 'transport_dispatch_view' },
  { key: 'supplier-handover', label: 'Передача поставщику', href: 'supplier-handover.html', icon: 'orders', permission: 'warehouse_return_dispatch' },
  { key: 'supplier-return', label: 'Возврат поставщику', href: 'supplier-return.html', icon: 'orders', permission: 'warehouse_return_dispatch' },
  { key: 'tare-loss', label: 'Недостача тары', href: 'tare-loss.html', icon: 'orders', permission: 'tare_view' },
  { key: 'tare-assembly', label: 'Тара для сборки', href: 'tare-assembly.html', icon: 'orders', permission: 'tare_view' },
  { key: 'tare-resolutions', label: 'Повреждения тары', href: 'tare-resolutions.html', icon: 'orders', permission: 'tare_view' },
  { key: 'tare-return-policy', label: 'Сроки возврата тары', href: 'tare-return-policy.html', icon: 'orders', permission: 'warehouse_settings_edit' },
  { key: 'tare-ledger', label: 'Оборотная тара', href: 'tare-ledger.html', icon: 'orders', permission: 'tare_view' },
  { key: 'store-return-putaway', label: 'Размещение возвратов', href: 'store-return-putaway.html', icon: 'orders', permission: 'warehouse_return_place' },
  { key: "store-return-receiving", label: "Складская приёмка возвратов", href: "store-return-receiving.html", icon: "orders", permission: "wms_admin_login" },
  { key: "driver-bindings", label: "Учётные записи водителей", href: "driver-bindings.html", icon: "orders", permission: "warehouse_settings_edit" },
  { key: "store-return-transport", label: "Вывоз возвратов", href: "store-return-transport.html", icon: "orders", permission: "store_return_transport" },
  { key: "store-returns", label: "Возвраты магазинов", href: "store-returns.html", icon: "orders", permission: "store_return_approve" },
  { key: "store-investigations", label: "Расследования поставок", href: "store-investigations.html", icon: "orders", permission: "wms_admin_login" },
  { key: "transport-loading", label: "Погрузка и выезд", href: "transport-loading.html", icon: "warehouse-types", permission: "transport_dispatch_view" },
  { key: "warehouse-hus", label: "Грузовые места", href: "warehouse-hus.html", icon: "warehouse-types", permission: "warehouse_task_view" },
  { key: "inventory-count", label: "Пересчёт", href: "inventory-count.html", icon: "orders", permission: "stock_inventory_count" },
  { key: "quality-policy", label: "Правила контроля отгрузки", href: "quality-policy.html", icon: "settings", permission: "warehouse_settings_view" },
  { key: "store-directory", label: "Магазины", href: "store-directory.html", icon: "settings", permission: "warehouse_settings_view" },
  { key: "receiving", label: "Приёмка поставки SAP", href: "receiving.html", icon: "orders", permission: "sap_supply_view" },
  { key: "home", label: "Главная", href: "index.html", icon: "home" },
  { key: "shift-supervisor", label: "Панель смены", href: "shift-supervisor-wave.html", icon: "kpi", permission: "pick_wave_view" },
  { key: "production", label: "Производство", href: "index.html", icon: "production" },
  { key: "mes", label: "MES", href: "production-orders.html", icon: "mes", permission: "mes_production_view" },
  { key: "raw-supply", label: "Сырье в производство", href: "raw-supply.html", icon: "raw", permission: "mes_raw_supply_view" },
  { key: "warehouse-tasks", label: "Складские задания", href: "warehouse-tasks.html", icon: "warehouse-types", permission: "warehouse_task_view" },
  { key: "resource-management", label: "Ресурсы", href: "resource-management.html", icon: "warehouse-types", permission: "resource_management_view" },
  { key: "warehouse-simulation", label: "Симуляция склада", href: "warehouse-simulation.html", icon: "kpi", permission: "pick_wave_view" },
  { key: "wave-replenishment", label: "Пополнение волны", href: "wave-replenishment.html", icon: "orders", permission: "pick_wave_view" },
  { key: "warehouse-task-sync", label: "Sync заданий", href: "warehouse-task-sync.html", icon: "api", permission: "warehouse_task_view" },
  { key: "reachtruck-tsd", label: "ТСД ричтрака", href: "reachtruck-tsd.html", icon: "warehouse-types", permission: "warehouse_task_view" },
  { key: "case-pick-management", label: "Комплектация", href: "case-pick-management.html", icon: "orders", permission: "case_pick_view" },
  { key: "case-pick-tsd", label: "ТСД сборки", href: "case-pick-tsd.html", icon: "orders", permission: "case_pick_view" },
  { key: "bom", label: "BOM", href: "bom.html", icon: "bom", permission: "bom_view" },
  { key: "customers", label: "Клиенты", href: "customers.html", icon: "customers", permission: "customer_view" },
  { key: "customer-orders", label: "Заказы клиентов", href: "customer-orders.html", icon: "orders", permission: "customer_order_view" },
  { key: "warehouses", label: "Склады", href: "index.html", icon: "warehouses" },
  { key: "warehouse-types", label: "Типы складов", href: "warehouses.html", icon: "warehouse-types", permission: "warehouse_settings_view" },
  { key: "aging", label: "Вылежка партий", href: "product-shipment-settings.html", icon: "aging", permission: "quality_batch_view" },
  { key: "raw", label: "Сырье", href: "raw-material.html", icon: "raw", permission: "raw_material_view" },
  { key: "finished", label: "Готовая продукция", href: "finished-goods.html", icon: "finished", permission: "finished_goods_view" },
  { key: "settings", label: "Настройки", href: "index.html", icon: "settings" },
  { key: "rights", label: "Права", href: "rights-admin.html", icon: "rights", permission: "rights_admin_view" },
  { key: "kpi", label: "KPI", href: "index.html", icon: "kpi" },
  { key: "api", label: "API", href: "api-audit.html", icon: "api", permission: "api_audit_view" },
  { key: "external", label: "Внешние отправки", href: "external-outbox.html", icon: "external", permission: "external_outbox_view" },
  { key: "reports", label: "Отчеты", href: "index.html", icon: "reports" },
];

function renderWmsAdminNav() {
  document.querySelectorAll("[data-admin-nav]").forEach((nav) => {
    const activeKey = nav.dataset.activeNav || "home";
    nav.innerHTML = WMS_ADMIN_NAV_ITEMS.map((item) => {
      const classes = ["nav-link"];
      if (item.key !== "home") classes.push("more");
      if (item.key === activeKey) classes.push("active");
      const permissionAttr = item.permission ? ` data-permission="${escapeNavAttr(item.permission)}"` : "";
      return `<a class="${classes.join(" ")}" href="${escapeNavAttr(item.href)}"${permissionAttr}>`
        + `<svg class="nav-icon" aria-hidden="true"><use href="assets/nav-icons.svg#icon-${escapeNavAttr(item.icon)}"></use></svg>`
        + `<span class="nav-label">${escapeNavText(item.label)}</span>`
        + "</a>";
    }).join("");
  });
}

function escapeNavText(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function escapeNavAttr(value) {
  return escapeNavText(value).replaceAll('"', "&quot;");
}

renderWmsAdminNav();

/* Native-навигация (C0122): права по области не попадают в плоский auth.permissions, поэтому пункты с готовой
   READ capability из /api/access/workspaces раскрываются отдельно. Это только навигация (navigation_only):
   операции и данные по-прежнему проверяет сервер. Текущий склад из адреса (warehouse_id) переносится в ссылку. */
const WMS_NATIVE_NAV = { "case-pick-management": "picking", "case-pick-tsd": "picking", "transport-loading": "dispatch", "warehouse-hus": "warehouse_tasks" };

window.wmsNativeAccess = (() => {
  let cacheKey = null, cache = null;
  function load() {
    const auth = window.wmsAdminAuth;
    if (!auth?.state?.user) return Promise.resolve(null);
    const key = auth.state.apiBase + ":" + auth.state.user.username;
    if (cacheKey !== key) {
      cacheKey = key;
      cache = fetch(auth.state.apiBase + "/api/access/workspaces", { headers: auth.headers(), cache: "no-store" })
        .then(r => r.ok ? r.json() : Promise.reject(Object.assign(new Error("HTTP " + r.status), { status: r.status })));
      cache.catch(() => { cacheKey = null; });
    }
    return cache;
  }
  const warehouseFromUrl = () => new URLSearchParams(location.search).get("warehouse_id")?.replace(/\D/g, "") || "";
  async function warehouses(capability) {
    const data = await load();
    return (data?.warehouses || []).filter(w => w.capabilities?.[capability] === true).map(w => String(w.warehouse_id));
  }
  /** Показать элемент: плоское право legacy ИЛИ native capability хотя бы одного склада (сервер решит по операции). */
  async function allows(capabilities, flat) {
    if (flat && window.wmsAdminAuth?.hasPermission(flat)) return true;
    for (const cap of capabilities) { try { if ((await warehouses(cap)).length) return true; } catch { /* нет ответа — закрыто */ } }
    return false;
  }
  async function applyNav() {
    const wh = warehouseFromUrl();
    for (const [key, cap] of Object.entries(WMS_NATIVE_NAV)) {
      const item = WMS_ADMIN_NAV_ITEMS.find(i => i.key === key);
      let list = [];
      try { list = await warehouses(cap); } catch { continue; }
      document.querySelectorAll(`[data-admin-nav] a[href="${escapeNavAttr(item.href)}"], [data-admin-nav] a[href^="${escapeNavAttr(item.href)}?"]`).forEach(link => {
        if (list.length) { link.hidden = false; link.dataset.nativeCapability = cap; }
        link.setAttribute("href", wh && list.includes(wh) ? item.href + "?warehouse_id=" + wh : item.href);
      });
    }
  }
  function deny() {
    const workspace = document.querySelector(".workspace");
    if (!workspace || workspace.querySelector(":scope > .native-denied")) return;
    // Разметку страницы не удаляем (её скрипты могут ещё привязывать обработчики) — только скрываем.
    [...workspace.children].forEach(node => { node.hidden = true; });
    workspace.insertAdjacentHTML("beforeend", '<section class="admin-page native-denied"><article class="panel access-denied"><h2>Нет прав на этот раздел</h2>'
      + "<p>Нет права legacy и нет готовой возможности ни по одному складу. Доступ определяет сервер.</p></article></section>");
  }
  async function applyPage() {
    const page = document.body.dataset.nativePage;
    if (page && !(await allows(page.split(/\s+/), document.body.dataset.flatPermission))) { deny(); return; }
    for (const node of document.querySelectorAll("[data-native-capability]:not(a)")) {
      node.hidden = !(await allows(node.dataset.nativeCapability.split(/\s+/), node.dataset.flatPermission));
    }
  }
  function apply() { if (window.wmsAdminAuth?.state?.user) { applyNav(); applyPage(); } }
  let pending = document.body.classList.contains("auth-pending");
  new MutationObserver(() => { const now = document.body.classList.contains("auth-pending"); if (pending && !now) apply(); pending = now; })
    .observe(document.body, { attributes: true, attributeFilter: ["class"] });
  window.addEventListener("wms-admin-auth-ready", apply);
  return { load, warehouses, allows, warehouseFromUrl, apply };
})();
