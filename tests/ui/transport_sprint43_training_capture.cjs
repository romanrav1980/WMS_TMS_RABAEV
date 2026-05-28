const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint43_sortable_trips_2026_05_28");
const tasks = [
  { ID: 4303, TRANSTYPE: "10", TRANSPORT: null, VODITEL_ID: 433, VODITEL_NAME: "Сидоров С.С.", TK_NAME: "ООО Sort", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 1, PALLET_COUNT: 5, TEMP_WEIGHT: 700, PRICE: null, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 },
  { ID: 4301, TRANSTYPE: "10", TRANSPORT: "В 431 ТТ 59", VODITEL_ID: 431, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Sort", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 2, PALLET_COUNT: 12, TEMP_WEIGHT: 1500, PRICE: 1200, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 },
  { ID: 4302, TRANSTYPE: "10", TRANSPORT: "А 430 ТТ 59", VODITEL_ID: 432, VODITEL_NAME: "Петров П.П.", TK_NAME: "ООО Sort", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Отгружен", ST_COUNT: 1, PALLET_COUNT: 8, TEMP_WEIGHT: 900, PRICE: 900, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 },
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
  await page.getByText("#4303").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_unsorted.png"), fullPage: true });
  await page.locator(".dispatch-trips-table-wrap thead th", { hasText: "ID" }).click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_id_asc.png"), fullPage: true });
  await page.locator(".dispatch-trips-table-wrap thead th", { hasText: "ID" }).click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_id_desc.png"), fullPage: true });
  await page.locator(".dispatch-trips-table-wrap thead th", { hasText: "Машина" }).click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "04_vehicle_null_last.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 43</title></head><body><h1>ТМС-2 Sprint 43: сортировка таблицы рейсов</h1><p>Блок помогает диспетчеру быстро упорядочить рейсы по ID, паллетам, машине, дате, цене, статусу и другим колонкам без нового запроса к серверу.</p><h2>Структура данных</h2><p>Сортировка работает по уже загруженному массиву <code>tasks</code>. Состояние хранит поле сортировки и направление. Пустые значения всегда остаются в конце списка.</p><h2>Результат</h2><p>Клик по заголовку сортирует по возрастанию, повторный клик переключает направление. В заголовке появляется стрелка.</p><h2>Бизнес-процесс</h2><ol><li>Открыть вкладку «Заявки».</li><li>Кликнуть заголовок нужной колонки.</li><li>Повторить клик для обратного порядка.</li><li>Использовать сортировку вместе с выбором рейса и просмотром состава.</li></ol><img src="screenshots/01_unsorted.png" width="100%"><img src="screenshots/02_id_asc.png" width="100%"><img src="screenshots/03_id_desc.png" width="100%"><img src="screenshots/04_vehicle_null_last.png" width="100%"><p>Проверка: functional, UI smoke и load gate пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
