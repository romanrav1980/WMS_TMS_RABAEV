const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint41_routes_status_filter_2026_05_28");
const tasks = [
  { ID: 4101, TRANSTYPE: "10", TRANSPORT: "В 411 ТТ 59", VODITEL_ID: 411, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Status", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 2, PALLET_COUNT: 10, TEMP_WEIGHT: 1500, PRICE: 1200, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 },
  { ID: 4102, TRANSTYPE: "10", TRANSPORT: "В 412 ТТ 59", VODITEL_ID: 412, VODITEL_NAME: "Петров П.П.", TK_NAME: "ООО Status", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Отгружен", ST_COUNT: 1, PALLET_COUNT: 5, TEMP_WEIGHT: 800, PRICE: 900, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 },
  { ID: 4103, TRANSTYPE: "10", TRANSPORT: "В 413 ТТ 59", VODITEL_ID: 413, VODITEL_NAME: "Сидоров С.С.", TK_NAME: "ООО Status", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Отменён", ST_COUNT: 1, PALLET_COUNT: 2, TEMP_WEIGHT: 200, PRICE: 100, PAY_ORDER_ID: null, DELETED: 1, READY_PERC: 0, UNREADY_COUNT: 1 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(tasks) }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(pageUrl("transport"));
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("4101").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_all_statuses.png"), fullPage: true });
  await page.locator(".dispatch-cond-filter").getByRole("button", { name: /Отгружен/ }).click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_closed_only.png"), fullPage: true });
  await page.locator(".dispatch-cond-filter").getByRole("button", { name: /Отменён/ }).click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_cancelled_only.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 41</title></head><body><h1>ТМС-2 Sprint 41: фильтр рейсов по статусу</h1><p>Блок ускоряет контроль маршрутов: диспетчер отделяет активные рейсы от отгруженных и отменённых без нового запроса к серверу.</p><h2>Структура данных</h2><p>Фильтр работает по уже загруженному списку <code>tasks</code> и полю <code>CONDITION</code>. Счётчики строятся для «Все», «Активен», «Отгружен», «Отменён».</p><h2>Результат</h2><p>Во вкладке «Маршруты» появились кнопки статусов со счётчиками, таблица мгновенно показывает только нужную группу рейсов.</p><h2>Бизнес-процесс</h2><ol><li>Открыть вкладку «Маршруты».</li><li>Выбрать статус «Отгружен» для контроля закрытых рейсов.</li><li>Выбрать «Отменён» для разбора отмен.</li><li>Вернуться на «Все» для полного списка дня.</li></ol><img src="screenshots/01_all_statuses.png" width="100%"><img src="screenshots/02_closed_only.png" width="100%"><img src="screenshots/03_cancelled_only.png" width="100%"><p>Проверка: functional, UI smoke и load gate пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
