const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const vehicle = { ID: 1, NUM: "В 501 ТТ 59", MARKA: "MAN", PALLETS: 10 };
const task = { ID: 3001, TRANSTYPE: "10", TRANSPORT: vehicle.NUM, VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Load-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 2, PALLET_COUNT: 9, TEMP_WEIGHT: 1800, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
const taskSts = [
  { ST_NUMBER: "СТ-3001", ADDR: "Пермь", REGION: "Пермь", RAION: "Север", PALLETS_COUNT: 5, WEIGHT_KG: 1000, VOLUME_M3: 4, STDATE: "2026-05-25", DATE_LOAD: "2026-05-25", TRANSPORT_TYPE: "10", LOAD_TYPE: null, ORD: 1, WARE_ID: 9201, VERIFY_PERC: 100 },
  { ST_NUMBER: "СТ-3002", ADDR: "Пермь", REGION: "Пермь", RAION: "Север", PALLETS_COUNT: 4, WEIGHT_KG: 800, VOLUME_M3: 3, STDATE: "2026-05-25", DATE_LOAD: "2026-05-25", TRANSPORT_TYPE: "10", LOAD_TYPE: null, ORD: 2, WARE_ID: 9201, VERIFY_PERC: 100 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([vehicle]) }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/3001/sts", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(taskSts) }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("3001").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await page.locator(".load-bar-row").waitFor({ timeout: 5000 });
  await page.getByText("9 / 10 пал (90%)").waitFor({ timeout: 5000 });
  const fillWidth = await page.locator(".load-bar-fill").evaluate(el => getComputedStyle(el).width);
  if (!fillWidth || fillWidth === "0px") throw new Error("Load bar fill is not visible");
  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => { console.error(error); process.exit(1); });
