const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const OUT_DIR = path.resolve("wiki-raw/tms2_training/block_i_sprint1_6_2026_05_28");

const available = [
  {
    ST_NUMBER: "ДЦСТ-П10001", ADDR: "Добра Цен #П01, г. Пермь, ул. Ленина 10",
    REGION: "г. Пермь", RAION: "Дзержинский", ORD: 1, TRANSPORT_TYPE: "10",
    NEEDS_HYDRO_BOARD: 0, STOL: 0, PRIM1: null, WARE_ID: 9201, NAPR: "Дзержинский",
    PALLETS_COUNT: 4, WEIGHT_KG: 595, VOLUME_M3: 1.43, STDATE: "2026-05-25T00:00:00",
    DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 100, SUGAR: 0
  },
  {
    ST_NUMBER: "ДЦСТ-П10002", ADDR: "Добра Цен #П02, г. Пермь, ул. Гагарина 18",
    REGION: "г. Пермь", RAION: "Дзержинский", ORD: 2, TRANSPORT_TYPE: "15",
    NEEDS_HYDRO_BOARD: 1, STOL: 1, PRIM1: "Гидроборт", WARE_ID: 9201, NAPR: "Дзержинский",
    PALLETS_COUNT: 3, WEIGHT_KG: 468, VOLUME_M3: 1.11, STDATE: "2026-05-25T00:00:00",
    DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 50, SUGAR: 1
  },
  {
    ST_NUMBER: "ДЦСТ-П10003", ADDR: "Добра Цен #П03, г. Пермь, ул. Советская 34",
    REGION: "г. Пермь", RAION: "Ленинский", ORD: 3, TRANSPORT_TYPE: "10",
    NEEDS_HYDRO_BOARD: 0, STOL: 0, PRIM1: null, WARE_ID: 9201, NAPR: "Ленинский",
    PALLETS_COUNT: 5, WEIGHT_KG: 735, VOLUME_M3: 1.77, STDATE: "2026-05-25T00:00:00",
    DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: 6001, VERIFY_PERC: 0, SUGAR: 0
  }
];

const task = {
  ID: 6001, CREATEDATE: "2026-05-25T09:00:00", TRANSPORT: "A001AA",
  TRANSTYPE: "10", CONDITION: "Новый", SHIPMENT_DATE: "2026-05-25T00:00:00",
  VODITEL_ID: 1, VODITEL_NAME: "Иванов Иван", VODITEL_TEL: "79990000000",
  TK_NAME: "ТК Тест", IS_OWN_DRIVER: 0, PRIMECHANIE: "Учебный рейс Block I",
  DOCK: "Д1", SHIPMENT_TIME: "2026-05-25T09:00:00", TEMP_REGION: "г. Пермь",
  REGIONS: "г. Пермь", TEMP_WEIGHT: 1330, PRICE: 12000, DELETED: 0,
  LOGIST: "admin", PAY_ORDER_ID: null, PALLET_COUNT: 9, ST_COUNT: 2,
  VOLUME_M3: 3.2, READY_PERC: 75, UNREADY_COUNT: 2
};

const composition = [
  { ST_NUMBER: "ДЦСТ-П10001", ADDR: "Добра Цен #П01", REGION: "г. Пермь", RAION: "Дзержинский", ORD: 1, PALLETS_COUNT: 4, WEIGHT_KG: 595, STDATE: "2026-05-25T00:00:00", ZONE: "A", TIME_FROM: "09:00", TIME_TO: "10:00", LOAD_TYPE: "Г", WARE_ID: 9201, VERIFY_PERC: 100 },
  { ST_NUMBER: "ДЦСТ-П10002", ADDR: "Добра Цен #П02", REGION: "г. Пермь", RAION: "Дзержинский", ORD: 2, PALLETS_COUNT: 3, WEIGHT_KG: 468, STDATE: "2026-05-25T00:00:00", ZONE: "B", TIME_FROM: "10:00", TIME_TO: "11:00", LOAD_TYPE: "П", WARE_ID: 9201, VERIFY_PERC: 50 }
];

