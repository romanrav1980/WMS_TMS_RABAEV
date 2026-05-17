const customerState = {
  customers: [],
  selectedId: null,
  detail: null,
  productRules: [],
  vehicleTypes: [],
};

const customerEl = (id) => document.getElementById(id);
const CUSTOMER_DEFAULT_API_BASE = "http://127.0.0.1:8088";

function customerApiBase() {
  return (window.wmsAdminAuth?.state?.apiBase || CUSTOMER_DEFAULT_API_BASE).replace(/\/$/, "");
}

function customerHeaders(extra = {}) {
  return window.wmsAdminAuth ? window.wmsAdminAuth.headers(extra) : { ...extra };
}

function customerCan(permission) {
  return window.wmsAdminAuth && window.wmsAdminAuth.hasPermission(permission);
}

function customerUser() {
  return window.wmsAdminAuth?.state?.user?.username || "admin";
}

async function customerRequest(path, options = {}) {
  const response = await fetch(`${customerApiBase()}${path}`, {
    ...options,
    headers: customerHeaders(options.headers || {}),
  });
  const text = await response.text();
  const payload = text ? JSON.parse(text) : null;
  if (!response.ok) {
    throw new Error((payload && payload.detail) || `HTTP ${response.status}`);
  }
  return payload;
}

function customerJson(method, payload) {
  return {
    method,
    headers: { "Content-Type": "application/json; charset=utf-8" },
    body: JSON.stringify(payload),
  };
}

function customerNumber(id) {
  const value = customerEl(id).value;
  return value === "" ? null : Number(value);
}

function customerText(id) {
  const value = customerEl(id).value.trim();
  return value === "" ? null : value;
}

