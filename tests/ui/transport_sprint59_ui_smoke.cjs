const path = require("path");
const { createRequire } = require("module");
const { pageUrl } = require("../support/project_config.cjs");

function requirePlaywright() {
  try {
    return require("playwright");
  } catch {
    return createRequire(path.resolve("admin/wms_admin_frontend/package.json"))("playwright");
  }
}

const { chromium } = requirePlaywright();
const APP_URL = process.env.WMS_UI_URL || pageUrl("transport");

const tasks = [
  { ID: 5901, TRANSTYPE: "Тент", TRANSPORT: "Е715ТТ", VODITEL_ID: 1, VODITEL_NAME: "Иванов И.И.", REGIONS: "Пермь", TK_NAME: "ООО Ромашка", SHIPMENT_DATE: "2026-05-25", CONDITION: "Новый", ST_COUNT: 2, PALLET_COUNT: 5, TEMP_WEIGHT: 300, VOLUME_M3: 2.5, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 },
  { ID: 5902, TRANSTYPE: "Реф", TRANSPORT: "А123БВ", VODITEL_ID: 2, VODITEL_NAME: "Петров П.П.", REGIONS: "Лысьва", TK_NAME: null, SHIPMENT_DATE: "2026-05-25", CONDITION: "Отгружен", ST_COUNT: 1, PALLET_COUNT: 8, TEMP_WEIGHT: 500, VOLUME_M3: 3.0, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 },
  { ID: 5903, TRANSTYPE: "Изо", TRANSPORT: "В456ГД", VODITEL_ID: null, VODITEL_NAME: null, REGIONS: "Чусовой", TK_NAME: "ООО Березка", SHIPMENT_DATE: "2026-05-25", CONDITION: "Новый", ST_COUNT: 1, PALLET_COUNT: 3, TEMP_WEIGHT: 150, VOLUME_M3: 1.0, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 50, UNREADY_COUNT: 1 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(tasks) }));
  await page.route("**/api/admin/transport/tasks/*/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function visibleRouteIds(page) {
  return page.locator(".dispatch-routes-table-wrap tbody tr[data-taskid]").evaluateAll(rows => rows.map(row => row.getAttribute("data-taskid")));
}

async function expectIds(page, expected, label) {
  const actual = await visibleRouteIds(page);
  if (JSON.stringify(actual) !== JSON.stringify(expected)) {
    throw new Error(`${label}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
  }
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.addInitScript(() => {
    localStorage.setItem("tms_activeTab", "routes");
    localStorage.setItem("tms_viewMode", "flat");
  });
  await page.goto(APP_URL);
  await page.locator(".dispatch-tab.active", { hasText: "Маршруты" }).waitFor({ timeout: 10000 });
  await expectIds(page, ["5901", "5902", "5903"], "initial");
  const search = page.locator(".dispatch-route-search");

  await search.fill("Е715");
  await expectIds(page, ["5901"], "transport search");
  await search.fill("Петров");
  await expectIds(page, ["5902"], "driver search");
  await search.fill("Березка");
  await expectIds(page, ["5903"], "TK search");
  await search.fill("XYZ-NOTFOUND");
  await page.locator(".dispatch-grid-empty", { hasText: "Нет рейсов по фильтрам" }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-route-search-clear").click();
  await expectIds(page, ["5901", "5902", "5903"], "clear search");

  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
