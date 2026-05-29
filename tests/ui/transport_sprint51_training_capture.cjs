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
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint51_selection_bar_2026_05_29");

const sts = [
  { ST_NUMBER: "SEL-ST-001", ADDR: "Первый", REGION: "Екб", RAION: "R1", ORD: 1, TRANSPORT_TYPE: "10", WARE_ID: 9201, NAPR: "Екб", PALLETS_COUNT: 5, WEIGHT_KG: 300, VOLUME_M3: 2.5, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 100 },
  { ST_NUMBER: "SEL-ST-002", ADDR: "Второй", REGION: "Екб", RAION: "R1", ORD: 2, TRANSPORT_TYPE: "10", WARE_ID: 9201, NAPR: "Екб", PALLETS_COUNT: 8, WEIGHT_KG: 500, VOLUME_M3: 3.0, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 75 },
];
const tasks = [{ ID: 5101, TRANSTYPE: "10", TRANSPORT: "А001АА", VODITEL_ID: 1, VODITEL_NAME: "Иванов", SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Спланирован", ST_COUNT: 0, PALLET_COUNT: 0, TEMP_WEIGHT: 0, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 0, UNREADY_COUNT: 0 }];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(sts) }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(tasks) }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks/*/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(pageUrl("transport"));
  await page.getByText("SEL-ST-001").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_no_selection.png"), fullPage: true });
  await page.locator(".dispatch-st-section tbody input[type='checkbox']").nth(0).check();
  await page.locator(".dispatch-st-section tbody input[type='checkbox']").nth(1).check();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_selection_bar_totals.png"), fullPage: true });
  await page.locator(".dispatch-trips-table-wrap tbody tr", { hasText: "5101" }).click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_add_to_selected_trip.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 51</title></head><body><h1>ТМС-2 Sprint 51: закреплённая панель выделения</h1><p>Панель показывает диспетчеру масштаб выбранных СТ и быстрые действия без прокрутки к тулбару.</p><h2>Структура данных</h2><p>Панель строится из выбранных <code>selectedStNums</code> и агрегирует <code>PALLETS_COUNT</code>, <code>WEIGHT_KG</code>, <code>VOLUME_M3</code>. Если выбран рейс, появляется действие <code>Добавить в #ID</code>.</p><h2>Бизнес-процесс</h2><ol><li>Выделить одну или несколько СТ.</li><li>Проверить count/P/M/V.</li><li>Создать новый маршрут или добавить СТ в выбранный рейс.</li><li>Снять выделение кнопкой закрытия.</li></ol><h2>Результат</h2><p>Sprint 51 закрыт functional, load и UI smoke проверками.</p><img src="screenshots/01_no_selection.png" width="100%"><img src="screenshots/02_selection_bar_totals.png" width="100%"><img src="screenshots/03_add_to_selected_trip.png" width="100%"></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
