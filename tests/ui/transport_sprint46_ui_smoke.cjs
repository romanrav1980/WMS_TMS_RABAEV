const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const APP_URL = process.env.WMS_UI_URL || pageUrl("transport");
const task = { ID: 4601, TRANSTYPE: "10", TRANSPORT: "В 461 ТТ 59", VODITEL_ID: 461, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Day", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 1, PALLET_COUNT: 2, TEMP_WEIGHT: 400, PRICE: 1000, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByText("4601").waitFor({ timeout: 10000 });

  const tasksToolbar = page.locator(".dispatch-trips-section .dispatch-trips-toolbar").first();
  const tasksDate = tasksToolbar.locator("input[type='date']");
  const initialTasksDate = await tasksDate.inputValue();
  await tasksToolbar.getByTitle("Следующий день").click();
  if (await tasksDate.inputValue() <= initialTasksDate) throw new Error("Tasks next-day button did not increase date");
  await tasksToolbar.getByTitle("Предыдущий день").click();
  if (await tasksDate.inputValue() !== initialTasksDate) throw new Error("Tasks prev-day button did not restore date");

  await page.getByRole("button", { name: "Маршруты" }).click();
  const routesToolbar = page.locator(".dispatch-trips-toolbar").filter({ hasText: "Маршруты за" });
  const routesDate = routesToolbar.locator("input[type='date']");
  const initialRoutesDate = await routesDate.inputValue();
  await routesToolbar.getByTitle("Следующий день").click();
  if (await routesDate.inputValue() <= initialRoutesDate) throw new Error("Routes next-day button did not increase date");
  await routesToolbar.getByTitle("Предыдущий день").click();
  if (await routesDate.inputValue() !== initialRoutesDate) throw new Error("Routes prev-day button did not restore date");

  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => { console.error(error); process.exit(1); });
