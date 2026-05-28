const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=planner";

const plan = {
  plan_id: 24001,
  routes: [
    {
      vehicle_id: 2401,
      vehicle_num: "В 441 ТТ 59",
      vehicle_type: "10",
      max_pallets: 18,
      total_pallets: 6,
      total_kg: 2400,
      total_km: 20,
      total_duration_min: 90,
      utilization_pct: 33,
      stops: [{ st_number: "ДЦСТ-2401", addr: "Пермь, Ленина 1", lat: 58.01, lon: 56.25, pallets: 6, weight_kg: 2400, ware_id: 9201, unload_norm_min: 40 }],
    },
    {
      vehicle_id: 2402,
      vehicle_num: "В 442 ТТ 59",
      vehicle_type: "10",
      max_pallets: 18,
      total_pallets: 4,
      total_kg: 1600,
      total_km: 18,
      total_duration_min: 80,
      utilization_pct: 22,
      stops: [{ st_number: "ДЦСТ-2402", addr: "Пермь, Мира 2", lat: 58.03, lon: 56.27, pallets: 4, weight_kg: 1600, ware_id: 9201, unload_norm_min: 35 }],
    },
  ],
  unassigned_sts: [],
  total_km: 38,
  fleet_utilization_pct: 28,
  tw_violations: 0,
  score: 52,
  solver_used: "savings",
  solve_time_ms: 25,
};

const orders = [
  { ST_NUMBER: "ДЦСТ-2401", ADDR: "Пермь, Ленина 1", LAT: 58.01, LON: 56.25, PALLETS_COUNT: 6, WEIGHT_KG: 2400, VOLUME_M3: 8, WARE_ID: 9201, TRANSPORT_TYPE: "10", UNLOAD_NORM_MIN: 40 },
  { ST_NUMBER: "ДЦСТ-2402", ADDR: "Пермь, Мира 2", LAT: 58.03, LON: 56.27, PALLETS_COUNT: 4, WEIGHT_KG: 1600, VOLUME_M3: 5, WARE_ID: 9201, TRANSPORT_TYPE: "10", UNLOAD_NORM_MIN: 35 },
];

async function installMocks(page, calls) {
  await page.route("**/api/admin/transport/planner/orders?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(orders) }));
  await page.route("**/api/admin/transport/routing/status", route => route.fulfill({ contentType: "application/json", body: JSON.stringify({ provider: "haversine", provider_available: true, total_addresses: 2, geocoded_count: 2, ungeocoded_count: 0 }) }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент 10т" }]) }));
  await page.route("**/api/admin/transport/planner/templates?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/planner/solve", route => { calls.solve += 1; route.fulfill({ contentType: "application/json", body: JSON.stringify(plan) }); });
  await page.route("**/api/admin/transport/planner/apply", route => { calls.apply += 1; route.fulfill({ contentType: "application/json", body: JSON.stringify({ tasks_created: 2 }) }); });
  await page.route(/https:\/\/.*\.tile\.openstreetmap\.org\/.*/, route => route.fulfill({ contentType: "image/png", body: Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAFgwJ/lk0ITwAAAABJRU5ErkJggg==", "base64") }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const calls = { solve: 0, apply: 0 };
  await installMocks(page, calls);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: /Авто-план/ }).click();
  await page.locator(".planner-rp-title", { hasText: "Рейсов: 2" }).waitFor({ timeout: 10000 });
  await page.locator(".planner-rp-route").nth(0).locator(".planner-rp-vehicle").click();
  await page.getByText("ДЦСТ-2401").waitFor({ timeout: 5000 });
  const source = page.locator(".planner-rp-stop-item", { hasText: "ДЦСТ-2401" });
  const target = page.locator(".planner-rp-route").nth(1);
  await source.dragTo(target);
  await page.getByText("Порядок изменён вручную").waitFor({ timeout: 5000 });
  await page.locator(".planner-rp-route").nth(1).locator(".planner-rp-stops", { hasText: "2 адресов" }).waitFor({ timeout: 5000 });
  await page.locator(".planner-reset-btn").click();
  await page.getByText("Порядок изменён вручную").waitFor({ state: "hidden", timeout: 5000 });
  if (calls.solve !== 1 || calls.apply !== 0) throw new Error(`Unexpected calls: ${JSON.stringify(calls)}`);
  await browser.close();
  console.log(JSON.stringify({ ok: true, calls }));
}

main().catch(error => { console.error(error); process.exit(1); });
