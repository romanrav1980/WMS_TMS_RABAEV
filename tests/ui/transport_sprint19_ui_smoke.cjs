const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const task = { ID: 1901, TRANSTYPE: "10", TRANSPORT: "В 415 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Тест-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Отгружен", ST_COUNT: 3, PALLET_COUNT: 12, TEMP_WEIGHT: 2400, PRICE: 12500, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
const openOrders = [{ order_id: 9901, num: "B-9901", company: "ООО Тест-Транс", date_from: "2026-05-01", date_to: "2026-05-31", closed: 0, payed: 0, total_price: 50000, task_count: 4 }];
const calls = { add: 0, list: 0 };

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/1901/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/companies", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(["ООО Тест-Транс"]) }));
  await page.route("**/api/admin/transport/billing/orders?**", route => { calls.list += 1; route.fulfill({ contentType: "application/json", body: JSON.stringify(openOrders) }); });
  await page.route("**/api/admin/transport/billing/orders/9901/tasks", route => { calls.add += 1; task.PAY_ORDER_ID = 9901; route.fulfill({ contentType: "application/json", body: JSON.stringify({ order_id: 9901, added: 1 }) }); });
  await page.route("**/api/admin/transport/billing/orders/9901", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(openOrders[0]) }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("1901").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await page.getByRole("button", { name: "Выставить счёт" }).click();
  await page.getByText("Привязать к счёту").waitFor({ timeout: 5000 });
  await page.getByText("B-9901").click();
  await page.getByRole("button", { name: "Добавить к счёту" }).click();
  await page.getByText("Счёт #9901").waitFor({ timeout: 5000 });
  if (calls.add !== 1 || calls.list < 1) throw new Error(`Unexpected calls: ${JSON.stringify(calls)}`);
  await browser.close();
  console.log(JSON.stringify({ ok: true, calls }));
}

main().catch(error => { console.error(error); process.exit(1); });
