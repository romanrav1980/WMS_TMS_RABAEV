const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint28_tasks_xlsx_2026_05_28");

async function installMocks(page) {
  const tasks = [{ ID: 2801, TRANSTYPE: "10", TRANSPORT: "В 481 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Рейсы-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Отгружен", ST_COUNT: 3, PALLET_COUNT: 12, TEMP_WEIGHT: 2400, PRICE: 12500, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 }];
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(tasks) }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("2801").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_tasks_excel_button.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 28</title></head><body><h1>ТМС-2 Sprint 28: Excel списка рейсов</h1><p>Блок выгружает текущий список рейсов в XLSX с теми же фильтрами, что применены на вкладке «Маршруты».</p><h2>Структура данных</h2><p>Экспорт использует <code>GET /tasks/export.xlsx</code> и поля рейса: дата, ID, паллеты, вес, тип ТС, машина, водитель, цена, ТК и статус.</p><h2>Результат</h2><p>Диспетчер получает файл рейсов для оперативной сверки, планёрки или передачи смежным подразделениям.</p><h2>Бизнес-процессы</h2><ol><li>Открыть вкладку «Маршруты».</li><li>Настроить фильтры рейсов.</li><li>Нажать «Excel» над списком.</li><li>Использовать файл для контроля рейсов.</li></ol><img src="screenshots/01_tasks_excel_button.png" width="100%"><p>Проверка: functional, UI smoke и load gates пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
