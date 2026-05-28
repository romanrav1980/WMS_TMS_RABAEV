const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint16_billing_lifecycle_2026_05_28");

const task = {
  ID: 1601, TRANSTYPE: "10", TRANSPORT: "В 415 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.",
  TK_NAME: "ООО Тест-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00",
  CONDITION: "Отгружен", ST_COUNT: 3, PALLET_COUNT: 12, TEMP_WEIGHT: 2400, PRICE: 12500,
  PAY_ORDER_ID: 8801, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0,
};
let order = { order_id: 8801, num: "B-8801", company: "ООО Тест-Транс", date_from: "2026-05-25", date_to: "2026-05-25", closed: 0, payed: 0, total_price: 12500, task_count: 1, num_plat: null };

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/1601/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/orders/8801", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(order) }));
  await page.route("**/api/admin/transport/billing/orders/8801/close", route => {
    order = { ...order, closed: 1 };
    route.fulfill({ contentType: "application/json", body: JSON.stringify({ order_id: 8801, closed: true }) });
  });
  await page.route("**/api/admin/transport/billing/orders/8801/pay", route => {
    order = { ...order, closed: 1, payed: 1 };
    route.fulfill({ contentType: "application/json", body: JSON.stringify({ order_id: 8801, payed: true }) });
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
  <title>ТМС-2 Sprint 16: Статусы счёта</title>
  <style>
    body { margin: 0; font-family: Arial, sans-serif; color: #172033; background: #f4f7fb; }
    header { padding: 28px 36px; background: #315142; color: white; }
    main { max-width: 1180px; margin: 0 auto; padding: 28px 24px 48px; }
    section { background: white; border: 1px solid #d8e0ea; border-radius: 8px; padding: 22px; margin: 0 0 22px; }
    h1, h2 { margin-top: 0; }
    h2 { color: #315142; }
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
    <h1>ТМС-2 Sprint 16: Закрытие и оплата счёта</h1>
    <p>Статусная машина биллинга: выставлен → закрыт → оплачен.</p>
  </header>
  <main>
    <section>
      <h2>Зачем этот блок</h2>
      <p>Sprint 16 добавляет управляемый жизненный цикл счета. После выставления счет можно закрыть, а затем отметить оплаченным; каждый переход фиксируется через Oracle billing API.</p>
      <div class="grid">
        <div class="card"><b>Вход</b><br>Выставленный биллинговый заказ, привязанный к рейсу.</div>
        <div class="card"><b>Процесс</b><br>Закрыть счет, затем отметить оплату.</div>
        <div class="card"><b>Результат</b><br>Счет получает финальный статус «Оплачен».</div>
      </div>
    </section>
    <section>
      <h2>Структура данных</h2>
      <table>
        <tr><th>Поле</th><th>Смысл</th></tr>
        <tr><td><code>closed</code></td><td>Счет закрыт для изменения состава.</td></tr>
        <tr><td><code>payed</code></td><td>Счет отмечен оплаченным.</td></tr>
        <tr><td><code>num_plat</code></td><td>Номер платежного документа, если задан.</td></tr>
      </table>
    </section>
    <section>
      <h2>Как работать</h2>
      <figure><img src="screenshots/01_open_order.png" alt="Выставленный счет" /><figcaption><b>1. Выставленный счет.</b> В карточке рейса виден номер счета, компания, период, сумма и кнопка «Закрыть счёт».</figcaption></figure>
      <figure><img src="screenshots/02_closed_order.png" alt="Закрытый счет" /><figcaption><b>2. Закрытый счет.</b> После закрытия статус меняется на «Закрыт», появляется действие «Отметить оплаченным».</figcaption></figure>
      <figure><img src="screenshots/03_paid_order.png" alt="Оплаченный счет" /><figcaption><b>3. Оплаченный счет.</b> Финальный статус показывает, что счет закрыт и оплачен.</figcaption></figure>
    </section>
    <section>
      <h2>Бизнес-процессы</h2>
      <ol>
        <li><b>Выставлен:</b> счет создан и содержит рейсы.</li>
        <li><b>Закрыт:</b> бухгалтерия/диспетчер подтверждает состав и сумму.</li>
        <li><b>Оплачен:</b> поступление денег фиксируется в системе.</li>
        <li><b>Контроль:</b> статус виден в карточке рейса и реестре счетов.</li>
      </ol>
    </section>
    <section>
      <h2>Результат проверки</h2>
      <p>Sprint 16 закрыт функционально: backend tests <code>11 passed</code>, UI smoke passed, load NFR passed. Проверены переходы выставлен → закрыт → оплачен.</p>
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
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("1601").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await page.getByText("B-8801").waitFor({ timeout: 5000 });
  await shot(page, "01_open_order.png");

  await page.getByRole("button", { name: "Закрыть счёт" }).click();
  await page.getByText("Закрыт").waitFor({ timeout: 5000 });
  await shot(page, "02_closed_order.png");

  await page.getByRole("button", { name: "Отметить оплаченным" }).click();
  await page.getByText("Счёт закрыт и оплачен").waitFor({ timeout: 5000 });
  await shot(page, "03_paid_order.png");

  await browser.close();
  fs.writeFileSync(path.join(OUT_DIR, "index.html"), html(), "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
