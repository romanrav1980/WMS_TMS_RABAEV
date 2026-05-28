const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const sourceTask = { ID: 3801, TRANSTYPE: "10", TRANSPORT: "В 501 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Copy-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", SHIPMENT_TIME: "2026-05-25T08:30:00", DOCK: "Д-1", CONDITION: "Новый", ST_COUNT: 2, PALLET_COUNT: 8, TEMP_WEIGHT: 1500, PRICE: 9900, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
const copiedTask = { ...sourceTask, ID: 3802, ST_COUNT: 0, PALLET_COUNT: 0, TEMP_WEIGHT: 0, PRICE: null };
let copied = false;
let patchPayload = null;

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks/3802", async route => {
    if (route.request().method() === "PATCH") {
      patchPayload = JSON.parse(route.request().postData() || "{}");
      return route.fulfill({ contentType: "application/json", body: JSON.stringify({ task_id: 3802 }) });
    }
    return route.fulfill({ contentType: "application/json", body: JSON.stringify(copiedTask) });
  });
  await page.route("**/api/admin/transport/tasks/3801/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks/3802/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks", async route => {
    if (route.request().method() === "POST") {
      copied = true;
      return route.fulfill({ contentType: "application/json", body: JSON.stringify({ task_id: 3802 }) });
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
  await page.getByText("#3801").waitFor({ timeout: 10000 });
  await page.locator("tr[data-taskid='3801']").click();
  await page.getByRole("button", { name: "📋 Копировать" }).click();
  await page.getByText("Рейс #3802 создан как копия рейса #3801").waitFor({ timeout: 5000 });
  await page.locator(".dispatch-trip-title-row b", { hasText: "Рейс #3802" }).waitFor({ timeout: 5000 });
  if (!patchPayload || patchPayload.transport !== "В 501 ТТ 59" || patchPayload.voditel_id !== 501 || patchPayload.dock !== "Д-1") {
    throw new Error(`Copy patch did not inherit expected fields: ${JSON.stringify(patchPayload)}`);
  }
  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => { console.error(error); process.exit(1); });
