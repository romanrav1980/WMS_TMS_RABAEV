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
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint54_selected_st_csv_2026_05_29");

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

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ acceptDownloads: true, viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.addInitScript(() => {
    localStorage.setItem("tms_activeTab", "tasks");
    localStorage.setItem("tms_viewMode", "flat");
    localStorage.setItem("tms_stDate", "2026-05-25");
  });
  await page.goto(pageUrl("transport"));
  await page.getByText("CSV-ST-001").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_available_sts.png"), fullPage: true });
  await page.locator(".dispatch-st-section tbody input[type='checkbox']").nth(0).check();
  await page.locator(".dispatch-st-section tbody input[type='checkbox']").nth(1).check();
  await page.locator(".dispatch-sel-bar-count", { hasText: "2 выбр." }).waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_selection_bar_csv.png"), fullPage: true });
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.locator(".dispatch-sel-bar-csv").click(),
  ]);
  const csvPath = await download.path();
  const csv = fs.readFileSync(csvPath, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "selected-sts-2026-05-25.csv"), csv, "utf8");
  await browser.close();

  const escapedCsv = csv.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 54</title></head><body><h1>ТМС-2 Sprint 54: CSV выделенных СТ</h1><p>Блок нужен для быстрой передачи выбранных заявок во внешний разбор, сверку или ручной маршрутный файл.</p><h2>Структура данных</h2><p>CSV строится на клиенте из текущего множества выделенных СТ: номер, адрес, регион, район, паллеты, вес, объем, готовность, тип ТС и рейс. Файл UTF-8 с BOM и разделителем <code>;</code>.</p><h2>Бизнес-процесс</h2><ol><li>Диспетчер выделяет нужные СТ.</li><li>Панель выделения показывает количество и итоги.</li><li>Кнопка <code>CSV</code> скачивает файл <code>selected-sts-YYYY-MM-DD.csv</code>.</li><li>Последняя строка содержит итог по паллетам и весу.</li></ol><h2>Результат</h2><p>Sprint 54 закрыт functional, load и UI smoke проверками.</p><img src="screenshots/01_available_sts.png" width="100%"><img src="screenshots/02_selection_bar_csv.png" width="100%"><h2>Фрагмент CSV</h2><pre>${escapedCsv}</pre></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR, filename: download.suggestedFilename() }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
