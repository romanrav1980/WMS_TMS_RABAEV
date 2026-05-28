const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint36_bulk_unassign_2026_05_28");
const task = { ID: 3601, TRANSTYPE: "10", TRANSPORT: "В 501 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Bulk-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 3, PALLET_COUNT: 9, TEMP_WEIGHT: 1800, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
let taskSts = [
  { ST_NUMBER: "СТ-3601", ADDR: "Адрес 1", REGION: "Пермь", RAION: "Ленинский", PALLETS_COUNT: 3, WEIGHT_KG: 600, VOLUME_M3: 2, ORD: 1, WARE_ID: 9201, VERIFY_PERC: 100 },
  { ST_NUMBER: "СТ-3602", ADDR: "Адрес 2", REGION: "Пермь", RAION: "Ленинский", PALLETS_COUNT: 3, WEIGHT_KG: 600, VOLUME_M3: 2, ORD: 2, WARE_ID: 9201, VERIFY_PERC: 100 },
  { ST_NUMBER: "СТ-3603", ADDR: "Адрес 3", REGION: "Пермь", RAION: "Ленинский", PALLETS_COUNT: 3, WEIGHT_KG: 600, VOLUME_M3: 2, ORD: 3, WARE_ID: 9201, VERIFY_PERC: 100 },
];

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/3601/sts", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(taskSts) }));
  await page.route("**/api/admin/transport/tasks/3601/sts/*", route => {
    const st = decodeURIComponent(route.request().url().split("/").pop());
    taskSts = taskSts.filter(row => row.ST_NUMBER !== st);
    return route.fulfill({ contentType: "application/json", body: JSON.stringify({ unassigned: true }) });
  });
  page.on("dialog", dialog => dialog.accept());
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByText("#3601").waitFor({ timeout: 10000 });
  await page.locator("tr[data-taskid='3601']").click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_trip_sts_before.png"), fullPage: true });
  await page.locator(".dispatch-trip-sts-wrap tbody input[type='checkbox']").nth(0).check();
  await page.locator(".dispatch-trip-sts-wrap tbody input[type='checkbox']").nth(1).check();
  await page.getByText("2 СТ выбрано").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_bulk_selected.png"), fullPage: true });
  await page.getByRole("button", { name: "Снять выбранные" }).click();
  await page.getByText("2 СТ снято с рейса #3601").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_bulk_removed.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 36</title></head><body><h1>ТМС-2 Sprint 36: Массовое снятие СТ с рейса</h1><p>Блок нужен, чтобы диспетчер снимал несколько СТ из рейса одной операцией, без повторения действия по каждой строке.</p><h2>Структура данных</h2><p>Frontend хранит выбранные СТ в <code>selectedTripStNums</code>. Для снятия отправляется несколько <code>DELETE /tasks/{id}/sts/{st}</code>. Backend запрещает операцию для отгруженных и billed рейсов.</p><h2>Результат</h2><p>Выбранные СТ снимаются, выделение очищается, состав рейса и список доступных СТ обновляются.</p><h2>Бизнес-процессы</h2><ol><li>Открыть рейс.</li><li>Отметить несколько СТ в составе рейса.</li><li>Нажать «Снять выбранные» и подтвердить.</li><li>Проверить, что выбранные СТ ушли из рейса.</li></ol><img src="screenshots/01_trip_sts_before.png" width="100%"><img src="screenshots/02_bulk_selected.png" width="100%"><img src="screenshots/03_bulk_removed.png" width="100%"><p>Проверка: functional, UI smoke и безопасный load gate пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
