const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const APP_URL = process.env.WMS_UI_URL || pageUrl("transport");
const tasks = [
  { ID: 4101, TRANSTYPE: "10", TRANSPORT: "В 411 ТТ 59", VODITEL_ID: 411, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Status", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 2, PALLET_COUNT: 10, TEMP_WEIGHT: 1500, PRICE: 1200, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 },
  { ID: 4102, TRANSTYPE: "10", TRANSPORT: "В 412 ТТ 59", VODITEL_ID: 412, VODITEL_NAME: "Петров П.П.", TK_NAME: "ООО Status", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Отгружен", ST_COUNT: 1, PALLET_COUNT: 5, TEMP_WEIGHT: 800, PRICE: 900, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 },
  { ID: 4103, TRANSTYPE: "10", TRANSPORT: "В 413 ТТ 59", VODITEL_ID: 413, VODITEL_NAME: "Сидоров С.С.", TK_NAME: "ООО Status", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Отменён", ST_COUNT: 1, PALLET_COUNT: 2, TEMP_WEIGHT: 200, PRICE: 100, PAY_ORDER_ID: null, DELETED: 1, READY_PERC: 0, UNREADY_COUNT: 1 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(tasks) }));
}

async function rowIds(page) {
  return page.locator(".dispatch-routes-table-wrap tbody tr").evaluateAll(rows => rows.map(r => r.textContent));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("4101").waitFor({ timeout: 10000 });

  const filter = page.locator(".dispatch-cond-filter");
  await filter.getByRole("button", { name: /Отгружен/ }).click();
  await page.getByText("4102").waitFor({ timeout: 5000 });
  if ((await rowIds(page)).some(text => text.includes("4101") || text.includes("4103"))) {
    throw new Error("Closed filter shows non-closed rows");
  }

  await filter.getByRole("button", { name: /Отменён/ }).click();
  await page.getByText("4103").waitFor({ timeout: 5000 });
  if ((await rowIds(page)).some(text => text.includes("4101") || text.includes("4102"))) {
    throw new Error("Cancelled filter shows non-cancelled rows");
  }

  await filter.getByRole("button", { name: /Все/ }).click();
  for (const id of ["4101", "4102", "4103"]) await page.getByText(id).waitFor({ timeout: 5000 });
  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => { console.error(error); process.exit(1); });
