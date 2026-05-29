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
  { ST_NUMBER: "SORT-ST-003", ADDR: "В", REGION: "Пермь", RAION: "Центр", ORD: 3, TRANSPORT_TYPE: "Тент", WARE_ID: 9201, NAPR: "Пермь", PALLETS_COUNT: 12, WEIGHT_KG: 800, VOLUME_M3: 6, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 100 },
  { ST_NUMBER: "SORT-ST-001", ADDR: "А", REGION: "Лысьва", RAION: "Лысьва", ORD: 1, TRANSPORT_TYPE: "Реф", WARE_ID: 9202, NAPR: "Лысьва", PALLETS_COUNT: 5, WEIGHT_KG: 300, VOLUME_M3: 2.5, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: 42, VERIFY_PERC: 50 },
  { ST_NUMBER: "SORT-ST-002", ADDR: "Б", REGION: "Чусовой", RAION: null, ORD: 2, TRANSPORT_TYPE: null, WARE_ID: 9201, NAPR: "Чусовой", PALLETS_COUNT: 8, WEIGHT_KG: 500, VOLUME_M3: 3, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: null },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(rows) }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function visibleStNumbers(page) {
  return page.locator(".dispatch-st-section tbody tr .dispatch-gc-stnum").allInnerTexts();
}

function assertOrder(actual, expected, label) {
  const got = actual.slice(0, expected.length);
  if (JSON.stringify(got) !== JSON.stringify(expected)) {
    throw new Error(`${label}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(got)}`);
  }
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByText("SORT-ST-003").waitFor({ timeout: 10000 });
  const stSection = page.locator(".dispatch-st-section");

  await stSection.getByRole("columnheader", { name: /СТ №/ }).click();
  assertOrder(await visibleStNumbers(page), ["SORT-ST-001", "SORT-ST-002", "SORT-ST-003"], "ST_NUMBER asc");

  await stSection.getByRole("columnheader", { name: /СТ №/ }).click();
  assertOrder(await visibleStNumbers(page), ["SORT-ST-003", "SORT-ST-002", "SORT-ST-001"], "ST_NUMBER desc");

  await stSection.getByRole("columnheader", { name: "%", exact: true }).click();
  assertOrder(await visibleStNumbers(page), ["SORT-ST-001", "SORT-ST-003", "SORT-ST-002"], "VERIFY_PERC asc null-last");

  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
