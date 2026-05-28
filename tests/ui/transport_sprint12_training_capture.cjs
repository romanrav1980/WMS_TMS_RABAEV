const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=gantt";
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint12_gantt_dashboard_2026_05_28");

const vehicles = [
  {
    vehicle_id: 9201,
    vehicle_num: "В 415 ТТ 59",
    vehicle_type: "10т",
    operations: [
      { op_id: 1201, tt_id: 6201, operation_code: "DOCK_ASSIGN", ord: 1, duration_min: 10, plan_start: "2026-05-25 06:00", plan_end: "2026-05-25 06:10", fact_start: "2026-05-25 06:04", fact_end: "2026-05-25 06:14", delta_min: 4, note: null },
      { op_id: 1202, tt_id: 6201, operation_code: "LOADING", ord: 2, duration_min: 35, plan_start: "2026-05-25 06:10", plan_end: "2026-05-25 06:45", fact_start: "2026-05-25 06:14", fact_end: "2026-05-25 06:55", delta_min: 10, note: null },
      { op_id: 1203, tt_id: 6201, operation_code: "DRIVE", ord: 3, duration_min: 70, plan_start: "2026-05-25 06:45", plan_end: "2026-05-25 07:55", fact_start: null, fact_end: null, delta_min: null, note: null },
      { op_id: 1204, tt_id: 6201, operation_code: "UNLOAD", ord: 4, duration_min: 45, plan_start: "2026-05-25 07:55", plan_end: "2026-05-25 08:40", fact_start: null, fact_end: null, delta_min: null, note: null },
    ],
  },
  {
    vehicle_id: 9202,
    vehicle_num: "Е 714 НО 59",
    vehicle_type: "15т",
    operations: [
      { op_id: 2201, tt_id: 6202, operation_code: "REST", ord: 1, duration_min: 30, plan_start: "2026-05-25 09:00", plan_end: "2026-05-25 09:30", fact_start: null, fact_end: null, delta_min: null, note: null },
      { op_id: 2202, tt_id: 6202, operation_code: "LOAD_RETURNS", ord: 2, duration_min: 20, plan_start: "2026-05-25 09:30", plan_end: "2026-05-25 09:50", fact_start: "2026-05-25 09:42", fact_end: "2026-05-25 10:08", delta_min: 18, note: null },
    ],
  },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles/gantt?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(vehicles) }));
  await page.route("**/api/admin/transport/plan-fact?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function shot(page, name) {
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", name), fullPage: true });
}

