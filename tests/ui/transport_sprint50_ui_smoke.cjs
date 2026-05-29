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

const rows = [
  { ST_NUMBER: "READY-ST-100", ADDR: "Готовая СТ", REGION: "Екб", RAION: "Готово", ORD: 1, TRANSPORT_TYPE: "10", WARE_ID: 9201, NAPR: "Екб", PALLETS_COUNT: 1, WEIGHT_KG: 100, VOLUME_M3: 0.5, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 100, SUGAR: 0 },
  { ST_NUMBER: "READY-ST-075", ADDR: "Частичная СТ", REGION: "Екб", RAION: "Частично", ORD: 2, TRANSPORT_TYPE: "10", WARE_ID: 9201, NAPR: "Екб", PALLETS_COUNT: 1, WEIGHT_KG: 100, VOLUME_M3: 0.5, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 75, SUGAR: 0 },
  { ST_NUMBER: "READY-ST-NULL", ADDR: "Без сборки", REGION: "Екб", RAION: "Нет", ORD: 3, TRANSPORT_TYPE: "10", WARE_ID: 9201, NAPR: "Екб", PALLETS_COUNT: 1, WEIGHT_KG: 100, VOLUME_M3: 0.5, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: null, SUGAR: 0 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(rows) }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function rowFor(page, stNumber) {
  return page.locator(".dispatch-st-section tbody tr", { hasText: stNumber }).first();
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByText("READY-ST-100").waitFor({ timeout: 10000 });

  const readyRow = await rowFor(page, "READY-ST-100");
  const partialRow = await rowFor(page, "READY-ST-075");
  const nullRow = await rowFor(page, "READY-ST-NULL");
  assert(String(await readyRow.getAttribute("class")).includes("dispatch-st-ready"), "100% row should have ready class");
  assert(!String(await partialRow.getAttribute("class")).includes("dispatch-st-ready"), "75% row must not have ready class");
  assert(!String(await nullRow.getAttribute("class")).includes("dispatch-st-ready"), "null verify row must not have ready class");

  await readyRow.locator("input[type='checkbox']").check();
  assert(!String(await readyRow.getAttribute("class")).includes("dispatch-st-ready"), "selected row should suppress ready class");
  await page.locator(".dispatch-sel-bar-count", { hasText: "1 выбр." }).waitFor({ timeout: 5000 });

  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
