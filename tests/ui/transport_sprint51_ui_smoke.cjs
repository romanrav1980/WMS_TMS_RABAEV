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

const sts = [
  { ST_NUMBER: "SEL-ST-001", ADDR: "Первый", REGION: "Екб", RAION: "R1", ORD: 1, TRANSPORT_TYPE: "10", WARE_ID: 9201, NAPR: "Екб", PALLETS_COUNT: 5, WEIGHT_KG: 300, VOLUME_M3: 2.5, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 100 },
  { ST_NUMBER: "SEL-ST-002", ADDR: "Второй", REGION: "Екб", RAION: "R1", ORD: 2, TRANSPORT_TYPE: "10", WARE_ID: 9201, NAPR: "Екб", PALLETS_COUNT: 8, WEIGHT_KG: 500, VOLUME_M3: 3.0, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 75 },
];

const tasks = [
  { ID: 5101, TRANSTYPE: "10", TRANSPORT: "А001АА", VODITEL_ID: 1, VODITEL_NAME: "Иванов", SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Спланирован", ST_COUNT: 0, PALLET_COUNT: 0, TEMP_WEIGHT: 0, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 0, UNREADY_COUNT: 0 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(sts) }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(tasks) }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks/*/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByText("SEL-ST-001").waitFor({ timeout: 10000 });

  if (await page.locator(".dispatch-sel-bar").count() !== 0) throw new Error("selection bar should be hidden initially");
  await page.locator(".dispatch-st-section tbody input[type='checkbox']").nth(0).check();
  await page.locator(".dispatch-st-section tbody input[type='checkbox']").nth(1).check();
  await page.locator(".dispatch-sel-bar-count", { hasText: "2 выбр." }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-sel-bar-stat", { hasText: "P=13" }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-sel-bar-stat", { hasText: "M=800 кг" }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-sel-bar-stat", { hasText: "V=5.50 м³" }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-sel-bar-create", { hasText: "+ Создать маршрут" }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-sel-bar-csv").waitFor({ timeout: 5000 });

  await page.locator(".dispatch-trips-table-wrap tbody tr", { hasText: "5101" }).click();
  await page.locator(".dispatch-sel-bar-add", { hasText: "Добавить в #5101" }).waitFor({ timeout: 5000 });

  await page.locator(".dispatch-sel-bar-clear").click();
  if (await page.locator(".dispatch-sel-bar").count() !== 0) throw new Error("clear button should hide selection bar");

  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
