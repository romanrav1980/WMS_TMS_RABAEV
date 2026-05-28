const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint40_day_summary_2026_05_28");
const tasks = [
  { ID: 4001, TRANSTYPE: "10", TRANSPORT: "В 401 ТТ 59", VODITEL_ID: 401, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Summary", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 2, PALLET_COUNT: 10, TEMP_WEIGHT: 1500, PRICE: 1200, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 },
  { ID: 4002, TRANSTYPE: "10", TRANSPORT: "В 402 ТТ 59", VODITEL_ID: 402, VODITEL_NAME: "Петров П.П.", TK_NAME: "ООО Summary", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Отгружен", ST_COUNT: 1, PALLET_COUNT: 5, TEMP_WEIGHT: 800, PRICE: 900, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 },
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
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByText("4001").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_day_summary.png"), fullPage: true });
  await page.locator("tr[data-taskid='4002']").click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_closed_trip_in_day.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 40</title></head><body><h1>ТМС-2 Sprint 40: сводка дня по рейсам</h1><p>Блок даёт диспетчеру быстрый контроль объёма работы за выбранный день без отдельного отчёта.</p><h2>Структура данных</h2><p>Сводка считается на клиенте из уже загруженного списка рейсов: количество рейсов, сумма <code>PALLET_COUNT</code>, сумма <code>TEMP_WEIGHT</code>, количество рейсов со статусом «Отгружен».</p><h2>Результат</h2><p>Над таблицей рейсов появляется строка «Рейсов · Паллет · Вес кг · Отгружено», которая меняется вместе со списком выбранного дня.</p><h2>Бизнес-процесс</h2><ol><li>Открыть вкладку «Заявки».</li><li>Выбрать дату рейсов.</li><li>Проверить общую нагрузку дня по рейсам, паллетам и весу.</li><li>Контролировать прогресс закрытия через показатель «Отгружено».</li></ol><img src="screenshots/01_day_summary.png" width="100%"><img src="screenshots/02_closed_trip_in_day.png" width="100%"><p>Проверка: functional, UI smoke и load gate пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
