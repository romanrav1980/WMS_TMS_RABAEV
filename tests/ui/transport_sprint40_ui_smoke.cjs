const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const APP_URL = process.env.WMS_UI_URL || pageUrl("transport");
const tasks = [
  { ID: 4001, TRANSTYPE: "10", TRANSPORT: "В 401 ТТ 59", VODITEL_ID: 401, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Summary", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 2, PALLET_COUNT: 10, TEMP_WEIGHT: 1500, PRICE: 1200, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 },
  { ID: 4002, TRANSTYPE: "10", TRANSPORT: "В 402 ТТ 59", VODITEL_ID: 402, VODITEL_NAME: "Петров П.П.", TK_NAME: "ООО Summary", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Отгружен", ST_COUNT: 1, PALLET_COUNT: 5, TEMP_WEIGHT: 800, PRICE: 900, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(tasks) }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByText("4001").waitFor({ timeout: 10000 });
  const summary = page.locator(".dispatch-day-summary");
  await summary.waitFor({ timeout: 5000 });
  for (const text of ["Рейсов", "2", "Паллет", "15", "Вес кг", "2300", "Отгружено", "1 / 2"]) {
    await summary.getByText(text, { exact: true }).waitFor({ timeout: 5000 });
  }
  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => { console.error(error); process.exit(1); });
