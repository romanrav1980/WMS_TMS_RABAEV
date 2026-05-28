const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";

const task = {
  ID: 604,
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
  PRIMECHANIE: "Sprint 4",
  DOCK: "Д1",
  SHIPMENT_TIME: "2026-05-25T09:00:00",
  TEMP_REGION: "Пермь",
  REGIONS: "Пермь",
  TEMP_WEIGHT: 1500,
  PRICE: 1000,
  DELETED: 0,
  LOGIST: "admin",
  PAY_ORDER_ID: null,
  PALLET_COUNT: 6,
  ST_COUNT: 2,
  VOLUME_M3: 4.6,
  READY_PERC: 50,
  UNREADY_COUNT: 1
};

const composition = [
  { ST_NUMBER: "ДЦСТ-П00001", ADDR: "Адрес 1", REGION: "Пермь", RAION: "Центр", ORD: 1, PALLETS_COUNT: 4, WEIGHT_KG: 1000, STDATE: "2026-05-25T00:00:00", ZONE: "A", TIME_FROM: "09:00", TIME_TO: "10:00", LOAD_TYPE: "Г", WARE_ID: 9201, VERIFY_PERC: 100 },
  { ST_NUMBER: "ДЦСТ-П00002", ADDR: "Адрес 2", REGION: "Пермь", RAION: "Центр", ORD: 2, PALLETS_COUNT: 2, WEIGHT_KG: 500, STDATE: "2026-05-25T00:00:00", ZONE: "B", TIME_FROM: "10:00", TIME_TO: "11:00", LOAD_TYPE: "П", WARE_ID: 9201, VERIFY_PERC: 0 }
];

async function installMocks(page, calls) {
  await page.route("**/api/admin/transport/vehicles", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ ID: 1, NUM: "A001AA", MARKA: "Газель", TR_TYPE: "10", PALLETS: 8, GIDROBORT: 1 }]) }));
  await page.route("**/api/admin/transport/drivers", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ ID: 1, FULL_NAME: "Иванов Иван", SOBSTVENNYY: 0, DOVERENNOST_OT: "ТК Тест" }]) }));
  await page.route("**/api/admin/transport/types", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент 10т" }, { TRANSPORTTYPE: "15", NAME: "Фургон 15т" }]) }));
  await page.route("**/api/admin/transport/available-sts?**", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/604/sts", (route) => {
    if (route.request().method() === "DELETE") calls.unassign += 1;
    return route.fulfill({ contentType: "application/json", body: JSON.stringify(composition) });
  });
  await page.route("**/api/admin/transport/tasks/604/sts/**", (route) => {
    calls.unassign += 1;
    return route.fulfill({ contentType: "application/json", body: JSON.stringify({ unassigned: true }) });
  });
  await page.route("**/api/admin/transport/tasks/604/close", (route) => {
    calls.close += 1;
    return route.fulfill({ contentType: "application/json", body: JSON.stringify({ task_id: 604, closed: true }) });
  });
  await page.route("**/api/admin/transport/tasks/604", async (route) => {
    if (route.request().method() === "PATCH") {
      calls.patch.push(JSON.parse(route.request().postData() || "{}"));
      return route.fulfill({ contentType: "application/json", body: JSON.stringify({ task_id: 604 }) });
    }
    return route.fulfill({ contentType: "application/json", body: JSON.stringify({ ...task, DOCK: "Д9" }) });
  });
  await page.route("**/api/admin/transport/billing/orders/**", (route) => route.fulfill({ contentType: "application/json", body: "{}" }));
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const calls = { patch: [], unassign: 0, close: 0 };
  await installMocks(page, calls);
  page.on("dialog", (dialog) => dialog.accept());

  await page.goto(APP_URL);
  await page.getByText("#604").waitFor({ timeout: 10000 });
  await page.getByText("#604").click();
  await page.getByText("Рейс #604").waitFor({ timeout: 5000 });
  await page.getByText("ДЦСТ-П00001").waitFor({ timeout: 5000 });

  await page.getByRole("button", { name: "Редактировать" }).click();
  await page.locator(".dispatch-trip-mi").first().fill("Д9");
  await page.getByRole("button", { name: "Сохранить" }).click();
  await page.waitForFunction(() => window.__never, null, { timeout: 150 }).catch(() => {});
  assert(calls.patch.some((body) => body.dock === "Д9"), "Dock edit was not sent via PATCH");

  await page.locator(".dispatch-unassign-btn").first().click();
  await page.waitForFunction(() => window.__never, null, { timeout: 150 }).catch(() => {});
  assert(calls.unassign >= 1, "Unassign button did not call DELETE");

  await page.getByRole("button", { name: "Закрыть рейс" }).click();
  await page.waitForFunction(() => window.__never, null, { timeout: 150 }).catch(() => {});
  assert(calls.close === 1, "Close button did not call close endpoint");

  await browser.close();
  console.log(JSON.stringify({ ok: true, patchCalls: calls.patch.length, unassignCalls: calls.unassign, closeCalls: calls.close }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
