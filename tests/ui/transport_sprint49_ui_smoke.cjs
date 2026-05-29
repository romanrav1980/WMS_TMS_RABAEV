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

function makeRows(count) {
  return Array.from({ length: count }, (_, idx) => {
    const n = idx + 1;
    return {
      ST_NUMBER: `DENSE-ST-${String(n).padStart(4, "0")}`,
      ADDR: `Адрес ${n}`,
      REGION: "Екатеринбург",
      RAION: `Район ${n % 5}`,
      ORD: n,
      TRANSPORT_TYPE: "10",
      NEEDS_HYDRO_BOARD: 0,
      STOL: 0,
      PRIM1: "",
      WARE_ID: 9201,
      NAPR: "Екб",
      PALLETS_COUNT: 1,
      WEIGHT_KG: 100,
      VOLUME_M3: 0.5,
      STDATE: "2026-05-25T00:00:00",
      DATE_LOAD: "2026-05-25T00:00:00",
      TRANSTASK_ID: null,
      VERIFY_PERC: 100,
      SUGAR: 0,
    };
  });
}

async function installMocks(page) {
  const rows = makeRows(200);
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

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.locator(".dispatch-shell").waitFor({ timeout: 10000 });
  await page.getByText("DENSE-ST-0001").waitFor({ timeout: 10000 });

  const toggle = page.locator(".dispatch-dense-toggle input");
  const table = page.locator(".dispatch-st-section table");
  const firstDataRow = page.locator(".dispatch-st-section tbody tr").first();
  assert(await toggle.isChecked() === false, "dense mode should be off by default");
  assert(!String(await table.getAttribute("class")).includes("dispatch-grid-dense"), "table should not start dense");

  const beforeHeight = (await firstDataRow.boundingBox())?.height || 0;
  await page.locator(".dispatch-st-section tbody input[type='checkbox']").first().check();
  await page.locator(".dispatch-sel-bar-count", { hasText: "1 выбр." }).waitFor({ timeout: 5000 });

  await toggle.check();
  assert(String(await table.getAttribute("class")).includes("dispatch-grid-dense"), "dense class was not applied");
  const denseHeight = (await firstDataRow.boundingBox())?.height || 0;
  assert(denseHeight > 0 && beforeHeight > 0, `row heights must be measurable: ${beforeHeight} -> ${denseHeight}`);
  assert(denseHeight < beforeHeight, `dense mode should reduce row height: ${beforeHeight} -> ${denseHeight}`);
  await page.locator(".dispatch-sel-bar-count", { hasText: "1 выбр." }).waitFor({ timeout: 5000 });

  await toggle.uncheck();
  assert(!String(await table.getAttribute("class")).includes("dispatch-grid-dense"), "dense class was not removed");
  await page.locator(".dispatch-sel-bar-count", { hasText: "1 выбр." }).waitFor({ timeout: 5000 });

  await browser.close();
  console.log(JSON.stringify({ ok: true, beforeHeight, denseHeight }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
