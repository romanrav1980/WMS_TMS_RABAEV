const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const task = { ID: 3401, TRANSTYPE: "10", TRANSPORT: "В 501 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Cancel-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 1, PALLET_COUNT: 4, TEMP_WEIGHT: 800, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
const taskSts = [{ ST_NUMBER: "СТ-3401", PALLETS_COUNT: 4, WEIGHT_KG: 800, VOLUME_M3: 3, ORD: 1, WARE_ID: 9201, VERIFY_PERC: 100 }];

async function installMocks(page) {
  let tasksReloaded = false;
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(tasksReloaded ? [] : [task]) }));
  await page.route("**/api/admin/transport/tasks/3401/sts", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(taskSts) }));
  await page.route("**/api/admin/transport/tasks/3401/cancel", route => {
    tasksReloaded = true;
    return route.fulfill({ contentType: "application/json", body: "{}" });
  });
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  page.on("dialog", dialog => dialog.accept());
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("3401").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await page.getByRole("button", { name: "Отменить" }).click();
  await page.getByText("Рейс #3401 отменён").waitFor({ timeout: 5000 });
  await page.getByText("Нет рейсов").waitFor({ timeout: 5000 });
  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => { console.error(error); process.exit(1); });
