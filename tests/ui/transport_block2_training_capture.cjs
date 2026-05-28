const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=planner";
const OUT_DIR = path.resolve("wiki-raw/tms2_training/block_ii_sprint7_10_2026_05_28");

const orders = [
  {
    ST_NUMBER: "ДЦСТ-П70001", ADDR: "г. Пермь, ул. Ленина 10", REGION: "г. Пермь", RAION: "Дзержинский",
    LAT: 58.0105, LON: 56.2502, PALLETS_COUNT: 8, WEIGHT_KG: 3200, VOLUME_M3: 11.2,
    WARE_ID: 9201, TRANSPORT_TYPE: "10", NEEDS_HYDRO_BOARD: 1, MAX_VEHICLE_TONS: 10,
    TW_STRICT: 1, UNLOAD_NORM_MIN: 45, VERIFY_PERC: 100, STDATE: "2026-05-25T00:00:00",
  },
  {
    ST_NUMBER: "ДЦСТ-П70002", ADDR: "г. Пермь, ул. Попова 3", REGION: "г. Пермь", RAION: "Дзержинский",
    LAT: 58.0042, LON: 56.231, PALLETS_COUNT: 3, WEIGHT_KG: 900, VOLUME_M3: 4.4,
    WARE_ID: 9201, TRANSPORT_TYPE: "15", NEEDS_HYDRO_BOARD: 0, MAX_VEHICLE_TONS: 15,
    TW_STRICT: 0, UNLOAD_NORM_MIN: 30, VERIFY_PERC: 50, STDATE: "2026-05-25T00:00:00",
  },
  {
    ST_NUMBER: "ДЦСТ-Е70003", ADDR: "г. Екатеринбург, ул. Мира 12", REGION: "г. Екатеринбург", RAION: "Верх-Исетский",
    LAT: 56.842, LON: 60.607, PALLETS_COUNT: 5, WEIGHT_KG: 1800, VOLUME_M3: 8.1,
    WARE_ID: 9202, TRANSPORT_TYPE: "10", NEEDS_HYDRO_BOARD: 0, MAX_VEHICLE_TONS: 20,
    TW_STRICT: 0, UNLOAD_NORM_MIN: 35, VERIFY_PERC: 100, STDATE: "2026-05-25T00:00:00",
  },
];

const plan = {
  plan_id: 88001,
  routes: [
    {
      vehicle_id: 9201, vehicle_num: "В 415 ТТ 59", vehicle_type: "10", max_pallets: 18,
      total_pallets: 11, total_kg: 4100, total_km: 42.5, total_duration_min: 128, utilization_pct: 61.1,
      stops: orders.slice(0, 2).map(toStop),
    },
    {
      vehicle_id: 9202, vehicle_num: "Е 714 НО 59", vehicle_type: "10", max_pallets: 16,
      total_pallets: 5, total_kg: 1800, total_km: 28.2, total_duration_min: 84, utilization_pct: 31.3,
      stops: [toStop(orders[2])],
    },
  ],
  unassigned_sts: [],
  total_km: 70.7,
  fleet_utilization_pct: 47.1,
  tw_violations: 0,
  score: 46.4,
  solver_used: "clarke-wright",
  solve_time_ms: 37,
};

function toStop(order) {
  return {
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
    tw_strict: Boolean(order.TW_STRICT),
  };
}