const pallets = [
  { PALLET_UID: "PAL-B1-001", ZONE: "A", LOAD_TYPE: "Г", ORD: 1, ARTICUL: "Т0000008795", ORDER_WEIGHT: 120, PACK_COUNT: 6, ROW_VOLUME_M3: 0.123 },
  { PALLET_UID: "PAL-B1-002", ZONE: "A", LOAD_TYPE: "Г", ORD: 1, ARTICUL: "Т0000127793", ORDER_WEIGHT: 180, PACK_COUNT: 8, ROW_VOLUME_M3: 0.222 }
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", r => r.fulfill({ contentType: "application/json", body: JSON.stringify([{ ID: 1, NUM: "A001AA", MARKA: "Газель", TR_TYPE: "10", PALLETS: 10, GIDROBORT: 1 }]) }));
  await page.route("**/api/admin/transport/drivers", r => r.fulfill({ contentType: "application/json", body: JSON.stringify([{ ID: 1, FULL_NAME: "Иванов Иван", SOBSTVENNYY: 0, DOVERENNOST_OT: "ТК Тест" }]) }));
  await page.route("**/api/admin/transport/types", r => r.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент 10т" }, { TRANSPORTTYPE: "15", NAME: "Тент 15т" }]) }));
  await page.route("**/api/admin/transport/available-sts?**", r => r.fulfill({ contentType: "application/json", body: JSON.stringify(available) }));
  await page.route("**/api/admin/transport/tasks?**", r => r.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/6001/sts", r => r.fulfill({ contentType: "application/json", body: JSON.stringify(composition) }));
  await page.route("**/api/admin/transport/sts/**/pallets", r => r.fulfill({ contentType: "application/json", body: JSON.stringify(pallets) }));
  await page.route("**/api/admin/transport/tasks", r => r.fulfill({ contentType: "application/json", body: JSON.stringify({ task_id: 6002 }) }));
}

async function shot(page, name) {
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", name), fullPage: true });
}

function html() {
  return `<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>ТМС-2 Block I: Диспетчер рейсов</title>
  <style>
    body { margin: 0; font-family: Arial, sans-serif; color: #172033; background: #f4f7fb; }
    header { padding: 28px 36px; background: #113a5c; color: white; }
    main { max-width: 1180px; margin: 0 auto; padding: 28px 24px 48px; }
    section { background: white; border: 1px solid #d8e0ea; border-radius: 8px; padding: 22px; margin: 0 0 22px; }
    h1, h2, h3 { margin-top: 0; }
    h2 { color: #113a5c; }
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
    <h1>ТМС-2 Block I: Диспетчер и жизненный цикл рейса</h1>
    <p>Sprint 1-6. Учебная визуальная инструкция по результатам успешного functional/UI/load gate.</p>
  </header>
  <main>
    <section>
      <h2>Зачем этот блок</h2>
      <p>Block I заменяет ежедневную работу диспетчера из legacy WinForms: увидеть свободные СТ, отфильтровать и выделить их, создать рейс, проверить состав, отредактировать реквизиты, управлять порядком/типом погрузки и открыть паллетную детализацию.</p>
      <div class="grid">
        <div class="card"><b>Вход</b><br>СТ из сборки, адреса, паллеты, вес, объём, готовность, требования к ТС.</div>
        <div class="card"><b>Процесс</b><br>Выделение СТ, создание/редактирование рейса, назначение/снятие СТ, закрытие рейса.</div>
        <div class="card"><b>Результат</b><br>Рейс с составом, реквизитами, порядком объезда, типом погрузки и контролем готовности.</div>
      </div>
    </section>

    <section>
      <h2>Структура данных</h2>
      <table>
        <tr><th>Объект</th><th>Основные поля</th><th>Источник</th></tr>
        <tr><td>СТ</td><td><code>ST_NUMBER</code>, <code>ADDR</code>, <code>REGION</code>, <code>RAION</code>, <code>PALLETS_COUNT</code>, <code>WEIGHT_KG</code>, <code>VOLUME_M3</code>, <code>VERIFY_PERC</code>, <code>TRANSTASK_ID</code></td><td><code>RRL_SBORKA_PALLETS</code>, <code>RRL_SBORKA_PALLET_ROWS</code>, <code>RRL_ADDR</code></td></tr>
        <tr><td>Рейс</td><td><code>ID</code>, <code>TRANSTYPE</code>, <code>TRANSPORT</code>, <code>VODITEL_ID</code>, <code>DOCK</code>, <code>SHIPMENT_DATE</code>, <code>READY_PERC</code>, <code>PAY_ORDER_ID</code></td><td><code>RRL_TRANSPORT_TASK</code>, <code>RRL_TR_VEHICLE</code>, <code>RRL_TR_VODITEL</code></td></tr>
        <tr><td>Паллеты СТ</td><td><code>PALLET_UID</code>, <code>ZONE</code>, <code>LOAD_TYPE</code>, <code>ORD</code>, <code>ARTICUL</code>, <code>ORDER_WEIGHT</code>, <code>PACK_COUNT</code></td><td><code>RRL_SBORKA_PALLETS</code>, <code>RRL_SBORKA_PALLET_ROWS</code></td></tr>
      </table>
    </section>

    <section>
      <h2>Как работать</h2>
      <figure>
        <img src="screenshots/01_requests_table.png" alt="Таблица СТ" />
        <figcaption><b>1. Таблица заявок.</b> Диспетчер начинает с вкладки заявок: видит склад, паллеты, вес, объём, регион, адрес, номер СТ, дату, готовность сборки, район, тип ТС, признак гидроборта/стола, примечание и полнопалетную отборку.</figcaption>
      </figure>
      <figure>
        <img src="screenshots/02_selection_summary.png" alt="Выделение СТ" />
        <figcaption><b>2. Выделение СТ.</b> Чекбокс выбирает СТ; строка итогов показывает количество выбранных СТ, паллеты, массу и объём без дополнительного запроса к серверу.</figcaption>
      </figure>
      <figure>
        <img src="screenshots/03_create_trip_dialog.png" alt="Создание рейса" />
        <figcaption><b>3. Создание рейса.</b> Из выделения открывается диалог создания: тип ТС, машина, водитель, док и дата отгрузки. После создания выбранные СТ назначаются на рейс.</figcaption>
      </figure>
      <figure>
        <img src="screenshots/04_routes_detail.png" alt="Список и состав рейса" />
        <figcaption><b>4. Маршруты и состав.</b> Вкладка маршрутов показывает список рейсов, готовность, ТК/свой водитель, цену и статус. При выборе рейса ниже открывается состав СТ.</figcaption>
      </figure>
      <figure>
        <img src="screenshots/05_edit_trip.png" alt="Редактирование рейса" />
        <figcaption><b>5. Редактирование рейса.</b> В карточке рейса можно изменить машину, водителя, док, время, дату, тип ТС и примечание. Снятие СТ и закрытие рейса доступны из той же формы.</figcaption>
      </figure>
      <figure>
        <img src="screenshots/06_pallets_panel.png" alt="Паллеты заявки" />
        <figcaption><b>6. Паллеты заявки.</b> Кнопка паллет открывает детализацию по выбранной СТ: паллеты, зона, тип погрузки, порядок, артикулы, вес, упаковки и объём.</figcaption>
      </figure>
    </section>

    <section>
      <h2>Бизнес-процессы</h2>
      <ol>
        <li><b>Планирование дня:</b> выбрать дату, отфильтровать свободные СТ, проверить готовность и требования к машине.</li>
        <li><b>Формирование рейса:</b> выделить группу СТ, выбрать тип ТС/водителя/док, создать рейс и проверить, что СТ ушли в состав.</li>
        <li><b>Оперативное редактирование:</b> поправить реквизиты рейса, порядок объезда и тип погрузки, снять ошибочно назначенную СТ.</li>
        <li><b>Контроль перед отгрузкой:</b> проверить readiness, состав, паллеты, адреса и требования гидроборта/стола.</li>
        <li><b>Закрытие:</b> закрыть рейс как отгруженный; пустой рейс или рейс с бизнес-ошибкой не должен закрываться молча.</li>
      </ol>
    </section>

    <section>
      <h2>Результат проверки</h2>
      <p>Block I Sprint 1-6 прошёл gate: functional tests <code>78 passed</code>, UI smoke Sprint 1-6 passed, load NFR Sprint 4-6 passed, frontend build passed.</p>
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
  await page.getByText("ДЦСТ-П10001").waitFor({ timeout: 10000 });
  await shot(page, "01_requests_table.png");

  const firstRequestCheckbox = page.locator(".dispatch-grid tbody input[type='checkbox']").first();
  await firstRequestCheckbox.check();
  await firstRequestCheckbox.waitFor({ state: "attached", timeout: 5000 });
  await shot(page, "02_selection_summary.png");

  await page.getByRole("button", { name: /Создать/ }).first().click();
  await page.getByText(/Создать/i).first().waitFor({ timeout: 5000 });
  await shot(page, "03_create_trip_dialog.png");
  await page.keyboard.press("Escape").catch(() => {});

  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("#6001").waitFor({ timeout: 5000 });
  await page.getByText("#6001").click();
  await page.getByText("ДЦСТ-П10001").waitFor({ timeout: 5000 });
  await shot(page, "04_routes_detail.png");

  await page.getByRole("button", { name: "Заявки" }).click();
  const taskRow = page.locator(".dispatch-trips-table-wrap tbody tr", { hasText: "#6001" }).first();
  await taskRow.waitFor({ timeout: 5000 });
  await taskRow.click();
  await page.locator("b", { hasText: "Рейс #6001" }).waitFor({ timeout: 5000 });
  await page.getByRole("button", { name: "Редактировать" }).click();
  await page.locator(".dispatch-trip-mi").first().waitFor({ timeout: 5000 });
  await shot(page, "05_edit_trip.png");

  await page.locator(".dispatch-pallet-btn").first().click();
  await page.getByText("PAL-B1-001").waitFor({ timeout: 5000 });
  await shot(page, "06_pallets_panel.png");

  await browser.close();
  fs.writeFileSync(path.join(OUT_DIR, "index.html"), html(), "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
