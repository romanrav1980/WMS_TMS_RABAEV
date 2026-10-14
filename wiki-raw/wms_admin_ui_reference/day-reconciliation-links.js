// NI07.2 (C-0010): переходы из обзора сверки в существующие реестры с сохранением склада, даты и ID.
// Параметры передаются только тем экранам, которые их действительно читают (проверено по их коду);
// для остальных переход честно подписан: склад и дату нужно указать на экране реестра.
(() => {
  // Экран → какие параметры он читает из адреса.
  const ACCEPTS = {
    "store-investigations.html": ["case_id"],
    "interwarehouse.html": ["warehouse_id"],
    "supplier-handover.html": ["warehouse_id"],
    "logistics-costs.html": ["warehouse_id"],
    "store-return-receiving.html": ["warehouse_id"],
    "store-return-putaway.html": ["warehouse_id"],
    "supplier-return.html": ["warehouse_id"],
    "return-disposal.html": ["warehouse_id"],
    "interwarehouse-groups.html": ["warehouse_id"],          // interwarehouse-groups.js: query.get("warehouse_id")
    "logistics-expenses.html": ["warehouse_id", "operation_id"], // logistics-expenses-actions.js: deep link
    "warehouse-tasks.html": ["preset", "task_id"],            // warehouse-tasks.js: preset, task_id (склад — из учётной записи)
    "pallet-composition.html": ["identifier"],
    "day-reconciliation.html": ["warehouse_id", "day"]
  };
  const page = href => href.split(/[?#]/)[0];

  // Ссылка с переносом контекста: склад и дата операционного дня из прочитанного ответа сверки.
  function build(link, context) {
    if (!link || link.kind !== "registry") return { href: link?.href || "", carried: [], lost: [] };
    const accepts = ACCEPTS[page(link.href)] || [];
    const values = { warehouse_id: context?.warehouse_id, day: context?.business_date, ...(link.params || {}) };
    const query = new URLSearchParams();
    for (const name of accepts) if (values[name] != null && values[name] !== "") query.set(name, String(values[name]));
    const carried = [...query.keys()];
    const lost = [];
    if (context?.warehouse_id != null && !carried.includes("warehouse_id")) lost.push("склад " + context.warehouse_id);
    if (context?.business_date && !carried.includes("day")) lost.push("дату " + context.business_date);
    return { href: page(link.href) + (carried.length ? "?" + query : ""), carried, lost };
  }

  // Прямая ссылка на саму сверку: ?warehouse_id=&day=. Возвращает только проверенные значения.
  function read() {
    const q = new URLSearchParams(location.search);
    const ware = Number(q.get("warehouse_id")), day = q.get("day") || "";
    return {
      ware: Number.isSafeInteger(ware) && ware > 0 ? ware : null,
      day: /^\d{4}-\d{2}-\d{2}$/.test(day) && !Number.isNaN(Date.parse(day + "T00:00:00Z")) ? day : null
    };
  }
  // После чтения сверки адрес страницы указывает на тот же склад и день: «назад» из реестра возвращает этот контекст.
  function write(ware, day) {
    try {
      const q = new URLSearchParams(location.search);
      q.set("warehouse_id", String(ware)); q.set("day", day);
      history.replaceState(history.state, "", location.pathname + "?" + q + location.hash);
    } catch {}
  }
  window.dayReconLinks = { build, read, write, ACCEPTS };
})();
