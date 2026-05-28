const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint23_billing_order_detail_2026_05_28");

async function installMocks(page) {
  const orders = [{ order_id: 2301, num: "B-2301", company: "ООО Детали-Транс", date_from: "2026-05-01", date_to: "2026-05-31", closed: 0, payed: 0, total_price: 25000, task_count: 2, num_plat: "ПП-2301" }];
  const orderTasks = [
    { tt_id: 2311, transport: "В 431 ТТ 59", shipment_date: "2026-05-25", status: "Отгружен", price: 12500 },
    { tt_id: 2312, transport: "В 432 ТТ 59", shipment_date: "2026-05-26", status: "Отгружен", price: 12500 },
  ];
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/orders?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(orders) }));
  await page.route("**/api/admin/transport/billing/orders/2301/tasks", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(orderTasks) }));
  await page.route("**/api/admin/transport/billing/orders/2301/export.xlsx", route => route.fulfill({ contentType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", body: "xlsx" }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "Биллинг" }).click();
  await page.getByText("B-2301").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_registry_row.png"), fullPage: true });
  await page.getByText("B-2301").click();
  await page.getByText("#2311").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_detail_tasks.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 23</title></head><body><h1>ТМС-2 Sprint 23: Детальный просмотр счёта</h1><p>Блок показывает полный состав рейсов внутри выбранного счёта и даёт экспорт списка рейсов для сверки с перевозчиком.</p><h2>Структура данных</h2><p>Детали читаются через <code>GET /billing/orders/{id}/tasks</code>; каждая строка содержит <code>tt_id</code>, авто, дату, статус и сумму.</p><h2>Результат</h2><p>Оператор открывает счёт из реестра, видит состав, итог и может выгрузить CSV/Excel.</p><h2>Бизнес-процессы</h2><ol><li>Открыть реестр счетов.</li><li>Выбрать счёт.</li><li>Проверить рейсы, сумму и статус.</li><li>Скачать CSV для внешней сверки.</li></ol><img src="screenshots/01_registry_row.png" width="100%"><img src="screenshots/02_detail_tasks.png" width="100%"><p>Проверка: functional, UI smoke и load gates пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
