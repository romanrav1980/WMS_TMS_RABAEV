const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint19_link_existing_billing_2026_05_28");

// This file intentionally reuses the smoke scenario shape but writes a compact training page.
async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const task = { ID: 1901, TRANSTYPE: "10", TRANSPORT: "В 415 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Тест-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Отгружен", ST_COUNT: 3, PALLET_COUNT: 12, TEMP_WEIGHT: 2400, PRICE: 12500, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
  const openOrders = [{ order_id: 9901, num: "B-9901", company: "ООО Тест-Транс", date_from: "2026-05-01", date_to: "2026-05-31", closed: 0, payed: 0, total_price: 50000, task_count: 4 }];
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/1901/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/companies", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(["ООО Тест-Транс"]) }));
  await page.route("**/api/admin/transport/billing/orders?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(openOrders) }));
  await page.route("**/api/admin/transport/billing/orders/9901/tasks", route => { task.PAY_ORDER_ID = 9901; route.fulfill({ contentType: "application/json", body: JSON.stringify({ order_id: 9901, added: 1 }) }); });
  await page.route("**/api/admin/transport/billing/orders/9901", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(openOrders[0]) }));
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("1901").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_task.png"), fullPage: true });
  await page.getByRole("button", { name: "Выставить счёт" }).click();
  await page.getByText("Привязать к счёту").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_choose_existing.png"), fullPage: true });
  await page.getByText("B-9901").click();
  await page.getByRole("button", { name: "Добавить к счёту" }).click();
  await page.getByText("Счёт #9901").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_linked.png"), fullPage: true });
  await browser.close();
  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 19</title></head><body><h1>ТМС-2 Sprint 19: Привязка к существующему счёту</h1><p>Блок нужен, чтобы добавлять рейс в уже открытый счет той же транспортной компании вместо создания нового.</p><h2>Бизнес-процесс</h2><ol><li>Открыть отгруженный рейс.</li><li>Нажать «Выставить счёт».</li><li>Выбрать открытый счет ТК.</li><li>Нажать «Добавить к счёту».</li></ol><img src="screenshots/01_task.png" width="100%"><img src="screenshots/02_choose_existing.png" width="100%"><img src="screenshots/03_linked.png" width="100%"><p>Проверка: backend <code>9 passed</code>, UI smoke/load passed.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
