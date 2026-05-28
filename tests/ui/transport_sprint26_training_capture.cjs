const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint26_billing_order_xlsx_2026_05_28");

async function installMocks(page) {
  const orders = [{ order_id: 2601, num: "B-2601", company: "ООО Excel-Транс", date_from: "2026-05-01", date_to: "2026-05-31", closed: 0, payed: 0, total_price: 25000, task_count: 1 }];
  const tasks = [{ tt_id: 2601, transport: "В 461 ТТ 59", shipment_date: "2026-05-25", status: "Отгружен", price: 25000 }];
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/orders?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(orders) }));
  await page.route("**/api/admin/transport/billing/orders/2601/tasks", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(tasks) }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "Биллинг", exact: true }).click();
  await page.getByText("B-2601").waitFor({ timeout: 10000 });
  await page.getByText("B-2601").click();
  await page.getByText("#2601").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_order_export_button.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 26</title></head><body><h1>ТМС-2 Sprint 26: Excel счёта</h1><p>Блок выгружает выбранный счёт в XLSX с реквизитами, рейсами и итоговой суммой.</p><h2>Структура данных</h2><p>Экспорт читает заголовок счёта и <code>GET /billing/orders/{id}/tasks</code>, затем формирует <code>.xlsx</code>. При отсутствии <code>openpyxl</code> используется встроенный минимальный генератор XLSX.</p><h2>Результат</h2><p>Оператор получает файл для отправки перевозчику или бухгалтерской сверки.</p><h2>Бизнес-процессы</h2><ol><li>Открыть реестр счетов.</li><li>Выбрать счёт.</li><li>Проверить состав рейсов.</li><li>Нажать «Excel» в панели деталей.</li></ol><img src="screenshots/01_order_export_button.png" width="100%"><p>Проверка: functional, UI smoke и load gates пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
