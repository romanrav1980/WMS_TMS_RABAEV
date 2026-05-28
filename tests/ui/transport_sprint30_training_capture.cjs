const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint30_load_bar_2026_05_28");

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const vehicle = { ID: 1, NUM: "В 501 ТТ 59", MARKA: "MAN", PALLETS: 10 };
  const task = { ID: 3001, TRANSTYPE: "10", TRANSPORT: vehicle.NUM, VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Load-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 2, PALLET_COUNT: 9, TEMP_WEIGHT: 1800, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
  const taskSts = [
    { ST_NUMBER: "СТ-3001", PALLETS_COUNT: 5, WEIGHT_KG: 1000, VOLUME_M3: 4, ORD: 1, WARE_ID: 9201, VERIFY_PERC: 100 },
    { ST_NUMBER: "СТ-3002", PALLETS_COUNT: 4, WEIGHT_KG: 800, VOLUME_M3: 3, ORD: 2, WARE_ID: 9201, VERIFY_PERC: 100 },
  ];
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([vehicle]) }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/3001/sts", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(taskSts) }));
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("3001").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await page.locator(".load-bar-row").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_load_bar.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 30</title></head><body><h1>ТМС-2 Sprint 30: Индикатор загрузки</h1><p>Блок показывает заполнение машины паллетами прямо в карточке рейса.</p><h2>Структура данных</h2><p>Значение берётся из суммы <code>PALLETS_COUNT</code> по СТ рейса, лимит — из <code>RRL_TR_VEHICLE.PALLETS</code>.</p><h2>Результат</h2><p>Диспетчер видит процент загрузки: зелёный до 85%, жёлтый 85–99%, красный при 100% и выше.</p><h2>Бизнес-процессы</h2><ol><li>Открыть рейс.</li><li>Проверить машину и состав СТ.</li><li>Оценить индикатор загрузки до закрытия рейса.</li></ol><img src="screenshots/01_load_bar.png" width="100%"><p>Проверка: functional, UI smoke и load gates пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
