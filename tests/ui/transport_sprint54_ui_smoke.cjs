const fs = require("fs");
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
  { ST_NUMBER: "CSV-ST-001", ADDR: "ул. Ленина 1", REGION: "Пермь", RAION: "Центр", ORD: 1, TRANSPORT_TYPE: "Тент", WARE_ID: 9201, NAPR: "Пермь", PALLETS_COUNT: 5, WEIGHT_KG: 300, VOLUME_M3: 2.5, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 1 },
  { ST_NUMBER: "CSV-ST-002", ADDR: "пр. Мира 10", REGION: "Лысьва", RAION: null, ORD: 2, TRANSPORT_TYPE: "Реф", WARE_ID: 9202, NAPR: "Лысьва", PALLETS_COUNT: 8, WEIGHT_KG: 500, VOLUME_M3: 3, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: 42, VERIFY_PERC: 0.5 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(sts) }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

function assertIncludes(text, expected) {
  if (!text.includes(expected)) {
    throw new Error(`CSV missing ${JSON.stringify(expected)} in ${JSON.stringify(text)}`);
  }
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ acceptDownloads: true, viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.addInitScript(() => {
    localStorage.setItem("tms_activeTab", "tasks");
    localStorage.setItem("tms_viewMode", "flat");
    localStorage.setItem("tms_stDate", "2026-05-25");
  });
  await page.goto(APP_URL);
  await page.getByText("CSV-ST-001").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-st-section tbody input[type='checkbox']").nth(0).check();
  await page.locator(".dispatch-st-section tbody input[type='checkbox']").nth(1).check();
  await page.locator(".dispatch-sel-bar-count", { hasText: "2 выбр." }).waitFor({ timeout: 5000 });

  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.locator(".dispatch-sel-bar-csv").click(),
  ]);
  if (download.suggestedFilename() !== "selected-sts-2026-05-25.csv") {
    throw new Error(`Unexpected filename: ${download.suggestedFilename()}`);
  }
  const filePath = await download.path();
  const csv = fs.readFileSync(filePath, "utf8");
  if (!csv.startsWith("\uFEFF")) throw new Error("CSV has no UTF-8 BOM");
  assertIncludes(csv, "СТ №;Адрес;Регион;Район;Паллет;Вес кг;Объём м³;% сборки;Тип ТС;Рейс");
  assertIncludes(csv, "CSV-ST-001;ул. Ленина 1;Пермь;Центр;5;300;2.50;100%;Тент;");
  assertIncludes(csv, "CSV-ST-002;пр. Мира 10;Лысьва;;8;500;3.00;50%;Реф;#42");
  assertIncludes(csv, "ИТОГО;;;;13;800;;;;");

  await browser.close();
  console.log(JSON.stringify({ ok: true, filename: download.suggestedFilename() }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
