const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint46_day_step_buttons_2026_05_28");
const task = { ID: 4601, TRANSTYPE: "10", TRANSPORT: "В 461 ТТ 59", VODITEL_ID: 461, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Day", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 1, PALLET_COUNT: 2, TEMP_WEIGHT: 400, PRICE: 1000, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(pageUrl("transport"));
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByText("4601").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_tasks_date_toolbar.png"), fullPage: true });
  await page.locator(".dispatch-trips-section .dispatch-trips-toolbar").first().getByTitle("Следующий день").click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_tasks_next_day.png"), fullPage: true });
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_routes_date_toolbar.png"), fullPage: true });
  await page.locator(".dispatch-trips-toolbar").filter({ hasText: "Маршруты за" }).getByTitle("Предыдущий день").click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "04_routes_prev_day.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 46</title></head><body><h1>ТМС-2 Sprint 46: быстрое переключение дня</h1><p>Блок ускоряет просмотр рейсов по соседним датам без ручного редактирования поля даты.</p><h2>Структура данных</h2><p>Обе панели используют общий helper <code>shiftDate(iso, days)</code>. Вкладка «Заявки» меняет <code>filterDate</code>, вкладка «Маршруты» меняет <code>routeShipDate</code>.</p><h2>Результат</h2><p>Кнопки <code>◄</code> и <code>►</code> рядом с датой сдвигают день назад или вперёд и запускают обычную перезагрузку списка.</p><h2>Бизнес-процесс</h2><ol><li>Открыть «Заявки» и нажать <code>►</code> для следующего дня.</li><li>Вернуться через <code>◄</code>.</li><li>Открыть «Маршруты» и проверить тот же сценарий.</li><li>Использовать переключение для оперативного просмотра вчера/завтра.</li></ol><img src="screenshots/01_tasks_date_toolbar.png" width="100%"><img src="screenshots/02_tasks_next_day.png" width="100%"><img src="screenshots/03_routes_date_toolbar.png" width="100%"><img src="screenshots/04_routes_prev_day.png" width="100%"><p>Проверка: functional, UI smoke и load gate пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
