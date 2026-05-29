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
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint50_ready_highlight_2026_05_29");

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

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(pageUrl("transport"));
  await page.getByText("READY-ST-100").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_ready_vs_partial.png"), fullPage: true });
  await page.locator(".dispatch-st-section tbody tr", { hasText: "READY-ST-100" }).first().locator("input[type='checkbox']").check();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_selected_ready_row.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 50</title></head><body><h1>ТМС-2 Sprint 50: подсветка полностью собранных СТ</h1><p>Диспетчер быстрее видит, какие свободные СТ уже полностью собраны и готовы к включению в рейс.</p><h2>Структура данных</h2><p>Поле <code>VERIFY_PERC</code> приходит в строке доступной СТ. Значение <code>100</code> добавляет класс <code>dispatch-st-ready</code>; частичные и пустые значения не подсвечиваются.</p><h2>Бизнес-процесс</h2><ol><li>Открыть список доступных СТ.</li><li>Найти строки с 100% сборкой по зеленой полосе.</li><li>Выделить нужные СТ; selected-состояние имеет приоритет над подсветкой.</li></ol><h2>Результат</h2><p>Sprint 50 закрыт functional, load и UI smoke проверками.</p><img src="screenshots/01_ready_vs_partial.png" width="100%"><img src="screenshots/02_selected_ready_row.png" width="100%"></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
