const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=gantt";
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint11_arm_gantt_2026_05_28");

const operations = [
  { op_id: 111, tt_id: 6101, operation_code: "DOCK_ASSIGN", ord: 1, duration_min: 10, plan_start: "2026-05-25 06:00", plan_end: "2026-05-25 06:10", fact_start: "2026-05-25 06:04", fact_end: "2026-05-25 06:14", delta_min: 4, note: null },
  { op_id: 112, tt_id: 6101, operation_code: "WAIT_LOAD", ord: 2, duration_min: 10, plan_start: "2026-05-25 06:10", plan_end: "2026-05-25 06:20", fact_start: "2026-05-25 06:14", fact_end: "2026-05-25 06:24", delta_min: 4, note: null },
  { op_id: 113, tt_id: 6101, operation_code: "LOADING", ord: 3, duration_min: 35, plan_start: "2026-05-25 06:20", plan_end: "2026-05-25 06:55", fact_start: "2026-05-25 06:24", fact_end: "2026-05-25 07:04", delta_min: 9, note: null },
  { op_id: 114, tt_id: 6101, operation_code: "DEPART", ord: 4, duration_min: 5, plan_start: "2026-05-25 06:55", plan_end: "2026-05-25 07:00", fact_start: null, fact_end: null, delta_min: null, note: null },
  { op_id: 115, tt_id: 6101, operation_code: "DRIVE", ord: 5, duration_min: 70, plan_start: "2026-05-25 07:00", plan_end: "2026-05-25 08:10", fact_start: null, fact_end: null, delta_min: null, note: null },
  { op_id: 116, tt_id: 6101, operation_code: "UNLOAD", ord: 6, duration_min: 45, plan_start: "2026-05-25 08:10", plan_end: "2026-05-25 08:55", fact_start: null, fact_end: null, delta_min: null, note: null },
];

const gantt = [
  { vehicle_id: 9201, vehicle_num: "В 415 ТТ 59", vehicle_type: "10т", operations },
  {
    vehicle_id: 9202,
    vehicle_num: "Е 714 НО 59",
    vehicle_type: "15т",
    operations: [
      { op_id: 211, tt_id: 6102, operation_code: "DOCK_ASSIGN", ord: 1, duration_min: 10, plan_start: "2026-05-25 08:30", plan_end: "2026-05-25 08:40", fact_start: null, fact_end: null, delta_min: null, note: null },
      { op_id: 212, tt_id: 6102, operation_code: "LOADING", ord: 2, duration_min: 40, plan_start: "2026-05-25 08:40", plan_end: "2026-05-25 09:20", fact_start: null, fact_end: null, delta_min: null, note: null },
      { op_id: 213, tt_id: 6102, operation_code: "DRIVE", ord: 3, duration_min: 80, plan_start: "2026-05-25 09:20", plan_end: "2026-05-25 10:40", fact_start: null, fact_end: null, delta_min: null, note: null },
    ],
  },
];

const planFact = [
  { tt_id: 6101, vehicle: "В 415 ТТ 59", shipment_date: "2026-05-25", status: "В рейсе", total_delta_min: 17, rest_violations: 0, operations },
  { tt_id: 6102, vehicle: "Е 714 НО 59", shipment_date: "2026-05-25", status: "План", total_delta_min: 0, rest_violations: 0, operations: gantt[1].operations },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles/gantt?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(gantt) }));
  await page.route("**/api/admin/transport/plan-fact?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(planFact) }));
  await page.route("**/api/admin/transport/operations/111/fact", route => route.fulfill({ contentType: "application/json", body: JSON.stringify({ updated: true }) }));
}

async function shot(page, name) {
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", name), fullPage: true });
}

