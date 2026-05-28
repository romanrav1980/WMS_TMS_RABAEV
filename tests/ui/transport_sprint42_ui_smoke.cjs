const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const APP_URL = process.env.WMS_UI_URL || pageUrl("transport");
const sourceTask = { ID: 4201, TRANSTYPE: "10", TRANSPORT: "В 421 ТТ 59", VODITEL_ID: 421, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Toast", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", SHIPMENT_TIME: "2026-05-25T08:30:00", DOCK: "Д-1", CONDITION: "Новый", ST_COUNT: 2, PALLET_COUNT: 8, TEMP_WEIGHT: 1500, PRICE: 9900, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
const copiedTask = { ...sourceTask, ID: 4202, ST_COUNT: 0, PALLET_COUNT: 0, TEMP_WEIGHT: 0, PRICE: null };
let copied = false;

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks/4202", async route => {
    if (route.request().method() === "PATCH") return route.fulfill({ contentType: "application/json", body: JSON.stringify({ task_id: 4202 }) });
    return route.fulfill({ contentType: "application/json", body: JSON.stringify(copiedTask) });
  });
  await page.route("**/api/admin/transport/tasks/4201/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks/4202/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks", async route => {
    if (route.request().method() === "POST") {
      copied = true;
      return route.fulfill({ contentType: "application/json", body: JSON.stringify({ task_id: 4202 }) });
    }
    return route.fallback();
  });
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(copied ? [copiedTask, sourceTask] : [sourceTask]) }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByText("#4201").waitFor({ timeout: 10000 });
  await page.locator("tr[data-taskid='4201']").click();
  await page.getByRole("button", { name: "📋 Копировать" }).click();
  const toast = page.locator(".dispatch-toast");
  await toast.filter({ hasText: "Рейс #4202 создан как копия рейса #4201" }).waitFor({ timeout: 5000 });
  await toast.click();
  if (await page.locator(".dispatch-toast").count()) throw new Error("Toast did not dismiss on click");
  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => { console.error(error); process.exit(1); });
