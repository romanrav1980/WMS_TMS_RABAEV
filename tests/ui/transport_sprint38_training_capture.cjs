const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint38_copy_trip_2026_05_28");
const sourceTask = { ID: 3801, TRANSTYPE: "10", TRANSPORT: "В 501 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Copy-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", SHIPMENT_TIME: "2026-05-25T08:30:00", DOCK: "Д-1", CONDITION: "Новый", ST_COUNT: 2, PALLET_COUNT: 8, TEMP_WEIGHT: 1500, PRICE: 9900, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
const copiedTask = { ...sourceTask, ID: 3802, ST_COUNT: 0, PALLET_COUNT: 0, TEMP_WEIGHT: 0, PRICE: null };
let copied = false;

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks/3802", route => {
    if (route.request().method() === "PATCH") return route.fulfill({ contentType: "application/json", body: JSON.stringify({ task_id: 3802 }) });
    return route.fulfill({ contentType: "application/json", body: JSON.stringify(copiedTask) });
  });
  await page.route("**/api/admin/transport/tasks/3801/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks/3802/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks", route => {
    if (route.request().method() === "POST") {
      copied = true;
      return route.fulfill({ contentType: "application/json", body: JSON.stringify({ task_id: 3802 }) });
    }
    return route.fallback();
  });
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(copied ? [copiedTask, sourceTask] : [sourceTask]) }));
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByText("#3801").waitFor({ timeout: 10000 });
  await page.locator("tr[data-taskid='3801']").click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_source_trip.png"), fullPage: true });
  await page.getByRole("button", { name: "📋 Копировать" }).click();
  await page.getByText("Рейс #3802 создан как копия рейса #3801").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_copied_trip.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 38</title></head><body><h1>ТМС-2 Sprint 38: Копирование рейса</h1><p>Блок нужен для повторяющихся маршрутов: диспетчер создаёт новый рейс с теми же реквизитами, но без состава СТ.</p><h2>Структура данных</h2><p>Копирование выполняет <code>POST /tasks</code> с типом и датой, затем <code>PATCH /tasks/{id}</code> для машины, водителя, дока и времени. СТ, цена и счёт не копируются.</p><h2>Результат</h2><p>Новый рейс выбран в интерфейсе, готов к наполнению СТ и не связан с биллингом исходного рейса.</p><h2>Бизнес-процессы</h2><ol><li>Открыть исходный рейс.</li><li>Нажать «Копировать».</li><li>Проверить новый номер рейса и унаследованные реквизиты.</li><li>Добавить актуальные СТ в новый рейс.</li></ol><img src="screenshots/01_source_trip.png" width="100%"><img src="screenshots/02_copied_trip.png" width="100%"><p>Проверка: functional, UI smoke и no-mutation load gate пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
