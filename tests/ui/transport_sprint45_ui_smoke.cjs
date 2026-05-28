const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const APP_URL = process.env.WMS_UI_URL || pageUrl("transport");
const task = { ID: 4501, TRANSTYPE: "10", TRANSPORT: "В 451 ТТ 59", VODITEL_ID: 451, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Goto", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 1, PALLET_COUNT: 2, TEMP_WEIGHT: 400, PRICE: 1000, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
const sts = [
  { ST_NUMBER: "СТ-4501", ADDR: "Пермь, Ленина 1", REGION: "Пермь", RAION: "Ленинский", PALLETS_COUNT: 2, WEIGHT_KG: 400, VOLUME_M3: 1.2, STDATE: "2026-05-25", DATE_LOAD: "2026-05-25", TRANSPORT_TYPE: "10", WARE_ID: 9201, VERIFY_PERC: 100, SUGAR: 0, TRANSTASK_ID: 4501 },
  { ST_NUMBER: "СТ-4502", ADDR: "Пермь, Мира 2", REGION: "Пермь", RAION: "Ленинский", PALLETS_COUNT: 1, WEIGHT_KG: 200, VOLUME_M3: 0.6, STDATE: "2026-05-25", DATE_LOAD: "2026-05-25", TRANSPORT_TYPE: "10", WARE_ID: 9201, VERIFY_PERC: 100, SUGAR: 0, TRANSTASK_ID: 0 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(sts) }));
  await page.route("**/api/admin/transport/tasks/4501", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(task) }));
  await page.route("**/api/admin/transport/tasks/4501/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByText("СТ-4501").waitFor({ timeout: 10000 });
  await page.getByRole("button", { name: "#4501 →" }).click();
  await page.locator(".dispatch-tab.active", { hasText: "Маршруты" }).waitFor({ timeout: 5000 });
  await page.locator("tr[data-taskid='4501'].selected").waitFor({ timeout: 5000 });
  if (await page.getByRole("button", { name: "#0 →" }).count()) throw new Error("Goto button rendered for TRANSTASK_ID=0");
  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => { console.error(error); process.exit(1); });
