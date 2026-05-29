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
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint52_st_sorting_2026_05_29");

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

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(pageUrl("transport"));
  await page.getByText("SORT-ST-003").waitFor({ timeout: 10000 });
  const stSection = page.locator(".dispatch-st-section");
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_original_order.png"), fullPage: true });
  await stSection.getByRole("columnheader", { name: /СТ №/ }).click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_st_number_asc.png"), fullPage: true });
  await stSection.getByRole("columnheader", { name: "%", exact: true }).click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_verify_asc_null_last.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 52</title></head><body><h1>ТМС-2 Sprint 52: сортировка таблицы СТ</h1><p>Диспетчер сортирует доступные СТ прямо в таблице, не запрашивая новые данные с сервера.</p><h2>Структура данных</h2><p>Клиент хранит <code>stSortField</code> и <code>stSortDir</code>. Повторный клик меняет направление. Пустые значения сортируются последними.</p><h2>Бизнес-процесс</h2><ol><li>Кликнуть заголовок «СТ №» для сортировки по номеру.</li><li>Повторить клик для обратного направления.</li><li>Кликнуть «%», чтобы вывести частично/полностью собранные СТ с пустыми значениями в конце.</li></ol><h2>Результат</h2><p>Sprint 52 закрыт functional, load и UI smoke проверками.</p><img src="screenshots/01_original_order.png" width="100%"><img src="screenshots/02_st_number_asc.png" width="100%"><img src="screenshots/03_verify_asc_null_last.png" width="100%"></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
