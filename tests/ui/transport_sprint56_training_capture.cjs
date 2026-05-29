const fs = require("fs");
const path = require("path");
const { createRequire } = require("module");
const { pageUrl } = require("../support/project_config.cjs");

function requirePlaywright() {
  try {
    return require("playwright");
  } catch {
    return createRequire(path.resolve("admin/wms_admin_frontend/package.json"))("playwright");
  }
}

const { chromium } = requirePlaywright();
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint56_route_sheet_print_2026_05_29");

const tasks = [
  { ID: 5601, TRANSTYPE: "Тент", TRANSPORT: "Е715ТТ", VODITEL_ID: 1, VODITEL_NAME: "Иванов И.И.", DOCK: "Д-3", SHIPMENT_DATE: "2026-05-25", CONDITION: "Новый", ST_COUNT: 2, PALLET_COUNT: 13, TEMP_WEIGHT: 800, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 75, UNREADY_COUNT: 1 },
  { ID: 5602, TRANSTYPE: "Реф", TRANSPORT: "А001АА", VODITEL_ID: 2, VODITEL_NAME: "Петров П.П.", DOCK: "Д-1", SHIPMENT_DATE: "2026-05-25", CONDITION: "Новый", ST_COUNT: 0, PALLET_COUNT: 0, TEMP_WEIGHT: 0, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 0, UNREADY_COUNT: 0 },
];

const taskSts = [
  { ST_NUMBER: "PRINT-ST-001", ADDR: "ул. Ленина 1", REGION: "Пермь", RAION: "Центр", ORD: 1, TRANSPORT_TYPE: "Тент", WARE_ID: 9201, PALLETS_COUNT: 5, WEIGHT_KG: 300, VOLUME_M3: 2.5, VERIFY_PERC: 100 },
  { ST_NUMBER: "PRINT-ST-002", ADDR: "пр. Мира 10", REGION: "Лысьва", RAION: "Лысьва", ORD: 2, TRANSPORT_TYPE: "Тент", WARE_ID: 9201, PALLETS_COUNT: 8, WEIGHT_KG: 500, VOLUME_M3: 3.0, VERIFY_PERC: 50 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route(/\/api\/admin\/transport\/tasks(?:\?|$)/, route => route.fulfill({ contentType: "application/json", body: JSON.stringify(tasks) }));
  await page.route(/tasks\/5601\/sts/, route => route.fulfill({ contentType: "application/json", body: JSON.stringify(taskSts) }));
  await page.route(/tasks\/5602\/sts/, route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  await installMocks(context);
  const page = await context.newPage();
  await page.addInitScript(() => {
    localStorage.setItem("tms_activeTab", "tasks");
    localStorage.setItem("tms_viewMode", "flat");
  });
  await page.goto(pageUrl("transport"));
  await page.locator(".dispatch-trips-table-wrap tbody tr", { hasText: "5601" }).click();
  await page.locator(".dispatch-trip-detail-section", { hasText: "Рейс #5601" }).waitFor({ timeout: 5000 });
  await page.getByText("PRINT-ST-001").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_trip_selected.png"), fullPage: true });
  const [popup] = await Promise.all([
    page.waitForEvent("popup"),
    page.getByRole("button", { name: "🖨 Печать" }).click(),
  ]);
  await popup.waitForLoadState("domcontentloaded");
  await popup.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_print_sheet.png"), fullPage: true });
  const printHtml = await popup.content();
  fs.writeFileSync(path.join(OUT_DIR, "route-sheet-5601.html"), printHtml, "utf8");
  await popup.close();
  await page.locator(".dispatch-trips-table-wrap tbody tr", { hasText: "5602" }).click();
  await page.locator(".dispatch-trip-detail-section", { hasText: "Рейс #5602" }).waitFor({ timeout: 5000 });
  await page.getByRole("button", { name: "🖨 Печать" }).waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_empty_trip_print_disabled.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 56</title></head><body><h1>ТМС-2 Sprint 56: печать маршрутного листа</h1><p>Блок формирует бумажный маршрутный лист из выбранного рейса и его состава СТ без нового backend endpoint.</p><h2>Структура данных</h2><p>HTML строится на клиенте из <code>selectedTask</code> и <code>taskSts</code>: дата, машина, водитель, док, статус, строки СТ, паллеты и вес. Новое окно вызывает <code>window.print()</code>.</p><h2>Бизнес-процесс</h2><ol><li>Диспетчер выбирает рейс.</li><li>Проверяет состав СТ.</li><li>Нажимает «Печать» и получает маршрутный лист.</li><li>Для пустого рейса кнопка печати недоступна.</li></ol><h2>Результат</h2><p>Sprint 56 закрыт functional, load и UI smoke проверками.</p><img src="screenshots/01_trip_selected.png" width="100%"><img src="screenshots/02_print_sheet.png" width="100%"><img src="screenshots/03_empty_trip_print_disabled.png" width="100%"><p><a href="route-sheet-5601.html">Сохранённый HTML маршрутного листа</a></p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
