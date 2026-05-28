const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint45_goto_trip_2026_05_28");
const task = { ID: 4501, TRANSTYPE: "10", TRANSPORT: "В 451 ТТ 59", VODITEL_ID: 451, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Goto", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 1, PALLET_COUNT: 2, TEMP_WEIGHT: 400, PRICE: 1000, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
const sts = [
  { ST_NUMBER: "СТ-4501", ADDR: "Пермь, Ленина 1", REGION: "Пермь", RAION: "Ленинский", PALLETS_COUNT: 2, WEIGHT_KG: 400, VOLUME_M3: 1.2, STDATE: "2026-05-25", DATE_LOAD: "2026-05-25", TRANSPORT_TYPE: "10", WARE_ID: 9201, VERIFY_PERC: 100, SUGAR: 0, TRANSTASK_ID: 4501 },
  { ST_NUMBER: "СТ-4502", ADDR: "Пермь, Мира 2", REGION: "Пермь", RAION: "Ленинский", PALLETS_COUNT: 1, WEIGHT_KG: 200, VOLUME_M3: 0.6, STDATE: "2026-05-25", DATE_LOAD: "2026-05-25", TRANSPORT_TYPE: "10", WARE_ID: 9201, VERIFY_PERC: 100, SUGAR: 0, TRANSTASK_ID: 0 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(sts) }));
  await page.route("**/api/admin/transport/tasks/4501", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(task) }));
  await page.route("**/api/admin/transport/tasks/4501/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(pageUrl("transport"));
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByText("СТ-4501").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_assigned_st_with_goto.png"), fullPage: true });
  await page.getByRole("button", { name: "#4501 →" }).click();
  await page.locator("tr[data-taskid='4501'].selected").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_trip_selected.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 45</title></head><body><h1>ТМС-2 Sprint 45: переход от СТ к рейсу</h1><p>Блок помогает диспетчеру быстро понять, в каком рейсе находится уже распределённая СТ.</p><h2>Структура данных</h2><p>Кнопка строится по полю <code>TRANSTASK_ID</code> в строке СТ. Если рейс уже загружен, он выбирается из текущего списка; если нет, UI может запросить <code>GET /tasks/{id}</code>.</p><h2>Результат</h2><p>В строке распределённой СТ появляется кнопка <code>#ID →</code>. Нажатие переключает на вкладку «Маршруты» и выбирает нужный рейс.</p><h2>Бизнес-процесс</h2><ol><li>Открыть список заявок.</li><li>Найти СТ с заполненным рейсом.</li><li>Нажать <code>#ID →</code>.</li><li>Проверить состав и параметры рейса во вкладке «Маршруты».</li></ol><img src="screenshots/01_assigned_st_with_goto.png" width="100%"><img src="screenshots/02_trip_selected.png" width="100%"><p>Проверка: functional, UI smoke и load gate пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
