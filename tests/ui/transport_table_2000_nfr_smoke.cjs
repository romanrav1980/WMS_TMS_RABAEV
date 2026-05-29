const path = require("path");
const { createRequire } = require("module");
const { pageUrl } = require("../support/project_config.cjs");

function requirePlaywright() {
  try {
    return require("playwright");
  } catch {
    const adminRequire = createRequire(path.resolve("admin/wms_admin_frontend/package.json"));
    return adminRequire("playwright");
  }
}

const { chromium } = requirePlaywright();
const APP_URL = process.env.WMS_UI_URL || pageUrl("transport");

function makeRows(count) {
  return Array.from({ length: count }, (_, idx) => {
    const n = idx + 1;
    return {
      ST_NUMBER: `NFR-ST-${String(n).padStart(5, "0")}`,
      ADDR: `NFR адрес ${n}`,
      REGION: n % 2 === 0 ? "Пермь" : "Екатеринбург",
      RAION: `Район ${n % 12}`,
      ORD: n,
      TRANSPORT_TYPE: n % 3 === 0 ? "15" : "10",
      NEEDS_HYDRO_BOARD: n % 5 === 0 ? 1 : 0,
      STOL: n % 7 === 0 ? 1 : 0,
      PRIM1: n % 11 === 0 ? "контроль" : "",
      WARE_ID: 9201 + (n % 3),
      NAPR: n % 2 === 0 ? "Пермь" : "Екб",
      PALLETS_COUNT: 1 + (n % 6),
      WEIGHT_KG: 100 + n,
      VOLUME_M3: Number((0.5 + (n % 8) / 10).toFixed(2)),
      STDATE: "2026-05-25T00:00:00",
      DATE_LOAD: "2026-05-25T00:00:00",
      TRANSTASK_ID: null,
      VERIFY_PERC: n % 4 === 0 ? 100 : 0,
      SUGAR: n % 9 === 0 ? 1 : 0
    };
  });
}

const rows = makeRows(2000);

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "10т" }, { TRANSPORTTYPE: "15", NAME: "15т" }])
  }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify(rows)
  }));
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);

  const started = Date.now();
  await page.goto(APP_URL);
  await page.getByRole("heading", { name: "Диспетчер отгрузки" }).waitFor({ timeout: 10000 });
  await page.getByText("NFR-ST-00001").waitFor({ timeout: 10000 });
  const firstRenderMs = Date.now() - started;
  assert(firstRenderMs < 4000, `2000-row first render too slow: ${firstRenderMs}ms`);

  const section = page.locator(".dispatch-st-section");
  await section.waitFor({ timeout: 5000 });
  assert(await section.getAttribute("data-virtualized") === "true", "ST section virtualization flag is not set");

  const renderedRows = await page.locator(".dispatch-st-section tbody tr").count();
  assert(renderedRows <= 70, `Too many rendered ST table rows: ${renderedRows}`);

  await page.locator(".dispatch-page-info", { hasText: "Всего СТ: 2000" }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-page-info", { hasText: "виртуализация активна" }).waitFor({ timeout: 5000 });

  await section.evaluate(el => { el.scrollTop = 800; el.dispatchEvent(new Event("scroll", { bubbles: true })); });
  await page.waitForTimeout(100);
  const renderedAfterScroll = await page.locator(".dispatch-st-section tbody tr").count();
  assert(renderedAfterScroll <= 70, `Too many rows after scroll: ${renderedAfterScroll}`);

  const firstCheckbox = page.locator(".dispatch-st-section tbody input[type='checkbox']").first();
  await firstCheckbox.check();
  await page.locator(".dispatch-sel-bar-count", { hasText: "1 выбр." }).waitFor({ timeout: 5000 });

  await section.evaluate(el => { el.scrollTop = el.scrollHeight - el.clientHeight; el.dispatchEvent(new Event("scroll", { bubbles: true })); });
  await page.waitForTimeout(150);
  await page.getByText("NFR-ST-02000").waitFor({ timeout: 5000 });
  const renderedAtBottom = await page.locator(".dispatch-st-section tbody tr").count();
  assert(renderedAtBottom <= 70, `Too many rows at virtualized bottom: ${renderedAtBottom}`);

  await browser.close();
  console.log(JSON.stringify({ ok: true, firstRenderMs, renderedRows, renderedAfterScroll, renderedAtBottom }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
