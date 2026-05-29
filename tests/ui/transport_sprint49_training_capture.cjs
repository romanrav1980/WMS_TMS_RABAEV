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
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint49_dense_mode_2026_05_29");

function makeRows(count) {
  return Array.from({ length: count }, (_, idx) => ({
    ST_NUMBER: `DENSE-ST-${String(idx + 1).padStart(4, "0")}`,
    ADDR: `Адрес ${idx + 1}`,
    REGION: "Екатеринбург",
    RAION: `Район ${idx % 5}`,
    ORD: idx + 1,
    TRANSPORT_TYPE: "10",
    WARE_ID: 9201,
    NAPR: "Екб",
    PALLETS_COUNT: 1,
    WEIGHT_KG: 100,
    VOLUME_M3: 0.5,
    STDATE: "2026-05-25T00:00:00",
    DATE_LOAD: "2026-05-25T00:00:00",
    TRANSTASK_ID: null,
    VERIFY_PERC: 100,
  }));
}

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(makeRows(200)) }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(pageUrl("transport"));
  await page.getByText("DENSE-ST-0001").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_normal_mode.png"), fullPage: true });
  await page.locator(".dispatch-dense-toggle input").check();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_dense_mode.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 49</title></head><body><h1>ТМС-2 Sprint 49: компактный режим таблицы СТ</h1><p>Компактный режим помогает диспетчеру просматривать больше строк доступных СТ без потери выбора и действий.</p><h2>Структура данных</h2><p>Состояние <code>stDenseMode</code> применяет класс <code>dispatch-grid-dense</code> и переключает расчетную высоту строк virtualizer с 27 до 22 px.</p><h2>Бизнес-процесс</h2><ol><li>Открыть вкладку «Заявки».</li><li>Включить «Компактно» в тулбаре таблицы СТ.</li><li>Сканировать больше строк в той же высоте таблицы.</li><li>Отключить режим при необходимости, выделение сохраняется.</li></ol><h2>Результат</h2><p>Sprint 49 закрыт functional, load и UI smoke проверками.</p><img src="screenshots/01_normal_mode.png" width="100%"><img src="screenshots/02_dense_mode.png" width="100%"></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