async function installMocks(page) {
  await page.route("**/api/admin/transport/planner/orders?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(orders) }));
  await page.route("**/api/admin/transport/routing/status", route => route.fulfill({ contentType: "application/json", body: JSON.stringify({ provider: "haversine", provider_available: true, total_addresses: 3, geocoded_count: 3, ungeocoded_count: 0 }) }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент 10т" }, { TRANSPORTTYPE: "15", NAME: "Тент 15т" }]) }));
  await page.route("**/api/admin/transport/planner/templates?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ plan_id: 77001, plan_date: "2026-05-18", score: 61.2, jaccard: 0.92, routes_count: 2, matched_sts: 3, total_current_sts: 3 }]) }));
  await page.route("**/api/admin/transport/planner/solve", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(plan) }));
  await page.route("**/api/admin/transport/planner/apply", route => route.fulfill({ contentType: "application/json", body: JSON.stringify({ tasks_created: 2 }) }));
  await page.route("**/api/admin/transport/planner/history?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([
    { plan_id: 1001, plan_date: "2026-05-24", solver: "clarke-wright", score: 72.4, routes: 3, total_km: 240, fleet_utilization_pct: 86.5, tw_violations: 0, applied: true },
    { plan_id: 1002, plan_date: "2026-05-25", solver: "dbscan-cluster", score: 69.1, routes: 4, total_km: 310, fleet_utilization_pct: 81.2, tw_violations: 1, applied: false },
  ]) }));
  await page.route("**/api/admin/transport/planner/demand-forecast?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify({ target_date: "2026-05-25", day_of_week: 0, forecast_sts: 77, confidence: "high", samples: 8, sample_counts: [70, 74, 76, 77, 79, 80, 75, 78], stddev: 3.1 }) }));
  await page.route(/https:\/\/.*\.tile\.openstreetmap\.org\/.*/, route => route.fulfill({ contentType: "image/png", body: Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAFgwJ/lk0ITwAAAABJRU5ErkJggg==", "base64") }));
}

async function shot(page, name) {
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", name), fullPage: true });
}

async function openFirstMarkerPopup(page) {
  const markers = page.locator(".leaflet-interactive");
  const count = await markers.count();
  for (let index = 0; index < count; index += 1) {
    const box = await markers.nth(index).boundingBox().catch(() => null);
    if (box) {
      await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
    } else {
      await markers.nth(index).click({ force: true }).catch(() => {});
    }
    try {
      await page.getByText(/СТ ДЦСТ-/).waitFor({ timeout: 700 });
      return;
    } catch {
      // try the next interactive Leaflet element
    }
  }
  throw new Error(`Could not open marker popup, interactive elements=${count}`);
}

function html() {
  return `<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>ТМС-2 Block II: MAP / VRP</title>
  <style>
    body { margin: 0; font-family: Arial, sans-serif; color: #172033; background: #f4f7fb; }
    header { padding: 28px 36px; background: #174035; color: white; }
    main { max-width: 1180px; margin: 0 auto; padding: 28px 24px 48px; }
    section { background: white; border: 1px solid #d8e0ea; border-radius: 8px; padding: 22px; margin: 0 0 22px; }
    h1, h2 { margin-top: 0; }
    h2 { color: #174035; }
    .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
    .card { background: #f8fbff; border: 1px solid #d8e0ea; border-radius: 6px; padding: 14px; }
    img { width: 100%; border: 1px solid #c7d2e0; border-radius: 6px; display: block; }
    figure { margin: 0 0 24px; }
    figcaption { font-size: 14px; color: #41516a; margin-top: 8px; line-height: 1.45; }
    table { width: 100%; border-collapse: collapse; }
    td, th { border: 1px solid #d8e0ea; padding: 8px; vertical-align: top; }
    th { background: #eef4fb; text-align: left; }
    code { background: #eef4fb; padding: 1px 4px; border-radius: 3px; }
  </style>
</head>
<body>
  <header>
    <h1>ТМС-2 Block II: MAP / VRP</h1>
    <p>Sprint 7-10. Карта заказов, матрица расстояний, автоплан рейсов, кластеры, шаблоны и аналитика.</p>
  </header>
  <main>
    <section>
      <h2>Зачем этот блок</h2>
      <p>Block II превращает список СТ в географическую картину дня: диспетчер видит точки на карте, запускает VRP-оптимизатор, получает маршруты по машинам, применяет план и анализирует качество планирования.</p>
      <div class="grid">
        <div class="card"><b>Вход</b><br>СТ с адресами, координатами, паллетами, весом, типом ТС и временными окнами.</div>
        <div class="card"><b>Процесс</b><br>Карта заказов, матрица расстояний, VRP, кластерный solver, исторические шаблоны.</div>
        <div class="card"><b>Результат</b><br>План рейсов с маршрутами, метриками, утилизацией, применением и аналитикой.</div>
      </div>
    </section>
    <section>
      <h2>Структура данных</h2>
      <table>
        <tr><th>Объект</th><th>Поля</th><th>Источник</th></tr>
        <tr><td>Заказ на карте</td><td><code>ST_NUMBER</code>, <code>LAT/LON</code>, <code>PALLETS_COUNT</code>, <code>TRANSPORT_TYPE</code>, <code>TW_STRICT</code>, <code>UNLOAD_NORM_MIN</code></td><td><code>RRL_SBORKA_PALLETS</code>, <code>RRL_ADDR</code></td></tr>
        <tr><td>Матрица расстояний</td><td><code>FROM_ADDR</code>, <code>TO_ADDR</code>, <code>DISTANCE_KM</code>, <code>DURATION_MIN</code>, <code>SOURCE</code></td><td><code>RRL_ADDR_DISTANCE_MATRIX</code></td></tr>
        <tr><td>VRP-план</td><td><code>PLAN_DATE</code>, <code>SOLVER</code>, <code>SCORE</code>, <code>PAYLOAD</code>, <code>APPLIED_AT</code></td><td><code>RRL_PLANNER_PLANS</code></td></tr>
      </table>
    </section>
    <section>
      <h2>Как работать</h2>
      <figure><img src="screenshots/01_map_orders.png" alt="Карта заказов" /><figcaption><b>1. Карта заказов.</b> СТ отображаются как точки на карте. Размер показывает паллеты, цвет связан со складом, статус геокодирования виден в левой панели.</figcaption></figure>
      <figure><img src="screenshots/02_marker_popup.png" alt="Карточка СТ" /><figcaption><b>2. Карточка СТ.</b> Клик по маркеру открывает адрес, район, паллеты, вес, дату, тип ТС, жесткое окно и требования к гидроборту.</figcaption></figure>
      <figure><img src="screenshots/03_vrp_plan.png" alt="VRP план" /><figcaption><b>3. Авто-план.</b> Кнопка «Авто-план» запускает solver. Справа появляются рейсы, машины, загрузка, пробег, длительность, score и список остановок.</figcaption></figure>
      <figure><img src="screenshots/04_clusters_templates.png" alt="Кластеры и шаблоны" /><figcaption><b>4. Кластеры и шаблоны.</b> Слой кластеров помогает работать районами, а блок похожих маршрутов предлагает исторические планы с Jaccard-сходством.</figcaption></figure>
      <figure><img src="screenshots/05_apply_plan.png" alt="Применение плана" /><figcaption><b>5. Применение плана.</b> После проверки маршрутов диспетчер применяет план: система создает рейсы через транспортные Oracle-функции.</figcaption></figure>
      <figure><img src="screenshots/06_analytics.png" alt="Аналитика" /><figcaption><b>6. Аналитика.</b> Вкладка показывает историю планов, среднюю утилизацию, лучший Score, настройки целевой функции и прогноз спроса.</figcaption></figure>
    </section>
    <section>
      <h2>Бизнес-процессы</h2>
      <ol>
        <li><b>Географическая оценка дня:</b> открыть карту, проверить количество СТ на карте, адреса без координат и требования к ТС.</li>
        <li><b>Расчет расстояний:</b> пересчитать матрицу расстояний по активному routing provider, сохранить пары адресов в Oracle.</li>
        <li><b>Автопланирование:</b> запустить VRP solver, получить набор рейсов с остановками, пробегом, загрузкой и нарушениями временных окон.</li>
        <li><b>Ручная корректировка:</b> включить кластеры, выделять районы, смотреть похожие исторические маршруты и применять подходящий шаблон.</li>
        <li><b>Применение плана:</b> создать рейсы из утвержденного плана, не превращая partial-success в success.</li>
        <li><b>Аналитика качества:</b> сравнить планы по Score, утилизации, пробегу и прогнозу числа СТ.</li>
      </ol>
    </section>
    <section>
      <h2>Результат проверки</h2>
      <p>Block II Sprint 7-10 прошёл fresh hardening gate: functional <code>62 passed, 1 skipped</code>, UI smoke Sprint 7-10 passed, load NFR Sprint 7-10 passed. Единственный backend skip — отсутствие historical-plan Oracle fixture для шаблонов Sprint 9.</p>
    </section>
  </main>
</body>
</html>`;
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  page.on("dialog", dialog => dialog.accept());
  await installMocks(page);

  await page.goto(APP_URL);
  await page.getByRole("heading", { name: "Планировщик маршрутов" }).waitFor({ timeout: 10000 });
  await page.locator(".leaflet-interactive").first().waitFor({ timeout: 10000 });
  await shot(page, "01_map_orders.png");

  await openFirstMarkerPopup(page);
  await shot(page, "02_marker_popup.png");
  await page.keyboard.press("Escape").catch(() => {});

  await page.getByRole("button", { name: /Авто-план/ }).click();
  await page.locator(".planner-rp-title", { hasText: "Рейсов: 2" }).waitFor({ timeout: 5000 });
  await page.locator(".planner-rp-vehicle", { hasText: "В 415 ТТ 59" }).click();
  await page.getByText("ДЦСТ-П70001").waitFor({ timeout: 5000 });
  await shot(page, "03_vrp_plan.png");

  await page.getByLabel(/Слой кластеров/).check();
  await page.locator(".planner-tmpl-load-btn").click();
  await page.getByText("Jaccard 92%").waitFor({ timeout: 5000 });
  await shot(page, "04_clusters_templates.png");

  await page.getByRole("button", { name: /Применить план/ }).click();
  await page.getByText("Создано рейсов: 2").waitFor({ timeout: 5000 });
  await shot(page, "05_apply_plan.png");

  await page.getByRole("button", { name: "Аналитика" }).click();
  await page.getByText("История планов").waitFor({ timeout: 5000 });
  await page.getByText("Уверенность: высокая").waitFor({ timeout: 5000 });
  await shot(page, "06_analytics.png");

  await browser.close();
  fs.writeFileSync(path.join(OUT_DIR, "index.html"), html(), "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
