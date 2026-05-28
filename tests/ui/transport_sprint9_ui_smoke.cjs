const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=planner";

const orders = [0, 1, 2].map((idx) => ({
  ST_NUMBER: `ДЦСТ-П9000${idx + 1}`,
  ADDR: `г. Пермь, тест ${idx + 1}`,
  REGION: "г. Пермь",
  RAION: "Дзержинский",
  LAT: 58.0105 + idx * 0.002,
  LON: 56.2502 + idx * 0.002,
  PALLETS_COUNT: 3 + idx,
  WEIGHT_KG: 900 + idx * 100,
  VOLUME_M3: 4.1,
  WARE_ID: 9201,
  TRANSPORT_TYPE: "10",
  NEEDS_HYDRO_BOARD: 0,
  MAX_VEHICLE_TONS: 10,
  TW_STRICT: 0,
  UNLOAD_NORM_MIN: 30,
  VERIFY_PERC: 100,
  STDATE: "2026-05-25T00:00:00",
}));

const plan = {
  plan_id: 99001,
  routes: [{
    vehicle_id: 9201,
    vehicle_num: "В 415 ТТ 59",
    vehicle_type: "10",
    max_pallets: 18,
    total_pallets: 12,
    total_kg: 3000,
    total_km: 25,
    total_duration_min: 90,
    utilization_pct: 66.7,
    stops: orders.map((order) => ({
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
    })),
  }],
  unassigned_sts: [],
  total_km: 25,
  fleet_utilization_pct: 66.7,
  tw_violations: 0,
  score: 66.4,
  solver_used: "dbscan-cluster",
  solve_time_ms: 51,
};

async function installMocks(page, calls) {
  await page.route("**/api/admin/transport/planner/orders?**", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify(orders) }));
  await page.route("**/api/admin/transport/routing/status", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify({ provider: "haversine", provider_available: true, total_addresses: 3, geocoded_count: 3, ungeocoded_count: 0 }) }));
  await page.route("**/api/admin/transport/types", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент 10т" }]) }));
  await page.route("**/api/admin/transport/planner/solve", async (route) => {
    calls.solve.push(route.request().postDataJSON());
    route.fulfill({ contentType: "application/json", body: JSON.stringify(plan) });
  });
  await page.route("**/api/admin/transport/planner/templates?**", (route) => {
    calls.templates += 1;
    route.fulfill({
      contentType: "application/json",
      body: JSON.stringify([{
        plan_id: 99000,
        plan_date: "2026-05-18",
        score: 61.2,
        jaccard: 0.92,
        routes_count: 1,
        matched_sts: 3,
        total_current_sts: 3,
      }]),
    });
  });
  await page.route("**/api/admin/transport/planner/apply", async (route) => {
    calls.apply.push(route.request().postDataJSON());
    route.fulfill({ contentType: "application/json", body: JSON.stringify({ tasks_created: 1 }) });
  });
  await page.route(/https:\/\/.*\.tile\.openstreetmap\.org\/.*/, (route) => route.fulfill({
    contentType: "image/png",
    body: Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAFgwJ/lk0ITwAAAABJRU5ErkJggg==", "base64"),
  }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const calls = { solve: [], templates: 0, apply: [] };
  await installMocks(page, calls);
  page.on("dialog", (dialog) => dialog.accept());

  await page.goto(APP_URL);
  await page.getByRole("heading", { name: "Планировщик маршрутов" }).waitFor({ timeout: 10000 });
  await page.getByLabel(/Слой кластеров/).check();
  await page.waitForFunction(() => document.querySelectorAll(".leaflet-interactive").length >= 4, null, { timeout: 5000 });

  await page.locator(".dispatch-fp-select").nth(1).selectOption("cluster");
  await page.getByRole("button", { name: /Авто-план/ }).click();
  await page.locator(".planner-solver-badge", { hasText: "dbscan-cluster" }).waitFor({ timeout: 5000 });
  if (calls.solve[0].solver !== "cluster") {
    throw new Error(`Cluster solver was not requested: ${JSON.stringify(calls.solve[0])}`);
  }

  await page.locator(".planner-tmpl-load-btn").click();
  await page.getByText("Jaccard 92%").waitFor({ timeout: 5000 });
  await page.getByRole("button", { name: "Применить шаблон" }).click();
  await page.getByText("Создано рейсов: 1").waitFor({ timeout: 5000 });
  if (calls.templates !== 1 || calls.apply[0].plan_id !== 99000) {
    throw new Error(`Template flow mismatch: ${JSON.stringify(calls)}`);
  }

  await browser.close();
  console.log(JSON.stringify({ ok: true, solveCalls: calls.solve.length, templatesCalls: calls.templates }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
