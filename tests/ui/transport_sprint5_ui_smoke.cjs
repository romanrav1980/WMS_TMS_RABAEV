const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";

const available = [
  {
    ST_NUMBER: "ДЦСТ-П00501", ADDR: "Адрес 1", REGION: "Пермь", RAION: "Центр", ORD: 1,
    TRANSPORT_TYPE: "15", NEEDS_HYDRO_BOARD: 1, STOL: 1, PRIM1: "Гидроборт",
    WARE_ID: 9201, NAPR: "Центр", PALLETS_COUNT: 4, WEIGHT_KG: 1200, VOLUME_M3: 3.2,
    STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00",
    TRANSTASK_ID: null, VERIFY_PERC: 25, SUGAR: 1
  },
  {
    ST_NUMBER: "ДЦСТ-П00502", ADDR: "Адрес 2", REGION: "Пермь", RAION: "Центр", ORD: 2,
    TRANSPORT_TYPE: "10", NEEDS_HYDRO_BOARD: 0, STOL: 0, PRIM1: null,
    WARE_ID: 9201, NAPR: "Центр", PALLETS_COUNT: 2, WEIGHT_KG: 500, VOLUME_M3: 1.4,
    STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00",
    TRANSTASK_ID: null, VERIFY_PERC: 100, SUGAR: 0
  }
];

const task = {
  ID: 605,
  CREATEDATE: "2026-05-25T09:00:00",
  TRANSPORT: "A001AA",
  TRANSTYPE: "15",
  CONDITION: "Новый",
  SHIPMENT_DATE: "2026-05-25T00:00:00",
  VODITEL_ID: 1,
  VODITEL_NAME: "Иванов Иван",
  VODITEL_TEL: "79990000000",
  TK_NAME: "ТК Тест",
  IS_OWN_DRIVER: 0,
  PRIMECHANIE: "Sprint 5",
  DOCK: "Д1",
  SHIPMENT_TIME: "2026-05-25T09:00:00",
  TEMP_REGION: "Пермь",
  REGIONS: "Пермь",
  TEMP_WEIGHT: 1700,
  PRICE: 1000,
  DELETED: 0,
  LOGIST: "admin",
  PAY_ORDER_ID: null,
  PALLET_COUNT: 6,
  ST_COUNT: 2,
  VOLUME_M3: 4.6,
  READY_PERC: 75,
  UNREADY_COUNT: 1
};

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент 10т" }, { TRANSPORTTYPE: "15", NAME: "Тент 15т" }]) }));
  await page.route("**/api/admin/transport/available-sts?**", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify(available) }));
  await page.route("**/api/admin/transport/tasks?**", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/605/sts", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);

  await page.goto(APP_URL);
  await page.getByText("ДЦСТ-П00501").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-verify-bar-label", { hasText: "25%" }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-verify-low").first().waitFor({ timeout: 5000 });
  await page.locator(".dispatch-verify-bar-label", { hasText: "100%" }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-tr-badge", { hasText: "Тент 15т" }).waitFor({ timeout: 5000 });
  await page.getByText("♿").waitFor({ timeout: 5000 });
  await page.locator(".dispatch-polnopallet", { hasText: "П" }).waitFor({ timeout: 5000 });

  await page.getByText("#605").waitFor({ timeout: 5000 });
  await page.locator(".dispatch-readiness-label", { hasText: "75%" }).first().waitFor({ timeout: 5000 });
  await page.locator(".dispatch-hired-badge", { hasText: "ТК Тест" }).first().waitFor({ timeout: 5000 });

  await browser.close();
  console.log(JSON.stringify({ ok: true, availableRows: available.length, taskRows: 1 }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
