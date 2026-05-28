const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const APP_URL = process.env.WMS_UI_URL || pageUrl("transport");
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

async function ids(page) {
  return page.locator(".dispatch-trips-table-wrap tbody tr").evaluateAll(rows => rows.map(r => Number((r.getAttribute("data-taskid") || "0"))));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByText("#4303").waitFor({ timeout: 10000 });

  await page.locator(".dispatch-trips-table-wrap thead th", { hasText: "ID" }).click();
  if ((await ids(page)).join(",") !== "4301,4302,4303") throw new Error(`ID asc failed: ${(await ids(page)).join(",")}`);
  await page.locator(".dispatch-trips-table-wrap thead th", { hasText: "ID" }).click();
  if ((await ids(page)).join(",") !== "4303,4302,4301") throw new Error(`ID desc failed: ${(await ids(page)).join(",")}`);

  await page.locator(".dispatch-trips-table-wrap thead th", { hasText: "Машина" }).click();
  if ((await ids(page)).join(",") !== "4302,4301,4303") throw new Error(`Transport asc/null-last failed: ${(await ids(page)).join(",")}`);
  await page.locator(".dispatch-trips-table-wrap thead th", { hasText: "Машина" }).click();
  if ((await ids(page)).join(",") !== "4301,4302,4303") throw new Error(`Transport desc/null-last failed: ${(await ids(page)).join(",")}`);

  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => { console.error(error); process.exit(1); });
