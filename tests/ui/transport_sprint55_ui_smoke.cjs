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
  { ST_NUMBER: "TOT-ST-001", ADDR: "Первый", REGION: "Пермь", RAION: "Центр", ORD: 1, TRANSPORT_TYPE: "Тент", WARE_ID: 9201, NAPR: "Пермь", PALLETS_COUNT: 5, WEIGHT_KG: 300, VOLUME_M3: 2.5, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 100 },
  { ST_NUMBER: "TOT-ST-002", ADDR: "Второй", REGION: "Лысьва", RAION: "Север", ORD: 2, TRANSPORT_TYPE: "Реф", WARE_ID: 9202, NAPR: "Лысьва", PALLETS_COUNT: 8, WEIGHT_KG: 500, VOLUME_M3: 3.0, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 75 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(sts) }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.addInitScript(() => {
    localStorage.setItem("tms_activeTab", "tasks");
    localStorage.setItem("tms_viewMode", "flat");
  });
  await page.goto(APP_URL);
  await page.getByText("TOT-ST-001").waitFor({ timeout: 10000 });
  const totals = page.locator(".dispatch-pmv-all");
  await totals.filter({ hasText: "П=13" }).filter({ hasText: "800 кг" }).filter({ hasText: "5.5 м³" }).waitFor({ timeout: 5000 });

  await page.locator(".dispatch-st-section tbody input[type='checkbox']").nth(0).check();
  await page.locator(".dispatch-sel-bar-stat", { hasText: "P=5" }).waitFor({ timeout: 5000 });
  await totals.filter({ hasText: "П=13" }).filter({ hasText: "800 кг" }).waitFor({ timeout: 5000 });

  await page.locator(".dispatch-ware-select").selectOption("9201");
  await totals.filter({ hasText: "П=5" }).filter({ hasText: "300 кг" }).filter({ hasText: "2.5 м³" }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-tcount", { hasText: "1 / 2 СТ" }).waitFor({ timeout: 5000 });

  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
