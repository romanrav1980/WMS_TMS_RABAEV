const WMS_ADMIN_NAV_ITEMS = [
  { key: "home", label: "Главная", href: "index.html", icon: "home" },
  { key: "production", label: "Производство", href: "index.html", icon: "production" },
  { key: "mes", label: "MES", href: "production-orders.html", icon: "mes", permission: "mes_production_view" },
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
