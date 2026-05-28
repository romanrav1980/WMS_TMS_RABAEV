const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint20_billed_task_protection_2026_05_28");

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const task = { ID: 2001, TRANSTYPE: "10", TRANSPORT: "В 415 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Тест-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 3, PALLET_COUNT: 12, TEMP_WEIGHT: 2400, PRICE: 12500, PAY_ORDER_ID: 7701, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/2001/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/orders/7701", route => route.fulfill({ contentType: "application/json", body: JSON.stringify({ order_id: 7701, num: "B-7701", company: "ООО Тест-Транс", date_from: "2026-05-25", date_to: "2026-05-25", closed: 0, payed: 0, total_price: 12500 }) }));
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("2001").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await page.getByText("Счёт #7701").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_billed_task.png"), fullPage: true });
  await browser.close();
  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 20</title></head><body><h1>ТМС-2 Sprint 20: Защита выставленного рейса</h1><p>Блок защищает рейсы с <code>PAY_ORDER_ID</code>: нельзя отменить рейс или менять состав, пока рейс находится в счёте.</p><h2>Бизнес-процессы</h2><ol><li>Рейс выставлен в счёт.</li><li>Карточка показывает тег счёта.</li><li>Опасные действия блокируются UI и backend возвращает 409.</li><li>Цена и примечание остаются разрешенными по ТЗ.</li></ol><img src="screenshots/01_billed_task.png" width="100%"><p>Проверка: backend <code>7 passed</code>, UI smoke/load passed.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
