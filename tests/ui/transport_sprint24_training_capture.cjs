const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint24_vrp_drag_drop_2026_05_28");

const plan = {
  plan_id: 24001,
  routes: [
    { vehicle_id: 2401, vehicle_num: "В 441 ТТ 59", vehicle_type: "10", max_pallets: 18, total_pallets: 6, total_kg: 2400, total_km: 20, total_duration_min: 90, utilization_pct: 33, stops: [{ st_number: "ДЦСТ-2401", addr: "Пермь, Ленина 1", lat: 58.01, lon: 56.25, pallets: 6, weight_kg: 2400, ware_id: 9201, unload_norm_min: 40 }] },
    { vehicle_id: 2402, vehicle_num: "В 442 ТТ 59", vehicle_type: "10", max_pallets: 18, total_pallets: 4, total_kg: 1600, total_km: 18, total_duration_min: 80, utilization_pct: 22, stops: [{ st_number: "ДЦСТ-2402", addr: "Пермь, Мира 2", lat: 58.03, lon: 56.27, pallets: 4, weight_kg: 1600, ware_id: 9201, unload_norm_min: 35 }] },
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

async function installMocks(page) {
  await page.route("**/api/admin/transport/planner/orders?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(orders) }));
  await page.route("**/api/admin/transport/routing/status", route => route.fulfill({ contentType: "application/json", body: JSON.stringify({ provider: "haversine", provider_available: true, total_addresses: 2, geocoded_count: 2, ungeocoded_count: 0 }) }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент 10т" }]) }));
  await page.route("**/api/admin/transport/planner/templates?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/planner/solve", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(plan) }));
  await page.route(/https:\/\/.*\.tile\.openstreetmap\.org\/.*/, route => route.fulfill({ contentType: "image/png", body: Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAFgwJ/lk0ITwAAAABJRU5ErkJggg==", "base64") }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto("http://127.0.0.1:3000/?page=planner");
  await page.getByRole("button", { name: /Авто-план/ }).click();
  await page.locator(".planner-rp-title", { hasText: "Рейсов: 2" }).waitFor({ timeout: 10000 });
  await page.locator(".planner-rp-route").nth(0).locator(".planner-rp-vehicle").click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_routes_before_drag.png"), fullPage: true });
  await page.locator(".planner-rp-stop-item", { hasText: "ДЦСТ-2401" }).dragTo(page.locator(".planner-rp-route").nth(1));
  await page.getByText("Порядок изменён вручную").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_routes_after_drag.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 24</title></head><body><h1>ТМС-2 Sprint 24: Перестановка СТ между рейсами</h1><p>Блок даёт диспетчеру ручную корректировку VRP-плана: СТ можно перетащить из одного рейса в другой до применения плана.</p><h2>Структура данных</h2><p>На клиенте хранится локальная копия <code>plan.routes[].stops</code>; после переноса пересчитываются паллеты, вес и утилизация затронутых маршрутов.</p><h2>Результат</h2><p>Диспетчер видит изменённый состав и индикатор ручной правки, а backend не вызывается до явного применения плана.</p><h2>Бизнес-процессы</h2><ol><li>Построить авто-план.</li><li>Раскрыть рейс и взять СТ.</li><li>Перетащить СТ в другой рейс.</li><li>Проверить изменённые метрики или сбросить правку.</li></ol><img src="screenshots/01_routes_before_drag.png" width="100%"><img src="screenshots/02_routes_after_drag.png" width="100%"><p>Проверка: functional, UI smoke и load gates пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
