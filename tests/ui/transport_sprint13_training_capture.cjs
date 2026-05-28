const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint13_vehicle_availability_2026_05_28");

const availableSts = [
  { ST_NUMBER: "ДЦСТ-П13001", ADDR: "Адрес Sprint 13", REGION: "Пермь", RAION: "Центр", ORD: 1, TRANSPORT_TYPE: "10", NEEDS_HYDRO_BOARD: 0, STOL: 0, PRIM1: "", WARE_ID: 9201, NAPR: "Пермь", PALLETS_COUNT: 4, WEIGHT_KG: 1000, VOLUME_M3: 3.1, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 100, SUGAR: 0 },
];
const vehicles = [
  { ID: 1, NUM: "А 100 АА 59", MARKA: "Газель", TR_TYPE: "5", PALLETS: 8, GIDROBORT: 0 },
  { ID: 2, NUM: "В 200 ВВ 59", MARKA: "Тент", TR_TYPE: "10", PALLETS: 18, GIDROBORT: 1 },
  { ID: 3, NUM: "С 300 СС 59", MARKA: "Фура", TR_TYPE: "20", PALLETS: 33, GIDROBORT: 0 },
];
const availability = [
  { vehicle_id: 1, vehicle_num: "А 100 АА 59", vehicle_type: "5", marka: "Газель", max_pallets: 8, gidrobort: false, free_at: null, delay_min: 0, status: "green", detail: "Свободна" },
  { vehicle_id: 2, vehicle_num: "В 200 ВВ 59", vehicle_type: "10", marka: "Тент", max_pallets: 18, gidrobort: true, free_at: "09:35", delay_min: 35, status: "yellow", detail: "Освободится в 09:35" },
  { vehicle_id: 3, vehicle_num: "С 300 СС 59", vehicle_type: "20", marka: "Фура", max_pallets: 33, gidrobort: false, free_at: "12:30", delay_min: 210, status: "red", detail: "Занята до 12:30" },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles/available?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(availability) }));
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(vehicles) }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент 10т" }]) }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(availableSts) }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function shot(page, name) {
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", name), fullPage: true });
}

function html() {
  return `<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>ТМС-2 Sprint 13: Подбор машины</title>
  <style>
    body { margin: 0; font-family: Arial, sans-serif; color: #172033; background: #f4f7fb; }
    header { padding: 28px 36px; background: #284b3b; color: white; }
    main { max-width: 1180px; margin: 0 auto; padding: 28px 24px 48px; }
    section { background: white; border: 1px solid #d8e0ea; border-radius: 8px; padding: 22px; margin: 0 0 22px; }
    h1, h2 { margin-top: 0; }
    h2 { color: #284b3b; }
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
    <h1>ТМС-2 Sprint 13: Умный подбор машины</h1>
    <p>Доступность транспорта в момент создания рейса и предупреждение о конфликте.</p>
  </header>
  <main>
    <section>
      <h2>Зачем этот блок</h2>
      <p>Sprint 13 помогает диспетчеру не назначить рейс на занятую или неподходящую машину. Система показывает свободные, задерживающиеся и конфликтные машины прямо в диалоге создания маршрута.</p>
      <div class="grid">
        <div class="card"><b>Вход</b><br>Дата/время отгрузки, требуемые паллеты, список машин и их текущий Гант.</div>
        <div class="card"><b>Процесс</b><br>API считает доступность, UI показывает зеленые/желтые/красные статусы.</div>
        <div class="card"><b>Результат</b><br>Диспетчер выбирает свободную машину или видит предупреждение о конфликте.</div>
      </div>
    </section>
    <section>
      <h2>Структура данных</h2>
      <table>
        <tr><th>Поле</th><th>Смысл</th></tr>
        <tr><td><code>vehicle_num</code>, <code>vehicle_type</code>, <code>marka</code></td><td>Идентификация машины в диалоге.</td></tr>
        <tr><td><code>max_pallets</code>, <code>gidrobort</code></td><td>Ограничения вместимости и оборудования.</td></tr>
        <tr><td><code>free_at</code>, <code>delay_min</code>, <code>status</code>, <code>detail</code></td><td>Результат проверки доступности.</td></tr>
      </table>
    </section>
    <section>
      <h2>Как работать</h2>
      <figure><img src="screenshots/01_dialog_availability.png" alt="Доступность машин" /><figcaption><b>1. Открыть создание маршрута.</b> После выбора СТ диалог загружает доступность машин на дату и время отгрузки.</figcaption></figure>
      <figure><img src="screenshots/02_red_conflict.png" alt="Конфликт машины" /><figcaption><b>2. Красная машина.</b> При выборе занятой машины система показывает предупреждение и причину конфликта.</figcaption></figure>
      <figure><img src="screenshots/03_yellow_warning.png" alt="Желтая машина" /><figcaption><b>3. Желтая машина.</b> Если машина освобождается с небольшой задержкой, диспетчер видит мягкое предупреждение.</figcaption></figure>
    </section>
    <section>
      <h2>Бизнес-процессы</h2>
      <ol>
        <li><b>Создание рейса:</b> выбрать СТ, открыть диалог, получить актуальный список машин.</li>
        <li><b>Проверка доступности:</b> система сравнивает требуемое время с последним окончанием операций машины.</li>
        <li><b>Проверка вместимости:</b> если паллет больше вместимости машины, статус становится красным.</li>
        <li><b>Решение диспетчера:</b> выбрать зеленую машину или осознанно обработать желтый/красный конфликт.</li>
      </ol>
    </section>
    <section>
      <h2>Результат проверки</h2>
      <p>Sprint 13 закрыт функционально: backend tests <code>16 passed</code>, UI smoke passed, load NFR passed. Проверены API доступности, plan-fact API, статусы green/yellow/red, предупреждения UI и производительность.</p>
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
  await page.getByText("ДЦСТ-П13001").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-grid tbody input[type='checkbox']").first().check();
  await page.getByText("+ Создать маршрут (1)").click();
  await page.getByRole("heading", { name: /Создать маршрут/ }).waitFor({ timeout: 5000 });
  await page.waitForFunction(() => document.body.textContent.includes("А 100 АА 59"), null, { timeout: 5000 });
  await shot(page, "01_dialog_availability.png");

  const vehicleSelect = page.locator(".dispatch-dialog-field", { hasText: "Машина" }).locator("select");
  await vehicleSelect.selectOption("С 300 СС 59");
  await page.getByText("Занята до 12:30 — конфликт возможен").waitFor({ timeout: 5000 });
  await shot(page, "02_red_conflict.png");

  await vehicleSelect.selectOption("В 200 ВВ 59");
  await page.getByText("Освободится в 09:35").waitFor({ timeout: 5000 });
  await shot(page, "03_yellow_warning.png");

  await browser.close();
  fs.writeFileSync(path.join(OUT_DIR, "index.html"), html(), "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
