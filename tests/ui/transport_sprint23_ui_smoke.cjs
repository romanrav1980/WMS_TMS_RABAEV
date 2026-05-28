const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const orders = [
  { order_id: 2301, num: "B-2301", company: "ООО Детали-Транс", date_from: "2026-05-01", date_to: "2026-05-31", closed: 0, payed: 0, total_price: 25000, task_count: 2, num_plat: "ПП-2301" },
];
const orderTasks = [
  { tt_id: 2311, transport: "В 431 ТТ 59", shipment_date: "2026-05-25", status: "Отгружен", price: 12500 },
  { tt_id: 2312, transport: "В 432 ТТ 59", shipment_date: "2026-05-26", status: "Отгружен", price: 12500 },
];
const calls = { tasks: 0 };

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/orders?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(orders) }));
  await page.route("**/api/admin/transport/billing/orders/2301/tasks", route => { calls.tasks += 1; route.fulfill({ contentType: "application/json", body: JSON.stringify(orderTasks) }); });
  await page.route("**/api/admin/transport/billing/orders/2301/export.xlsx", route => route.fulfill({ contentType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", body: "xlsx" }));
}

async function main() {
  const browser = await chromium.launch();
  const context = await browser.newContext({ acceptDownloads: true, viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Биллинг" }).click();
  await page.getByText("B-2301").waitFor({ timeout: 10000 });
  await page.getByText("B-2301").click();
  await page.getByText("#2311").waitFor({ timeout: 5000 });
  await page.getByText("#2312").waitFor({ timeout: 5000 });
  await page.getByText("Итого:").waitFor({ timeout: 5000 });
  const downloadPromise = page.waitForEvent("download");
  await page.locator(".billing-detail-export-row .billing-csv-btn").click();
  await downloadPromise;
  if (calls.tasks !== 1) throw new Error(`Expected one tasks request, got ${JSON.stringify(calls)}`);
  await browser.close();
  console.log(JSON.stringify({ ok: true, calls }));
}

main().catch(error => { console.error(error); process.exit(1); });
