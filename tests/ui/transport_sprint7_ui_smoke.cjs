const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=planner";

const plannerOrders = [
  {
    ST_NUMBER: "ДЦСТ-П70001",
    ADDR: "г. Пермь, ул. Ленина 10",
    REGION: "г. Пермь",
    RAION: "Дзержинский",
    LAT: 58.0105,
    LON: 56.2502,
    PALLETS_COUNT: 8,
    WEIGHT_KG: 3200,
    VOLUME_M3: 11.2,
    WARE_ID: 9201,
    TRANSPORT_TYPE: "10",
    NEEDS_HYDRO_BOARD: 1,
    MAX_VEHICLE_TONS: 10,
    TW_STRICT: 1,
    UNLOAD_NORM_MIN: 45,
    VERIFY_PERC: 100,
    STDATE: "2026-05-25T00:00:00",
  },
  {
    ST_NUMBER: "ДЦСТ-П70002",
    ADDR: "г. Пермь, ул. Попова 3",
    REGION: "г. Пермь",
    RAION: "Ленинский",
    LAT: 58.0042,
    LON: 56.2310,
    PALLETS_COUNT: 3,
    WEIGHT_KG: 900,
    VOLUME_M3: 4.4,
    WARE_ID: 9201,
    TRANSPORT_TYPE: "15",
    NEEDS_HYDRO_BOARD: 0,
    MAX_VEHICLE_TONS: 15,
    TW_STRICT: 0,
    UNLOAD_NORM_MIN: 30,
    VERIFY_PERC: 50,
    STDATE: "2026-05-25T00:00:00",
  },
];

async function installMocks(page, calls) {
  await page.route("**/api/admin/transport/planner/orders?**", (route) => {
    calls.orders.push(route.request().url());
    const url = new URL(route.request().url());
    const trType = url.searchParams.get("transport_type");
    const body = trType ? plannerOrders.filter((order) => order.TRANSPORT_TYPE === trType) : plannerOrders;
    route.fulfill({ contentType: "application/json", body: JSON.stringify(body) });
  });
  await page.route("**/api/admin/transport/routing/status", (route) => {
    calls.status += 1;
    route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        provider: "haversine",
        provider_available: true,
        total_addresses: 2,
        geocoded_count: 2,
        ungeocoded_count: 0,
      }),
    });
  });
  await page.route("**/api/admin/transport/types", (route) => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify([
      { TRANSPORTTYPE: "10", NAME: "Тент 10т" },
      { TRANSPORTTYPE: "15", NAME: "Тент 15т" },
    ]),
  }));
  await page.route("**/api/admin/transport/planner/templates?**", (route) => route.fulfill({
    contentType: "application/json",
    body: "[]",
  }));
  await page.route(/https:\/\/.*\.tile\.openstreetmap\.org\/.*/, (route) => route.fulfill({
    contentType: "image/png",
    body: Buffer.from(
      "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAFgwJ/lk0ITwAAAABJRU5ErkJggg==",
      "base64",
    ),
  }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const calls = { orders: [], status: 0 };
  await installMocks(page, calls);

  await page.goto(APP_URL);
  await page.getByRole("heading", { name: "Планировщик маршрутов" }).waitFor({ timeout: 10000 });
  await page.getByText("Геокодинг:").waitFor({ timeout: 10000 });
  await page.locator(".planner-stat-row", { hasText: "Всего СТ" }).locator("b", { hasText: "2" }).waitFor({ timeout: 5000 });
  await page.locator(".planner-stat-row", { hasText: "На карте" }).locator("b", { hasText: "2" }).waitFor({ timeout: 5000 });
  await page.locator(".leaflet-interactive").first().waitFor({ timeout: 10000 });

  await page.locator(".leaflet-interactive").first().click({ force: true });
  await page.getByText("СТ ДЦСТ-П70001").waitFor({ timeout: 5000 });
  await page.getByText("Нужен гидроборт").waitFor({ timeout: 5000 });

  await page.locator(".dispatch-fp-select").first().selectOption("15");
  await page.waitForTimeout(500);
  await page.locator(".planner-stat-row", { hasText: "Всего СТ" }).locator("b", { hasText: "1" }).waitFor({ timeout: 5000 });
  const lastUrl = calls.orders.at(-1) || "";
  if (!lastUrl.includes("transport_type=15")) {
    throw new Error(`transport_type filter was not sent: ${lastUrl}`);
  }

  await page.getByRole("button", { name: "⟳ Обновить" }).click();
  if (calls.orders.length < 3) {
    throw new Error(`Reload did not call planner/orders enough times: ${calls.orders.length}`);
  }
  if (calls.status < 1) {
    throw new Error("routing/status was not called");
  }

  await browser.close();
  console.log(JSON.stringify({ ok: true, ordersCalls: calls.orders.length, statusCalls: calls.status }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
