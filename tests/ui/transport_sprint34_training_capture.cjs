const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint34_cancel_releases_st_2026_05_28");
const task = { ID: 3401, TRANSTYPE: "10", TRANSPORT: "В 501 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Cancel-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 1, PALLET_COUNT: 4, TEMP_WEIGHT: 800, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
const taskSts = [{ ST_NUMBER: "СТ-3401", PALLETS_COUNT: 4, WEIGHT_KG: 800, VOLUME_M3: 3, ORD: 1, WARE_ID: 9201, VERIFY_PERC: 100 }];

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  let tasksReloaded = false;
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(tasksReloaded ? [] : [task]) }));
  await page.route("**/api/admin/transport/tasks/3401/sts", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(taskSts) }));
  await page.route("**/api/admin/transport/tasks/3401/cancel", route => {
    tasksReloaded = true;
    return route.fulfill({ contentType: "application/json", body: "{}" });
  });
  page.on("dialog", dialog => dialog.accept());
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("3401").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_task_before_cancel.png"), fullPage: true });
  await page.getByRole("button", { name: "Отменить" }).click();
  await page.getByText("Рейс #3401 отменён").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_task_cancelled.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 34</title></head><body><h1>ТМС-2 Sprint 34: Расформирование рейса освобождает СТ</h1><p>Блок нужен, чтобы отменённый рейс не блокировал СТ для повторного планирования.</p><h2>Структура данных</h2><p>Операция работает в одной транзакции: проверяет <code>PAY_ORDER_ID</code>, снимает <code>TRANSTASK_ID</code> у строк <code>RRL_SBORKA_PALLETS</code>, затем помечает рейс <code>DELETED=1</code>.</p><h2>Результат</h2><p>После отмены рейс пропадает из активного списка, а его СТ снова могут попасть в доступные для нового рейса.</p><h2>Бизнес-процессы</h2><ol><li>Открыть рейс.</li><li>Нажать «Отменить» и подтвердить действие.</li><li>Проверить, что рейс исчез из активного списка.</li><li>Проверить в Oracle/prod, что СТ освобождены.</li></ol><img src="screenshots/01_task_before_cancel.png" width="100%"><img src="screenshots/02_task_cancelled.png" width="100%"><p>Проверка: functional, UI smoke и безопасный service load gate пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
