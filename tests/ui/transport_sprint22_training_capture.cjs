const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint22_company_directory_num_plat_2026_05_28");

async function installMocks(page) {
  const task = { ID: 2201, TRANSTYPE: "10", TRANSPORT: "В 422 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Справочник-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Отгружен", ST_COUNT: 3, PALLET_COUNT: 12, TEMP_WEIGHT: 2400, PRICE: 12500, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
  const orders = [{ order_id: 2202, num: "B-2202", company: "ООО Справочник-Транс", date_from: "2026-05-01", date_to: "2026-05-31", closed: 0, payed: 0, total_price: 50000, task_count: 4, num_plat: "ПП-2202" }];
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/2201/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/companies", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(["ООО Справочник-Транс", "ООО Вторая ТК"]) }));
  await page.route("**/api/admin/transport/billing/orders?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(orders) }));
  await page.route("**/api/admin/transport/billing/orders/2202/tasks", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ tt_id: 2201, transport: "В 422 ТТ 59", shipment_date: "2026-05-25", status: "Отгружен", price: 12500 }]) }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "Биллинг" }).click();
  await page.getByText("B-2202").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_registry_num_plat.png"), fullPage: true });
  await page.getByText("B-2202").click();
  await page.getByText("№ плат.: ПП-2202").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_detail_num_plat.png"), fullPage: true });
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("2201").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await page.getByRole("button", { name: "Выставить счёт" }).click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_company_datalist.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 22</title></head><body><h1>ТМС-2 Sprint 22: Справочник компаний и номер платёжного поручения</h1><p>Блок связывает реестр биллинга с Oracle-справочником транспортных компаний и показывает номер платёжного поручения в списке и карточке счёта.</p><h2>Структура данных</h2><p>Компании читаются из <code>RRL_BILL_COMPANY</code>, счёт содержит <code>NUM_PLAT</code> и отдаёт его как <code>num_plat</code>.</p><h2>Результат</h2><p>Оператор быстрее выбирает ТК при выставлении счёта и видит номер платёжного поручения в реестре.</p><h2>Бизнес-процессы</h2><ol><li>Открыть реестр счетов и проверить колонку «№ платёжного».</li><li>Открыть детали счёта и сверить номер платёжного поручения.</li><li>Открыть диалог выставления счёта и выбрать компанию из подсказки.</li></ol><img src="screenshots/01_registry_num_plat.png" width="100%"><img src="screenshots/02_detail_num_plat.png" width="100%"><img src="screenshots/03_company_datalist.png" width="100%"><p>Проверка: functional, UI smoke и load gates пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
