const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";

const task = {
  ID: 606,
  CREATEDATE: "2026-05-25T09:00:00",
  TRANSPORT: "A001AA",
  TRANSTYPE: "10",
  CONDITION: "Новый",
  SHIPMENT_DATE: "2026-05-25T00:00:00",
  VODITEL_ID: 1,
  VODITEL_NAME: "Иванов Иван",
  VODITEL_TEL: "79990000000",
  TK_NAME: "ТК Тест",
  IS_OWN_DRIVER: 0,
  PRIMECHANIE: "Sprint 6",
  DOCK: "Д1",
  SHIPMENT_TIME: "2026-05-25T09:00:00",
  TEMP_REGION: "Пермь",
  REGIONS: "Пермь",
  TEMP_WEIGHT: 1500,
  PRICE: 1000,
  DELETED: 0,
  LOGIST: "admin",
  PAY_ORDER_ID: null,
  PALLET_COUNT: 2,
  ST_COUNT: 1,
  VOLUME_M3: 1.2,
  READY_PERC: 0,
  UNREADY_COUNT: 2
};

const composition = [
  { ST_NUMBER: "ДЦСТ-П00601", ADDR: "Адрес 1", REGION: "Пермь", RAION: "Центр", ORD: 1, PALLETS_COUNT: 2, WEIGHT_KG: 500, STDATE: "2026-05-25T00:00:00", ZONE: "A", TIME_FROM: "09:00", TIME_TO: "10:00", LOAD_TYPE: "Г", WARE_ID: 9201, VERIFY_PERC: 0 }
];

const pallets = [
  { PALLET_UID: "PAL-606-1", ZONE: "A", LOAD_TYPE: "Г", ORD: 1, ARTICUL: "ART-1", ORDER_WEIGHT: 120, PACK_COUNT: 6, ROW_VOLUME_M3: 0.123 },
  { PALLET_UID: "PAL-606-2", ZONE: "A", LOAD_TYPE: "Г", ORD: 1, ARTICUL: "ART-2", ORDER_WEIGHT: 180, PACK_COUNT: 8, ROW_VOLUME_M3: 0.222 }
];

async function installMocks(page, calls) {
  await page.route("**/api/admin/transport/vehicles", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент 10т" }]) }));
  await page.route("**/api/admin/transport/available-sts?**", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/606/sts", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify(composition) }));
  await page.route("**/api/admin/transport/tasks/606/sts/**/load-type", (route) => {
    calls.loadType.push(JSON.parse(route.request().postData() || "{}"));
    return route.fulfill({ contentType: "application/json", body: JSON.stringify({ ok: true }) });
  });
  await page.route("**/api/admin/transport/tasks/606/sts/**/order", (route) => {
    calls.order.push(JSON.parse(route.request().postData() || "{}"));
    return route.fulfill({ contentType: "application/json", body: JSON.stringify({ ok: true }) });
  });
  await page.route("**/api/admin/transport/sts/**/pallets", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify(pallets) }));
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const calls = { loadType: [], order: [] };
  await installMocks(page, calls);

  await page.goto(APP_URL);
  await page.getByText("#606").waitFor({ timeout: 10000 });
  await page.getByText("#606").click();
  await page.getByText("ДЦСТ-П00601").waitFor({ timeout: 5000 });

  await page.locator(".dispatch-loadtype-select").first().selectOption("П");
  await page.waitForTimeout(150);
  assert(calls.loadType.some((body) => body.load_type === "П"), "Load type PATCH was not sent");

  await page.locator(".dispatch-ord-val").first().click();
  await page.locator(".dispatch-ord-input").fill("7");
  await page.locator(".dispatch-ord-input").press("Enter");
  await page.waitForTimeout(150);
  assert(calls.order.some((body) => body.ord === 7), "Order PATCH was not sent");

  await page.locator(".dispatch-pallet-btn").first().click();
  await page.getByText("Паллеты СТ ДЦСТ-П00601").waitFor({ timeout: 5000 });
  await page.getByText("PAL-606-1").waitFor({ timeout: 5000 });
  await page.getByText("ART-2").waitFor({ timeout: 5000 });

  await browser.close();
  console.log(JSON.stringify({ ok: true, loadTypeCalls: calls.loadType.length, orderCalls: calls.order.length, palletRows: pallets.length }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
