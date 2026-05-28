const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";

const task = {
  ID: 1501,
  TRANSTYPE: "10",
  TRANSPORT: "В 415 ТТ 59",
  VODITEL_ID: 501,
  VODITEL_NAME: "Иванов И.И.",
  TK_NAME: "ООО Тест-Транс",
  IS_OWN_DRIVER: 0,
  SHIPMENT_DATE: "2026-05-25T00:00:00",
  CONDITION: "Отгружен",
  ST_COUNT: 3,
  PALLET_COUNT: 12,
  TEMP_WEIGHT: 2400,
  PRICE: 12500,
  PAY_ORDER_ID: null,
  DELETED: 0,
  READY_PERC: 100,
  UNREADY_COUNT: 0,
};

const calls = { open: 0, companies: 0, existing: 0 };

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент 10т" }]) }));
  await page.route("**/api/admin/transport/available-sts?**", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/1501/sts", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/companies", (route) => {
    calls.companies += 1;
    route.fulfill({ contentType: "application/json", body: JSON.stringify(["ООО Тест-Транс"]) });
  });
  await page.route("**/api/admin/transport/billing/orders?**", (route) => {
    calls.existing += 1;
    route.fulfill({ contentType: "application/json", body: "[]" });
  });
  await page.route("**/api/admin/transport/tasks/1501/billing/open", (route) => {
    calls.open += 1;
    task.PAY_ORDER_ID = 7701;
    route.fulfill({ contentType: "application/json", body: JSON.stringify({ order_id: 7701 }) });
  });
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);

  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("1501").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await page.getByText("Рейс #1501").waitFor({ timeout: 5000 });
  await page.getByRole("button", { name: "Выставить счёт" }).click();
  await page.getByText("Транспортная компания").waitFor({ timeout: 5000 });
  await page.locator(".billing-dialog-company", { hasText: "ООО Тест-Транс" }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-dialog", { hasText: "12" }).locator("text=/500\\s*₽/").waitFor({ timeout: 5000 });
  await page.getByRole("button", { name: "Создать счёт" }).click();
  await page.getByText("Счёт #7701").waitFor({ timeout: 5000 });

  if (calls.open !== 1 || calls.companies < 1 || calls.existing < 1) {
    throw new Error(`Unexpected billing calls: ${JSON.stringify(calls)}`);
  }

  await browser.close();
  console.log(JSON.stringify({ ok: true, calls }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
