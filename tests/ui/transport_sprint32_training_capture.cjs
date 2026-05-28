const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint32_overload_warning_2026_05_28");
const vehicle = { ID: 1, NUM: "В 501 ТТ 59", MARKA: "MAN", PALLETS: 10 };
const task = { ID: 3201, TRANSTYPE: "10", TRANSPORT: vehicle.NUM, VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Overload-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 2, PALLET_COUNT: 12, TEMP_WEIGHT: 2400, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
const taskSts = [
  { ST_NUMBER: "СТ-3201", PALLETS_COUNT: 6, WEIGHT_KG: 1200, VOLUME_M3: 5, ORD: 1, WARE_ID: 9201, VERIFY_PERC: 100 },
  { ST_NUMBER: "СТ-3202", PALLETS_COUNT: 6, WEIGHT_KG: 1200, VOLUME_M3: 5, ORD: 2, WARE_ID: 9201, VERIFY_PERC: 100 },
];

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([vehicle]) }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/3201/sts", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(taskSts) }));
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("3201").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await page.locator(".dispatch-overload-warn").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_overload_warning.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 32</title></head><body><h1>ТМС-2 Sprint 32: Предупреждение о перегрузе</h1><p>Блок нужен, чтобы диспетчер не закрывал рейс с количеством паллет выше нормы машины.</p><h2>Структура данных</h2><p>Фактическая загрузка считается по <code>PALLETS_COUNT</code> в составе рейса. Норма берётся из <code>RRL_TR_VEHICLE.PALLETS</code> выбранной машины.</p><h2>Результат</h2><p>Когда паллет больше нормы, рядом с индикатором загрузки появляется красное предупреждение с фактом, лимитом и номером машины.</p><h2>Бизнес-процессы</h2><ol><li>Открыть рейс.</li><li>Проверить состав СТ и машину.</li><li>Если появился перегруз, заменить машину или изменить состав рейса до отгрузки.</li></ol><img src="screenshots/01_overload_warning.png" width="100%"><p>Проверка: functional и UI smoke пройдены; live load gate pending до очистки порта 8088.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