function html() {
  return `<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>ТМС-2 Sprint 11: ARM / Диаграмма Ганта</title>
  <style>
    body { margin: 0; font-family: Arial, sans-serif; color: #172033; background: #f4f7fb; }
    header { padding: 28px 36px; background: #243b53; color: white; }
    main { max-width: 1180px; margin: 0 auto; padding: 28px 24px 48px; }
    section { background: white; border: 1px solid #d8e0ea; border-radius: 8px; padding: 22px; margin: 0 0 22px; }
    h1, h2 { margin-top: 0; }
    h2 { color: #243b53; }
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
    <h1>ТМС-2 Sprint 11: ARM / Диаграмма Ганта</h1>
    <p>Операционная цепочка рейса, отметка факта и план-факт контроль диспетчера.</p>
  </header>
  <main>
    <section>
      <h2>Зачем этот блок</h2>
      <p>Sprint 11 переводит рейс из одной строки диспетчера в управляемую цепочку операций. Диспетчер видит загрузку, выезд, движение, разгрузку и возвраты на временной шкале, фиксирует факт и сразу видит отклонения.</p>
      <div class="grid">
        <div class="card"><b>Вход</b><br>Рейс, дата отгрузки, машина, нормативы операций и плановое время.</div>
        <div class="card"><b>Процесс</b><br>Построить операции, контролировать Гант, открыть карточку рейса, отметить факт.</div>
        <div class="card"><b>Результат</b><br>Операционный таймлайн, факт выполнения, отклонения и план-факт отчет.</div>
      </div>
    </section>
    <section>
      <h2>Структура данных</h2>
      <table>
        <tr><th>Объект</th><th>Поля</th><th>Назначение</th></tr>
        <tr><td>Операция рейса</td><td><code>op_id</code>, <code>tt_id</code>, <code>operation_code</code>, <code>ord</code>, <code>duration_min</code></td><td>Шаг жизненного цикла рейса.</td></tr>
        <tr><td>План</td><td><code>plan_start</code>, <code>plan_end</code></td><td>Расчетная цепочка по нормативам.</td></tr>
        <tr><td>Факт</td><td><code>fact_start</code>, <code>fact_end</code>, <code>delta_min</code></td><td>Реальное выполнение и отклонение от плана.</td></tr>
        <tr><td>Гант машины</td><td><code>vehicle_id</code>, <code>vehicle_num</code>, <code>vehicle_type</code>, <code>operations</code></td><td>Группировка операций по машинам на день.</td></tr>
      </table>
    </section>
    <section>
      <h2>Как работать</h2>
      <figure><img src="screenshots/01_gantt_overview.png" alt="Диаграмма Ганта" /><figcaption><b>1. Диаграмма Ганта.</b> Откройте дату: слева машины, справа операции по времени. Цвета показывают склад, переезд, разгрузку и возвраты.</figcaption></figure>
      <figure><img src="screenshots/02_task_card.png" alt="Карточка рейса" /><figcaption><b>2. Карточка рейса.</b> Клик по операции открывает рейс и всю цепочку операций с планом, фактом и отклонениями.</figcaption></figure>
      <figure><img src="screenshots/03_fact_modal.png" alt="Отметка факта" /><figcaption><b>3. Отметка факта.</b> Контекстное меню операции открывает ввод фактического начала и окончания. Сохранение пишет факт в API операции.</figcaption></figure>
      <figure><img src="screenshots/04_plan_fact.png" alt="План-факт" /><figcaption><b>4. План-факт анализ.</b> Вкладка «Аналитика» показывает суммарное отклонение по рейсу, детали операций и экспорт CSV.</figcaption></figure>
    </section>
    <section>
      <h2>Бизнес-процессы</h2>
      <ol>
        <li><b>Планирование операций:</b> для рейса строится последовательная цепочка нормативных операций без разрывов времени.</li>
        <li><b>Оперативный контроль:</b> диспетчер смотрит машины на временной шкале и видит текущие/будущие операции.</li>
        <li><b>Разбор рейса:</b> карточка рейса показывает всю цепочку, план, факт и отклонения по шагам.</li>
        <li><b>Фиксация факта:</b> диспетчер или водительский интерфейс записывает фактические времена операции.</li>
        <li><b>План-факт управление:</b> отклонения агрегируются по рейсу и используются для контроля качества исполнения.</li>
      </ol>
    </section>
    <section>
      <h2>Результат проверки</h2>
      <p>Sprint 11 закрыт функционально: backend tests <code>20 passed</code>, UI smoke passed, load NFR passed. Проверены планирование операций, чтение цепочки, фиксация факта, Гант по машинам и план-факт экран.</p>
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
  await shot(page, "01_gantt_overview.png");

  const firstOp = page.locator("svg rect[fill='#4A90D9']").first();
  await firstOp.click();
  await page.getByText("Цепочка операций").waitFor({ timeout: 5000 });
  await shot(page, "02_task_card.png");
  await page.getByRole("button", { name: "Закрыть" }).click();

  await firstOp.click({ button: "right" });
  await page.getByText("Отметить факт").click();
  await page.getByText("Отметить факт · Ворота").waitFor({ timeout: 5000 });
  await shot(page, "03_fact_modal.png");
  await page.getByRole("button", { name: "Отмена" }).click();

  await page.getByRole("button", { name: "Аналитика" }).click();
  await page.getByText("План-факт анализ").waitFor({ timeout: 5000 });
  await shot(page, "04_plan_fact.png");

  await browser.close();
  fs.writeFileSync(path.join(OUT_DIR, "index.html"), html(), "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
