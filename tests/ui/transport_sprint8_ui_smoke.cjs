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
  explain: {
    input: {
      plan_date: "2026-05-25",
      orders_total: 1,
      orders_with_coords: 1,
      orders_skipped_no_coords: 0,
      ware_ids: [9201],
      transport_type: null,
    },
    routing: {
      requested_source: "auto",
      active_provider: "haversine",
      used_provider: "haversine",
      fallback_used: false,
      matrix_pairs: 0,
      matrix_age_min: null,
    },
    solver: {
      requested_solver: "auto",
      used_solver: "clarke-wright",
      time_limit_s: 60,
      solve_time_ms: 37,
    },
    constraints: {
      capacity_pallets: true,
      capacity_weight: true,
      time_windows: true,
      vehicle_type: true,
      hydro_board: true,
      fallback_time_windows: 1,
    },
    fleet: {
      vehicles_total: 1,
      vehicles_used: 1,
      target_routes_per_vehicle: 4,
      target_daily_routes: 4,
      planned_routes: 1,
      avg_utilization_pct: 44.4,
      min_utilization_pct: 44.4,
      max_utilization_pct: 44.4,
      low_utilization_routes: 1,
      over_capacity_routes: 0,
    },
    steps: [
      { code: "orders_loaded", status: "done", label: "Заявки загружены", message: "Найдено 1 СТ, 1 с координатами", elapsed_ms: 10 },
      { code: "vehicles_loaded", status: "done", label: "Машины загружены", message: "Доступно 1 активных ТС", elapsed_ms: 15 },
      { code: "distance_matrix_loaded", status: "warning", label: "Матрица расстояний", message: "Загружено 0 пар, расчетный provider: haversine", elapsed_ms: 18 },
      { code: "optimization_done", status: "done", label: "Оптимизация завершена", message: "Построено 1 рейсов, без рейса 0 СТ", elapsed_ms: 37 },
      { code: "plan_saved", status: "done", label: "План сохранен", message: "plan_id=88001", elapsed_ms: 39 },
    ],
    warnings: [
      { code: "low_utilization_routes", severity: "info", message: "1 рейсов имеют загрузку ниже 60%", action: "Проверить возможность объединения" },
    ],
  },
};

const jsonHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "*",
  "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
};

async function installMocks(page, calls) {
  await page.route("**/api/admin/transport/planner/orders?**", (route) => {
    route.fulfill({
      contentType: "application/json",
      headers: jsonHeaders,
      body: JSON.stringify([order]),
    });
  });
  await page.route("**/api/admin/transport/routing/status", (route) => route.fulfill({
    contentType: "application/json",
    headers: jsonHeaders,
    body: JSON.stringify({ provider: "haversine", provider_available: true, total_addresses: 1, geocoded_count: 1, ungeocoded_count: 0 }),
  }));
  await page.route("**/api/admin/transport/types", (route) => route.fulfill({
    contentType: "application/json",
    headers: jsonHeaders,
    body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент 10т" }]),
  }));
  await page.route("**/api/admin/transport/planner/templates?**", (route) => route.fulfill({
    contentType: "application/json",
    headers: jsonHeaders,
    body: "[]",
  }));
  await page.route("**/api/admin/transport/distance-matrix/rebuild?**", async (route) => {
    if (route.request().method() === "OPTIONS") {
      route.fulfill({ status: 204, headers: jsonHeaders });
      return;
    }
    calls.matrix.push(route.request().url());
    route.fulfill({
      contentType: "application/json",
      headers: jsonHeaders,
      body: JSON.stringify({
        pairs: 0,
        computed_pairs: 0,
        skipped_pairs: 0,
        source: "haversine",
        addresses: 1,
        cached: true,
      }),
    });
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
  const calls = { matrix: [] };
  await installMocks(page, calls);
  page.on("dialog", (dialog) => {
    throw new Error(`Unexpected browser dialog: ${dialog.message()}`);
  });

  await page.goto(APP_URL);
  await page.getByRole("heading", { name: "Планировщик маршрутов" }).waitFor({ timeout: 10000 });
  await page.locator('input[type="date"]').fill("2026-05-24");
  await page.locator(".planner-solve-btn:not([disabled])").waitFor({ timeout: 10000 });
  await page.locator(".planner-solve-btn").click({ force: true });

  await page.locator(".planner-rp-title", { hasText: "Рейсов:" }).waitFor({ timeout: 30000 });
  await page.locator(".planner-solver-badge").waitFor({ timeout: 5000 });
  await page.getByRole("heading", { name: "Детали расчета" }).waitFor({ timeout: 5000 });
  await page.locator(".planner-explain-section", { hasText: "Ход расчета" }).waitFor({ timeout: 5000 });
  await page.locator(".planner-explain-section", { hasText: "Загрузка автомобилей" }).waitFor({ timeout: 5000 });
  await page.locator(".planner-step", { hasText: "Заявки загружены" }).waitFor({ timeout: 5000 });
  await page.getByRole("button", { name: "Открыть план на карте" }).click();
  await page.getByRole("button", { name: /Матрица/ }).click();
  await page.locator(".planner-explain-alert", { hasText: "Матрица расстояний:" }).waitFor({ timeout: 30000 });

  await browser.close();
  console.log(JSON.stringify({ ok: true, matrixCalls: calls.matrix.length }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
