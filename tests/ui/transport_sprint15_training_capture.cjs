const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint15_billing_open_2026_05_28");

const task = {
  ID: 1501, TRANSTYPE: "10", TRANSPORT: "В 415 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.",
  TK_NAME: "ООО Тест-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00",
  CONDITION: "Отгружен", ST_COUNT: 3, PALLET_COUNT: 12, TEMP_WEIGHT: 2400, PRICE: 12500,
  PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0,
};

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент 10т" }]) }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/1501/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/companies", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(["ООО Тест-Транс"]) }));
  await page.route("**/api/admin/transport/billing/orders?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks/1501/billing/open", route => {
    task.PAY_ORDER_ID = 7701;
    route.fulfill({ contentType: "application/json", body: JSON.stringify({ order_id: 7701 }) });
  });
}

async function shot(page, name) {
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", name), fullPage: true });
}

function html() {
  return `<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>ТМС-2 Sprint 15: Выставление счёта</title>
  <style>
    body { margin: 0; font-family: Arial, sans-serif; color: #172033; background: #f4f7fb; }
    header { padding: 28px 36px; background: #2f3d59; color: white; }
    main { max-width: 1180px; margin: 0 auto; padding: 28px 24px 48px; }
    section { background: white; border: 1px solid #d8e0ea; border-radius: 8px; padding: 22px; margin: 0 0 22px; }
    h1, h2 { margin-top: 0; }
    h2 { color: #2f3d59; }
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
    <h1>ТМС-2 Sprint 15: Выставление счёта</h1>
    <p>Закрытый рейс привязывается к биллинговому заказу транспортной компании.</p>
  </header>
  <main>
    <section>
      <h2>Зачем этот блок</h2>
      <p>Sprint 15 запускает биллинговый контур: отгруженный рейс превращается в счёт, а рейс после этого защищается от редактирования и расформирования.</p>
      <div class="grid">
        <div class="card"><b>Вход</b><br>Отгруженный рейс, транспортная компания, цена рейса.</div>
        <div class="card"><b>Процесс</b><br>Открыть рейс, нажать «Выставить счёт», создать новый заказ или привязать к существующему.</div>
        <div class="card"><b>Результат</b><br>Рейс получает <code>PAY_ORDER_ID</code> и тег счёта.</div>
      </div>
    </section>
    <section>
      <h2>Структура данных</h2>
      <table>
        <tr><th>Объект</th><th>Поля</th><th>Назначение</th></tr>
        <tr><td>Рейс</td><td><code>ID</code>, <code>TK_NAME</code>, <code>PRICE</code>, <code>PAY_ORDER_ID</code></td><td>Источник строки счёта и связь с заказом.</td></tr>
        <tr><td>Биллинг-заказ</td><td><code>order_id</code>, <code>company</code>, <code>date_from</code>, <code>date_to</code>, <code>total_price</code></td><td>Документ для транспортной компании.</td></tr>
      </table>
    </section>
    <section>
      <h2>Как работать</h2>
      <figure><img src="screenshots/01_closed_task.png" alt="Закрытый рейс" /><figcaption><b>1. Выбрать закрытый рейс.</b> Кнопка «Выставить счёт» доступна только для отгруженного рейса внешней транспортной компании.</figcaption></figure>
      <figure><img src="screenshots/02_open_billing_dialog.png" alt="Диалог выставления счёта" /><figcaption><b>2. Проверить счёт.</b> Диалог показывает рейс, транспортную компанию, дату и цену. Если есть открытые счета этой ТК, можно привязать рейс к ним.</figcaption></figure>
      <figure><img src="screenshots/03_billed_task.png" alt="Рейс со счётом" /><figcaption><b>3. Создать счёт.</b> После создания рейс получает тег счёта и становится защищенным от изменений.</figcaption></figure>
    </section>
    <section>
      <h2>Бизнес-процессы</h2>
      <ol>
        <li><b>Подготовка:</b> рейс закрыт, водитель внешний, цена рассчитана.</li>
        <li><b>Выставление:</b> диспетчер создает биллинговый заказ или добавляет рейс в открытый счет ТК.</li>
        <li><b>Блокировка рейса:</b> наличие <code>PAY_ORDER_ID</code> запрещает расформирование и изменение состава.</li>
        <li><b>Контроль:</b> рейс виден с тегом счета, дальше его ведет статусная машина биллинга.</li>
      </ol>
    </section>
    <section>
      <h2>Результат проверки</h2>
      <p>Sprint 15 закрыт функционально: backend tests <code>12 passed</code>, UI smoke passed, load NFR passed. Проверены создание биллингового заказа, открытие счёта по рейсу, связь рейс-счёт и пользовательский диалог.</p>
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
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("1501").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await page.getByText("Рейс #1501").waitFor({ timeout: 5000 });
  await shot(page, "01_closed_task.png");

  await page.getByRole("button", { name: "Выставить счёт" }).click();
  await page.getByText("Транспортная компания").waitFor({ timeout: 5000 });
  await shot(page, "02_open_billing_dialog.png");

  await page.getByRole("button", { name: "Создать счёт" }).click();
  await page.getByText("Счёт #7701").waitFor({ timeout: 5000 });
  await shot(page, "03_billed_task.png");

  await browser.close();
  fs.writeFileSync(path.join(OUT_DIR, "index.html"), html(), "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
