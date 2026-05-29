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
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint59_route_search_2026_05_29");

const tasks = [
  { ID: 5901, TRANSTYPE: "Тент", TRANSPORT: "Е715ТТ", VODITEL_ID: 1, VODITEL_NAME: "Иванов И.И.", REGIONS: "Пермь", TK_NAME: "ООО Ромашка", SHIPMENT_DATE: "2026-05-25", CONDITION: "Новый", ST_COUNT: 2, PALLET_COUNT: 5, TEMP_WEIGHT: 300, VOLUME_M3: 2.5, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 },
  { ID: 5902, TRANSTYPE: "Реф", TRANSPORT: "А123БВ", VODITEL_ID: 2, VODITEL_NAME: "Петров П.П.", REGIONS: "Лысьва", TK_NAME: null, SHIPMENT_DATE: "2026-05-25", CONDITION: "Отгружен", ST_COUNT: 1, PALLET_COUNT: 8, TEMP_WEIGHT: 500, VOLUME_M3: 3.0, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 },
  { ID: 5903, TRANSTYPE: "Изо", TRANSPORT: "В456ГД", VODITEL_ID: null, VODITEL_NAME: null, REGIONS: "Чусовой", TK_NAME: "ООО Березка", SHIPMENT_DATE: "2026-05-25", CONDITION: "Новый", ST_COUNT: 1, PALLET_COUNT: 3, TEMP_WEIGHT: 150, VOLUME_M3: 1.0, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 50, UNREADY_COUNT: 1 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(tasks) }));
  await page.route("**/api/admin/transport/tasks/*/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.addInitScript(() => {
    localStorage.setItem("tms_activeTab", "routes");
    localStorage.setItem("tms_viewMode", "flat");
  });
  await page.goto(pageUrl("transport"));
  await page.locator(".dispatch-tab.active", { hasText: "Маршруты" }).waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_all_routes.png"), fullPage: true });
  await page.locator(".dispatch-route-search").fill("Петров");
  await page.locator(".dispatch-routes-table-wrap tbody tr[data-taskid='5902']").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_driver_search.png"), fullPage: true });
  await page.locator(".dispatch-route-search").fill("XYZ-NOTFOUND");
  await page.locator(".dispatch-grid-empty", { hasText: "Нет рейсов по фильтрам" }).waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_no_match.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 59</title></head><body><h1>ТМС-2 Sprint 59: быстрый поиск по маршрутам</h1><p>Блок помогает диспетчеру быстро найти рейс по номеру, машине, водителю, региону или транспортной компании без нового запроса к серверу.</p><h2>Структура данных</h2><p>Поиск работает на клиенте по загруженному списку <code>tasks</code> после фильтра статуса. Поля: <code>ID</code>, <code>TRANSPORT</code>, <code>VODITEL_NAME</code>, <code>REGIONS</code>, <code>TK_NAME</code>.</p><h2>Бизнес-процесс</h2><ol><li>Открыть вкладку «Маршруты».</li><li>Ввести часть номера машины, ФИО водителя, регион или ТК.</li><li>Проверить отфильтрованную таблицу и счётчик.</li><li>Очистить поиск кнопкой «×».</li></ol><h2>Результат</h2><p>Sprint 59 закрыт functional, load и UI smoke проверками.</p><img src="screenshots/01_all_routes.png" width="100%"><img src="screenshots/02_driver_search.png" width="100%"><img src="screenshots/03_no_match.png" width="100%"></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
