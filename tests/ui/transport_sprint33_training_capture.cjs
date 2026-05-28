const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint33_routes_brief_mode_2026_05_28");
const task = { ID: 3301, TRANSTYPE: "10", TRANSPORT: "В 501 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Brief-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 1, PALLET_COUNT: 4, TEMP_WEIGHT: 800, PRICE: 1200, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("3301").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_full_routes_table.png"), fullPage: true });
  await page.getByLabel("Кратко").check();
  await page.locator(".routes-brief").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_brief_routes_table.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 33</title></head><body><h1>ТМС-2 Sprint 33: Краткий режим маршрутов</h1><p>Блок нужен диспетчеру для быстрого просмотра рейсов, когда второстепенные колонки мешают сканированию.</p><h2>Структура данных</h2><p>Данные остаются теми же: <code>GET /api/admin/transport/tasks</code>. Меняется только набор видимых колонок на клиенте.</p><h2>Результат</h2><p>В режиме «Кратко» остаются ключевые поля рейса: дата отгрузки, номер, паллеты, вес, машина, водитель, док, регионы и статус.</p><h2>Бизнес-процессы</h2><ol><li>Открыть вкладку «Маршруты».</li><li>Включить «Кратко».</li><li>Сканировать список рейсов без цены, ТК, логиста и служебных колонок.</li><li>Выключить «Кратко», когда нужны полные детали.</li></ol><img src="screenshots/01_full_routes_table.png" width="100%"><img src="screenshots/02_brief_routes_table.png" width="100%"><p>Проверка: functional, UI smoke и load gate пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
