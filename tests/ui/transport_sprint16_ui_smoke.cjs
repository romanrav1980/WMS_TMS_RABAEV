const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";

const task = {
  ID: 1601,
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
  PAY_ORDER_ID: 8801,
  DELETED: 0,
  READY_PERC: 100,
  UNREADY_COUNT: 0,
};

let order = {
  order_id: 8801,
  num: "B-8801",
  company: "ООО Тест-Транс",
  date_from: "2026-05-25",
  date_to: "2026-05-25",
  closed: 0,
  payed: 0,
  total_price: 12500,
  task_count: 1,
  num_plat: null,
};

const calls = { getOrder: 0, close: 0, pay: 0 };

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/1601/sts", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/orders/8801", (route) => {
    calls.getOrder += 1;
    route.fulfill({ contentType: "application/json", body: JSON.stringify(order) });
  });
  await page.route("**/api/admin/transport/billing/orders/8801/close", (route) => {
    calls.close += 1;
    order = { ...order, closed: 1 };
    route.fulfill({ contentType: "application/json", body: JSON.stringify({ order_id: 8801, closed: true }) });
  });
  await page.route("**/api/admin/transport/billing/orders/8801/pay", (route) => {
    calls.pay += 1;
    order = { ...order, closed: 1, payed: 1 };
    route.fulfill({ contentType: "application/json", body: JSON.stringify({ order_id: 8801, payed: true }) });
  });
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  page.on("dialog", dialog => dialog.accept());
  await installMocks(page);

  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("1601").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await page.getByText("B-8801").waitFor({ timeout: 5000 });
  await page.getByText("Выставлен").waitFor({ timeout: 5000 });
  await page.getByRole("button", { name: "Закрыть счёт" }).click();
  await page.getByText("Закрыт").waitFor({ timeout: 5000 });
  await page.getByRole("button", { name: "Отметить оплаченным" }).click();
  await page.getByText("Счёт закрыт и оплачен").waitFor({ timeout: 5000 });

  if (calls.close !== 1 || calls.pay !== 1 || calls.getOrder < 1) {
    throw new Error(`Unexpected billing lifecycle calls: ${JSON.stringify(calls)}`);
  }

  await browser.close();
  console.log(JSON.stringify({ ok: true, calls }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