function escapeCustomer(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function customerFilters() {
  const params = new URLSearchParams();
  const search = customerText("customerSearch") || customerText("customerSearchTop");
  if (search) params.set("search", search);
  params.set("limit", customerEl("customerLimit").value || "200");
  return params;
}

async function loadVehicleTypes() {
  if (!customerCan("vehicle_type_view")) return;
  customerState.vehicleTypes = await customerRequest("/api/vehicle-types?active_only=1");
  renderVehicleSelects();
}

function renderVehicleSelects() {
  const options = ['<option value="">Не задано</option>'].concat(
    customerState.vehicleTypes.map((row) =>
      `<option value="${row.vehicle_type_id}">${escapeCustomer(row.vehicle_type_code)} / ${escapeCustomer(row.vehicle_type_name)}</option>`,
    ),
  ).join("");
  customerEl("customerAddressVehicle").innerHTML = options;
}

async function loadCustomers() {
  customerEl("customerStatusText").textContent = "Загрузка...";
  customerState.customers = await customerRequest(`/api/customers?${customerFilters().toString()}`);
  renderCustomers();
  customerEl("customerStatusText").textContent = `Клиентов: ${customerState.customers.length}`;
}

function renderCustomers() {
  const tbody = customerEl("customerRows");
  tbody.innerHTML = "";
  for (const customer of customerState.customers) {
    const tr = document.createElement("tr");
    tr.className = customerState.selectedId === customer.customer_id ? "selected" : "";
    tr.innerHTML = `
      <td>${customer.customer_id ?? ""}</td>
      <td>${escapeCustomer(customer.customer_code)}</td>
      <td>${escapeCustomer(customer.customer_name)}</td>
      <td>${escapeCustomer(customer.customer_type)}</td>
      <td>${Number(customer.active || 0) === 1 ? "Да" : "Нет"}</td>
      <td>${escapeCustomer(customer.legacy_addr || customer.address_text || "")}</td>
    `;
    tr.addEventListener("click", () => loadCustomerDetail(customer.customer_id));
    tbody.appendChild(tr);
  }
}

async function loadCustomerDetail(customerId) {
  customerState.selectedId = customerId;
  customerEl("customerDetailStatus").textContent = "Загрузка...";
  customerState.detail = await customerRequest(`/api/customers/${customerId}`);
  fillCustomerForm(customerState.detail);
  renderCustomers();
  renderCustomerAddresses();
  if (customerCan("customer_rule_view")) {
    await loadCustomerRules(customerId);
  }
  customerEl("customerDetailStatus").textContent = `${customerState.detail.customer_name} / ID ${customerId}`;
}

function fillCustomerForm(customer) {
  customerEl("customerEditCode").value = customer.customer_code || "";
  customerEl("customerEditName").value = customer.customer_name || "";
  customerEl("customerEditType").value = customer.customer_type || "STORE";
  customerEl("customerEditActive").value = String(customer.active ?? 1);
  customerEl("customerEditInn").value = customer.inn || "";
  customerEl("customerEditKpp").value = customer.kpp || "";
  customerEl("customerEditGln").value = customer.gln || "";
  customerEl("customerEditEdi").value = customer.edi_id || "";
  customerEl("customerEditShelfDays").value = customer.default_min_shelf_life_days ?? "";
  customerEl("customerEditShelfPercent").value = customer.default_min_shelf_life_percent ?? "";
}

function customerPayload(mode) {
  const payload = {
    customer_code: customerText("customerEditCode"),
    customer_name: customerText("customerEditName"),
    customer_type: customerEl("customerEditType").value,
    inn: customerText("customerEditInn"),
    kpp: customerText("customerEditKpp"),
    gln: customerText("customerEditGln"),
    edi_id: customerText("customerEditEdi"),
    default_min_shelf_life_days: customerNumber("customerEditShelfDays"),
    default_min_shelf_life_percent: customerNumber("customerEditShelfPercent"),
    active: Number(customerEl("customerEditActive").value || 1),
  };
  if (mode === "create") payload.created_by = customerUser();
  if (mode === "update") payload.updated_by = customerUser();
  return payload;
}

async function createCustomer() {
  const created = await customerRequest("/api/customers", customerJson("POST", customerPayload("create")));
  await loadCustomers();
  await loadCustomerDetail(created.customer_id);
}

async function saveCustomer() {
  if (!customerState.selectedId) throw new Error("Сначала выберите клиента");
  await customerRequest(`/api/customers/${customerState.selectedId}`, customerJson("PATCH", customerPayload("update")));
  await loadCustomers();
  await loadCustomerDetail(customerState.selectedId);
}

async function addCustomerAddress() {
  if (!customerState.selectedId) throw new Error("Сначала выберите клиента");
  await customerRequest(`/api/customers/${customerState.selectedId}/addresses`, customerJson("POST", {
    address_type: customerEl("customerAddressType").value,
    address_text: customerText("customerAddressText"),
    city: customerText("customerAddressCity"),
    region: customerText("customerAddressRegion"),
    postal_code: customerText("customerAddressPostal"),
    gln: customerText("customerAddressGln"),
    vehicle_type_id: customerNumber("customerAddressVehicle"),
    max_pallet_count: customerNumber("customerAddressVehiclePallets"),
    max_weight: customerNumber("customerAddressVehicleWeight"),
    max_volume: customerNumber("customerAddressVehicleVolume"),
    split_order_by_capacity: Number(customerEl("customerAddressSplit").value || 1),
    active: 1,
    created_by: customerUser(),
  }));
  customerEl("customerAddressText").value = "";
  await loadCustomerDetail(customerState.selectedId);
}

function renderCustomerAddresses() {
  const addresses = customerState.detail?.addresses || [];
  customerEl("customerAddressRows").innerHTML = addresses.map((row) => `
    <tr>
      <td>${escapeCustomer(row.address_type)}</td>
      <td>${escapeCustomer(row.address_text)}</td>
      <td>${escapeCustomer(row.city)}</td>
      <td>${escapeCustomer(row.gln)}</td>
      <td>${escapeCustomer(row.vehicle_type_code || row.vehicle_type_name || "")}</td>
      <td>${escapeCustomer(row.max_pallet_count ?? "")}</td>
      <td>${Number(row.active || 0) === 1 ? "Да" : "Нет"}</td>
    </tr>
  `).join("");

  const mappings = customerState.detail?.legacy_mappings || [];
  customerEl("customerMappingRows").innerHTML = mappings.map((row) => `
    <tr>
      <td>${escapeCustomer(row.legacy_addr)}</td>
      <td>${escapeCustomer(row.store_name || row.store_code)}</td>
      <td>${escapeCustomer(row.address_text)}</td>
      <td>${escapeCustomer(row.default_route_id)}</td>
      <td>${escapeCustomer(row.default_dock_id)}</td>
    </tr>
  `).join("");
}

async function loadCustomerRules(customerId) {
  customerState.productRules = await customerRequest(`/api/customers/${customerId}/product-rules`);
  renderCustomerRules();
}

function renderCustomerRules() {
  customerEl("customerRuleRows").innerHTML = customerState.productRules.map((row) => `
    <tr>
      <td>${escapeCustomer(row.articul || row.product_group || "По умолчанию")}</td>
      <td>${escapeCustomer(row.min_shelf_life_days)}</td>
      <td>${escapeCustomer(row.min_shelf_life_percent)}</td>
      <td>${escapeCustomer(row.pallet_case_qty)}</td>
      <td>${escapeCustomer(row.pallet_layer_count)}</td>
      <td>${Number(row.allow_top_stacking || 0) === 1 ? "Да" : "Нет"}</td>
      <td>${Number(row.active || 0) === 1 ? "Да" : "Нет"}</td>
    </tr>
  `).join("");
}

async function addProductRule() {
  if (!customerState.selectedId) throw new Error("Сначала выберите клиента");
  await customerRequest(`/api/customers/${customerState.selectedId}/product-rules`, customerJson("POST", {
    articul: customerText("customerRuleArticul"),
    min_shelf_life_days: customerNumber("customerRuleShelfDays"),
    min_shelf_life_percent: customerNumber("customerRuleShelfPercent"),
    pallet_case_qty: customerNumber("customerStackCases"),
    pallet_layer_count: customerNumber("customerStackLayers"),
    allow_top_stacking: Number(customerEl("customerStackTop").value || 0),
    rule_priority: 100,
    active: 1,
    created_by: customerUser(),
  }));
  await loadCustomerRules(customerState.selectedId);
}

function customerBind(id, handler) {
  customerEl(id).addEventListener("click", async () => {
    try {
      await handler();
    } catch (exc) {
      customerEl("customerDetailStatus").textContent = exc.message;
    }
  });
}

async function customerInit() {
  customerBind("customerLoad", loadCustomers);
  customerBind("customerRefresh", loadCustomers);
  customerBind("customerCreate", createCustomer);
  customerBind("customerSave", saveCustomer);
  customerBind("customerAddAddress", addCustomerAddress);
  customerBind("customerAddProductRule", addProductRule);
  customerEl("customerSearchTop").addEventListener("keydown", (event) => {
    if (event.key === "Enter") loadCustomers();
  });
  await loadVehicleTypes();
  await loadCustomers();
}

window.addEventListener("wms-admin-auth-ready", customerInit);