function html() {
  return `<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>ТМС-2 Sprint 12: Диаграмма Ганта</title>
  <style>
    body { margin: 0; font-family: Arial, sans-serif; color: #172033; background: #f4f7fb; }
    header { padding: 28px 36px; background: #1f3658; color: white; }
    main { max-width: 1180px; margin: 0 auto; padding: 28px 24px 48px; }
    section { background: white; border: 1px solid #d8e0ea; border-radius: 8px; padding: 22px; margin: 0 0 22px; }
    h1, h2 { margin-top: 0; }
    h2 { color: #1f3658; }
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
    <h1>ТМС-2 Sprint 12: Диаграмма Ганта</h1>
    <p>Визуальный диспетчерский экран загрузки машин на день.</p>
  </header>
  <main>
    <section>
      <h2>Зачем этот блок</h2>
      <p>Диаграмма Ганта дает диспетчеру обзор дня: какие машины на базе, какие грузятся, какие уже в рейсе, где есть отклонения и что будет следующим.</p>
      <div class="grid">
        <div class="card"><b>Вход</b><br>Операции рейсов на выбранную дату, сгруппированные по машинам.</div>
        <div class="card"><b>Процесс</b><br>Просмотр временной шкалы, фильтр машин, hover-подсказки, дата-навигация и контроль отклонений.</div>
        <div class="card"><b>Результат</b><br>Единая картина загрузки транспорта и быстрый переход к проблемным рейсам.</div>
      </div>
    </section>
    <section>
      <h2>Структура данных</h2>
      <table>
        <tr><th>Уровень</th><th>Поля</th><th>Зачем нужно</th></tr>
        <tr><td>Машина</td><td><code>vehicle_id</code>, <code>vehicle_num</code>, <code>vehicle_type</code></td><td>Строка Ганта и статус транспорта.</td></tr>
        <tr><td>Операция</td><td><code>operation_code</code>, <code>plan_start</code>, <code>plan_end</code>, <code>fact_start</code>, <code>fact_end</code>, <code>delta_min</code></td><td>Цветной блок на временной шкале.</td></tr>
        <tr><td>Сводка</td><td>статусы машин, ближайшие операции, отклонения</td><td>Оперативное управление сменой.</td></tr>
      </table>
    </section>
    <section>
      <h2>Как работать</h2>
      <figure><img src="screenshots/01_dashboard.png" alt="Обзор Ганта" /><figcaption><b>1. Обзор дня.</b> Выберите дату. Слева машины, справа цветные блоки операций: склад, переезд, разгрузка, возвраты, перерыв, смена.</figcaption></figure>
      <figure><img src="screenshots/02_tooltip.png" alt="Hover подсказка" /><figcaption><b>2. Подсказка операции.</b> Наведение на блок показывает операцию, план, факт, дельту и длительность.</figcaption></figure>
      <figure><img src="screenshots/03_filter.png" alt="Фильтр машины" /><figcaption><b>3. Фильтр машины.</b> Фильтр по госномеру оставляет только нужную машину, чтобы разобрать конкретный рейс без шума.</figcaption></figure>
      <figure><img src="screenshots/04_deviations.png" alt="Отклонения" /><figcaption><b>4. Отклонения.</b> Нижняя панель показывает фактические отклонения по машинам и операциям, чтобы диспетчер видел, где день пошел не по плану.</figcaption></figure>
    </section>
    <section>
      <h2>Бизнес-процессы</h2>
      <ol>
        <li><b>Утренний контроль выпуска:</b> открыть дату и проверить, что все машины имеют плановые операции.</li>
        <li><b>Мониторинг смены:</b> смотреть текущие статусы, ближайшие операции и машины в рейсе.</li>
        <li><b>Работа с отклонениями:</b> найти операцию с дельтой, открыть карточку рейса и принять диспетчерское решение.</li>
        <li><b>Фокус по машине:</b> отфильтровать госномер и проверить цепочку одной машины.</li>
      </ol>
    </section>
    <section>
      <h2>Результат проверки</h2>
      <p>Sprint 12 закрыт функционально: backend tests <code>12 passed</code>, UI smoke passed, load NFR passed. Проверены загрузка Ганта, легенда, сводка, hover tooltip, фильтр машин, дата-навигация и панель отклонений.</p>
    </section>
  </main>
</body>
</html>`;
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);

  await page.goto(APP_URL);
  await page.getByRole("heading", { name: "Диаграмма Ганта" }).waitFor({ timeout: 10000 });
  await page.locator(".gantt-date-input").fill("2026-05-25");
  await page.locator(".gantt-veh-num", { hasText: "В 415 ТТ 59" }).waitFor({ timeout: 5000 });
  await shot(page, "01_dashboard.png");

  await page.locator("svg rect[fill='#52C41A']").first().hover();
  await page.locator(".gantt-tooltip", { hasText: "Переезд" }).waitFor({ timeout: 5000 });
  await shot(page, "02_tooltip.png");

  await page.locator(".gantt-veh-filter").fill("Е 714");
  await page.locator(".gantt-veh-num", { hasText: "Е 714 НО 59" }).waitFor({ timeout: 5000 });
  await shot(page, "03_filter.png");

  await page.locator(".gantt-veh-filter").fill("");
  await page.locator(".gantt-panel-delta", { hasText: "+18 мин" }).waitFor({ timeout: 5000 });
  await shot(page, "04_deviations.png");

  await browser.close();
  fs.writeFileSync(path.join(OUT_DIR, "index.html"), html(), "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
