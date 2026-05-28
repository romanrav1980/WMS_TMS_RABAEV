const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const task = {
  ID: 2101,
  TRANSTYPE: "10",
  TRANSPORT: "В 421 ТТ 59",
  VODITEL_ID: 501,
  VODITEL_NAME: "Иванов И.И.",
  TK_NAME: "ООО RBAC-Транс",
  IS_OWN_DRIVER: 0,
  SHIPMENT_DATE: "2026-05-25T00:00:00",
  CONDITION: "Новый",
  ST_COUNT: 3,
  PALLET_COUNT: 12,
  TEMP_WEIGHT: 2400,
  PRICE: 12500,
  PAY_ORDER_ID: null,
  DELETED: 0,
  READY_PERC: 100,
  UNREADY_COUNT: 0
};

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/2101/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/orders?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/companies", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(["ООО RBAC-Транс"]) }));
  await page.route("**/api/admin/transport/tasks/2101/recalculate-price", route => route.fulfill({ status: 403, contentType: "application/json", body: JSON.stringify({ detail: "missing calc_tt_price" }) }));
  await page.route("**/api/admin/transport/tasks/2101/price", route => route.fulfill({ status: 403, contentType: "application/json", body: JSON.stringify({ detail: "missing create_tt_price" }) }));
  await page.route("**/api/admin/transport/tasks/2101/billing/open", route => route.fulfill({ status: 403, contentType: "application/json", body: JSON.stringify({ detail: "missing edit_bill_tt" }) }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("2101").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();

  await page.getByRole("button", { name: /Пересчитать/ }).click();
  await page.locator(".dispatch-error").waitFor({ timeout: 5000 });
  const recalcError = await page.locator(".dispatch-error").innerText();
  if (!recalcError.includes("403")) throw new Error(`Expected recalculation 403 error, got: ${recalcError}`);
  await page.locator(".dispatch-error").click();

  await page.locator(".price-input").fill("12345");
  await page.locator(".price-save-btn").click();
  await page.locator(".dispatch-error").waitFor({ timeout: 5000 });
  const manualError = await page.locator(".dispatch-error").innerText();
  if (!manualError.includes("403")) throw new Error(`Expected manual price 403 error, got: ${manualError}`);

  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => { console.error(error); process.exit(1); });
