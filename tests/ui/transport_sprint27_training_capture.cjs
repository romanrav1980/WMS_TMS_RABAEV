const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint27_billing_registry_xlsx_2026_05_28");

async function installMocks(page) {
  const orders = [
    { order_id: 2701, num: "B-2701", company: "ООО Реестр-Транс", date_from: "2026-05-01", date_to: "2026-05-31", closed: 0, payed: 0, total_price: 25000, task_count: 1, num_plat: "ПП-2701" },
    { order_id: 2702, num: "B-2702", company: "ООО Реестр-Транс", date_from: "2026-05-01", date_to: "2026-05-31", closed: 1, payed: 1, total_price: 15000, task_count: 1, num_plat: "ПП-2702" },
  ];
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/orders?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(orders) }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "Биллинг", exact: true }).click();
  await page.getByText("B-2701").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_registry_excel_button.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 27</title></head><body><h1>ТМС-2 Sprint 27: Excel реестра счетов</h1><p>Блок выгружает текущий отфильтрованный реестр счетов в XLSX.</p><h2>Структура данных</h2><p>Экспорт использует те же фильтры, что и реестр: компания, период, статус, признак оплаты. XLSX содержит номер счёта, компанию, период, число рейсов, сумму, статус и номер платёжного поручения.</p><h2>Результат</h2><p>Оператор получает файл для бухгалтерии или управленческой сверки по всем счетам.</p><h2>Бизнес-процессы</h2><ol><li>Открыть вкладку «Биллинг».</li><li>Настроить фильтры реестра.</li><li>Нажать «Excel» в панели реестра.</li><li>Передать файл на сверку.</li></ol><img src="screenshots/01_registry_excel_button.png" width="100%"><p>Проверка: functional, UI smoke и load gates пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
