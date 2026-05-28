const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const task = { ID: 2501, TRANSTYPE: "10", TRANSPORT: "В 451 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Отвязка-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Отгружен", ST_COUNT: 3, PALLET_COUNT: 12, TEMP_WEIGHT: 2400, PRICE: 12500, PAY_ORDER_ID: 2501, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
const openOrder = { order_id: 2501, num: "B-2501", company: "ООО Отвязка-Транс", date_from: "2026-05-25", date_to: "2026-05-25", closed: 0, payed: 0, total_price: 12500, task_count: 1 };
const registryOrder = { order_id: 2502, num: "B-2502", company: "ООО Отвязка-Транс", date_from: "2026-05-25", date_to: "2026-05-25", closed: 0, payed: 0, total_price: 24000, task_count: 2 };
let detailTasks = [
  { tt_id: 2511, transport: "В 452 ТТ 59", shipment_date: "2026-05-25", status: "Отгружен", price: 12000 },
  { tt_id: 2512, transport: "В 453 ТТ 59", shipment_date: "2026-05-25", status: "Отгружен", price: 12000 },
];
const calls = { cardDetach: 0, detailDetach: 0 };

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/2501/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/orders/2501", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(openOrder) }));
  await page.route("**/api/admin/transport/billing/orders/2501/tasks/2501", route => { calls.cardDetach += 1; task.PAY_ORDER_ID = null; route.fulfill({ contentType: "application/json", body: JSON.stringify({ removed: true }) }); });
  await page.route("**/api/admin/transport/billing/orders?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([registryOrder]) }));
  await page.route("**/api/admin/transport/billing/orders/2502/tasks", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(detailTasks) }));
  await page.route("**/api/admin/transport/billing/orders/2502/tasks/2511", route => { calls.detailDetach += 1; detailTasks = detailTasks.filter(t => t.tt_id !== 2511); route.fulfill({ contentType: "application/json", body: JSON.stringify({ removed: true }) }); });
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  page.on("dialog", dialog => dialog.accept());
  await installMocks(page);
  await page.goto(APP_URL);

  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("2501").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await page.getByRole("button", { name: "Снять с биллинга" }).click();
  await page.getByRole("button", { name: "Выставить счёт" }).waitFor({ timeout: 5000 });

  await page.getByRole("button", { name: "Биллинг" }).click();
  await page.getByText("B-2502").waitFor({ timeout: 10000 });
  await page.getByText("B-2502").click();
  await page.getByText("#2511").waitFor({ timeout: 5000 });
  await page.locator(".billing-detach-task-btn").first().click();
  await page.getByText("#2511").waitFor({ state: "hidden", timeout: 5000 });
  if (calls.cardDetach !== 1 || calls.detailDetach !== 1) throw new Error(`Unexpected calls: ${JSON.stringify(calls)}`);

  await browser.close();
  console.log(JSON.stringify({ ok: true, calls }));
}

main().catch(error => { console.error(error); process.exit(1); });
