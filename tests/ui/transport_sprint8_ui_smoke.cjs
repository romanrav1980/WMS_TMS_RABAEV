const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=planner";

const order = {
  ST_NUMBER: "ДЦСТ-П80001",
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
  TW_STRICT: 0,
  UNLOAD_NORM_MIN: 45,
  VERIFY_PERC: 100,
  STDATE: "2026-05-25T00:00:00",
};

const plan = {
  plan_id: 88001,
  routes: [
    {
      vehicle_id: 9201,
      vehicle_num: "В 415 ТТ 59",
      vehicle_type: "10",
      max_pallets: 18,
      total_pallets: 8,
      total_kg: 3200,
      total_km: 42.5,
      total_duration_min: 128,
      utilization_pct: 44.4,
      stops: [
        {
          st_number: order.ST_NUMBER,
          addr: order.ADDR,
          lat: order.LAT,
          lon: order.LON,
          pallets: order.PALLETS_COUNT,
          weight_kg: order.WEIGHT_KG,
          ware_id: order.WARE_ID,
          unload_norm_min: order.UNLOAD_NORM_MIN,
          tw_from: 0,
          tw_to: 1080,
          tw_strict: false,
        },
      ],
    },
  ],
  unassigned_sts: [],
  total_km: 42.5,
  fleet_utilization_pct: 44.4,
  tw_violations: 0,
  score: 43.9,
  solver_used: "clarke-wright",
  solve_time_ms: 37,
};

async function installMocks(page, calls) {
  await page.route("**/api/admin/transport/planner/orders?**", (route) => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify([order]),
  }));
  await page.route("**/api/admin/transport/routing/status", (route) => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify({ provider: "haversine", provider_available: true, total_addresses: 1, geocoded_count: 1, ungeocoded_count: 0 }),
  }));
  await page.route("**/api/admin/transport/types", (route) => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент 10т" }]),
  }));
  await page.route("**/api/admin/transport/planner/templates?**", (route) => route.fulfill({
    contentType: "application/json",
    body: "[]",
  }));
  await page.route("**/api/admin/transport/planner/solve", async (route) => {
    calls.solve.push(route.request().postDataJSON());
    route.fulfill({ contentType: "application/json", body: JSON.stringify(plan) });
  });
  await page.route("**/api/admin/transport/planner/apply", async (route) => {
    calls.apply.push(route.request().postDataJSON());
    route.fulfill({ contentType: "application/json", body: JSON.stringify({ tasks_created: 1 }) });
  });
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
  const calls = { solve: [], apply: [] };
  await installMocks(page, calls);
  page.on("dialog", (dialog) => dialog.accept());

  await page.goto(APP_URL);
  await page.getByRole("heading", { name: "Планировщик маршрутов" }).waitFor({ timeout: 10000 });
  await page.getByRole("button", { name: /Авто-план/ }).click();

  await page.locator(".planner-rp-title", { hasText: "Рейсов: 1" }).waitFor({ timeout: 5000 });
  await page.locator(".planner-rp-vehicle", { hasText: "В 415 ТТ 59" }).waitFor({ timeout: 5000 });
  await page.locator(".planner-solver-badge", { hasText: "clarke-wright" }).waitFor({ timeout: 5000 });
  await page.locator(".planner-rp-vehicle", { hasText: "В 415 ТТ 59" }).click();
  await page.getByText("ДЦСТ-П80001").waitFor({ timeout: 5000 });

  await page.getByRole("button", { name: /Применить план/ }).click();
  await page.getByText("Создано рейсов: 1").waitFor({ timeout: 5000 });

  if (calls.solve.length !== 1) {
    throw new Error(`Expected one solve call, got ${calls.solve.length}`);
  }
  if (calls.apply.length !== 1 || calls.apply[0].plan_id !== 88001) {
    throw new Error(`Apply payload mismatch: ${JSON.stringify(calls.apply)}`);
  }

  await browser.close();
  console.log(JSON.stringify({ ok: true, solveCalls: calls.solve.length, applyCalls: calls.apply.length }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
