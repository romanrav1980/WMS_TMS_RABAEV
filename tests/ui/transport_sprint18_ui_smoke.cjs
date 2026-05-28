const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";

const task = { ID: 1801, TRANSTYPE: "10", TRANSPORT: "В 415 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Тест-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 3, PALLET_COUNT: 12, TEMP_WEIGHT: 2400, PRICE: 9000, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
const calls = { recalc: 0, price: 0 };

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/1801/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks/1801/recalculate-price", route => { calls.recalc += 1; task.PRICE = 11000; route.fulfill({ contentType: "application/json", body: JSON.stringify({ task_id: 1801, price: 11000 }) }); });
  await page.route("**/api/admin/transport/tasks/1801/price", route => { calls.price += 1; task.PRICE = 12345; route.fulfill({ contentType: "application/json", body: JSON.stringify({ task_id: 1801, price: 12345 }) }); });
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("1801").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await page.locator(".price-value", { hasText: "9" }).waitFor({ timeout: 5000 });
  await page.getByRole("button", { name: /Пересчитать/ }).click();
  await page.locator(".price-value", { hasText: "11" }).waitFor({ timeout: 5000 });
  await page.locator(".price-input").fill("12345");
  await page.getByRole("button", { name: "Сохранить", exact: true }).click();
  await page.locator(".price-value", { hasText: "12" }).waitFor({ timeout: 5000 });
  if (calls.recalc !== 1 || calls.price !== 1) throw new Error(`Unexpected calls: ${JSON.stringify(calls)}`);
  await browser.close();
  console.log(JSON.stringify({ ok: true, calls }));
}

main().catch(error => { console.error(error); process.exit(1); });
