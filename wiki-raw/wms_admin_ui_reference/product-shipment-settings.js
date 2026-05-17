const productState = {
  products: [],
  selected: null,
};

const productEl = (id) => document.getElementById(id);

function productApiBase() {
  return (window.wmsAdminAuth?.state?.apiBase || "http://127.0.0.1:8088").replace(/\/$/, "");
}

function productHeaders(extra = {}) {
  if (!window.wmsAdminAuth) return { ...extra };
  return window.wmsAdminAuth.headers(extra);
}

function productCan(permission) {
  return window.wmsAdminAuth && window.wmsAdminAuth.hasPermission(permission);
}

function productFilters() {
  const params = new URLSearchParams();
  const search = productEl("productSearch").value.trim();
  if (search) params.set("articul_like", search);
  if (productEl("productOnlyAging").value) params.set("only_with_aging", productEl("productOnlyAging").value);
  params.set("limit", productEl("productLimit").value || "200");
  return params;
}

async function loadProducts() {
  productEl("productStatusText").textContent = "Загрузка...";
  const response = await fetch(`${productApiBase()}/api/admin/product-shipment-settings?${productFilters().toString()}`, {
    headers: productHeaders(),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Product settings HTTP ${response.status}`);
  productState.products = result;
  renderProducts();
  productEl("productStatusText").textContent = `Артикулов: ${productState.products.length}`;
}

function renderProducts() {
  const tbody = productEl("productRows");
  tbody.innerHTML = "";
  for (const product of productState.products) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeProduct(product.acticul ?? "")}</td>
      <td>${escapeProduct(product.name ?? "")}</td>
      <td>${escapeProduct(product.unit_type ?? "")}</td>
      <td>${product.shipment_aging_hours ?? 0}</td>
      <td>${escapeProduct(product.shipment_aging_comment ?? "")}</td>
    `;
    tr.addEventListener("click", () => selectProduct(product));
    tbody.appendChild(tr);
  }
}

function selectProduct(product) {
  productState.selected = product;
  productEl("productDetailStatus").textContent = product.acticul || "Артикул";
  productEl("productDetails").textContent = JSON.stringify(product, null, 2);
  productEl("productAgingHours").value = product.shipment_aging_hours ?? 0;
  productEl("productAgingComment").value = product.shipment_aging_comment || "";
}

async function saveProduct() {
  if (!productState.selected) throw new Error("Выберите артикул");
  if (!productCan("quality_batch_edit")) throw new Error("Нет права quality_batch_edit");
  const body = {
    shipment_aging_hours: Number(productEl("productAgingHours").value || 0),
    shipment_aging_comment: productEl("productAgingComment").value.trim() || null,
  };
  const response = await fetch(
    `${productApiBase()}/api/admin/product-shipment-settings/${encodeURIComponent(productState.selected.acticul)}`,
    {
      method: "PATCH",
      headers: productHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(body),
    },
  );
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Save product settings HTTP ${response.status}`);
  await loadProducts();
  const updated = productState.products.find((row) => row.acticul === productState.selected.acticul);
  if (updated) selectProduct(updated);
}

function initProducts() {
  if (!productEl("productRefresh")) return;
  if (window.wmsAdminAuth && !window.wmsAdminAuth.hasPermission("quality_batch_view")) return;
  productEl("productRefresh").addEventListener("click", () => loadProducts().catch(showProductError));
  productEl("productLoad").addEventListener("click", () => loadProducts().catch(showProductError));
  productEl("productSave").addEventListener("click", () => saveProduct().catch(showProductError));
  productEl("productOnlyAging").addEventListener("change", () => loadProducts().catch(showProductError));
  productEl("productLimit").addEventListener("change", () => loadProducts().catch(showProductError));
  productEl("productSearch").addEventListener("input", () => loadProducts().catch(showProductError));
  loadProducts().catch(showProductError);
}

function showProductError(error) {
  productEl("productStatusText").textContent = `Ошибка: ${error.message}`;
  productEl("productDetailStatus").textContent = `Ошибка: ${error.message}`;
}

function escapeProduct(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

document.addEventListener("DOMContentLoaded", () => {
  if (window.wmsAdminAuth) {
    window.wmsAdminAuth.initPage().then(initProducts).catch(showProductError);
  } else {
    initProducts();
  }
});
