const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const task = { ID: 2201, TRANSTYPE: "10", TRANSPORT: "В 422 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Справочник-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Отгружен", ST_COUNT: 3, PALLET_COUNT: 12, TEMP_WEIGHT: 2400, PRICE: 12500, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
const orders = [
  { order_id: 2202, num: "B-2202", company: "ООО Справочник-Транс", date_from: "2026-05-01", date_to: "2026-05-31", closed: 0, payed: 0, total_price: 50000, task_count: 4, num_plat: "ПП-2202" },
];
const calls = { companies: 0, list: 0 };

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/2201/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/companies", route => { calls.companies += 1; route.fulfill({ contentType: "application/json", body: JSON.stringify(["ООО Справочник-Транс", "ООО Вторая ТК"]) }); });
  await page.route("**/api/admin/transport/billing/orders?**", route => { calls.list += 1; route.fulfill({ contentType: "application/json", body: JSON.stringify(orders) }); });
  await page.route("**/api/admin/transport/billing/orders/2202/tasks", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ tt_id: 2201, transport: "В 422 ТТ 59", shipment_date: "2026-05-25", status: "Отгружен", price: 12500 }]) }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);

  await page.getByRole("button", { name: "Биллинг" }).click();
  await page.getByText("B-2202").waitFor({ timeout: 10000 });
  await page.getByText("ПП-2202").waitFor({ timeout: 5000 });
  await page.getByText("B-2202").click();
  await page.getByText("№ плат.: ПП-2202").waitFor({ timeout: 5000 });

  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("2201").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await page.getByRole("button", { name: "Выставить счёт" }).click();
  await page.locator(".billing-dialog-company", { hasText: "ООО Справочник-Транс" }).waitFor({ timeout: 5000 });
  const option = await page.locator("#billing-companies-list option").first().getAttribute("value");
  if (option !== "ООО Справочник-Транс") throw new Error(`Company datalist not populated: ${option}`);
  if (calls.companies < 1 || calls.list < 1) throw new Error(`Unexpected calls: ${JSON.stringify(calls)}`);

  await browser.close();
  console.log(JSON.stringify({ ok: true, calls }));
}

main().catch(error => { console.error(error); process.exit(1); });
