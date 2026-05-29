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
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint57_quick_add_st_2026_05_29");

const tasks = [
  { ID: 5701, TRANSTYPE: "Тент", TRANSPORT: "Е715ТТ", VODITEL_ID: 1, VODITEL_NAME: "Иванов И.И.", DOCK: "Д-3", SHIPMENT_DATE: "2026-05-25", CONDITION: "Новый", ST_COUNT: 0, PALLET_COUNT: 0, TEMP_WEIGHT: 0, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 0, UNREADY_COUNT: 0 },
];

let taskSts = [];

async function installMocks(target) {
  await target.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await target.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await target.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await target.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await target.route(/\/api\/admin\/transport\/tasks(?:\?|$)/, route => route.fulfill({ contentType: "application/json", body: JSON.stringify(tasks) }));
  await target.route(/tasks\/5701\/sts/, async route => {
    if (route.request().method() === "POST") {
      const body = JSON.parse(route.request().postData() || "{}");
      taskSts = [{ ST_NUMBER: body.st_numbers[0], ADDR: "Быстро добавленная СТ", REGION: "Пермь", RAION: "Центр", ORD: 1, TRANSPORT_TYPE: "Тент", WARE_ID: 9201, PALLETS_COUNT: 1, WEIGHT_KG: 10, VOLUME_M3: 0.5, VERIFY_PERC: 100 }];
      await route.fulfill({ contentType: "application/json", body: JSON.stringify({ assigned: 1, warnings: [] }) });
      return;
    }
    await route.fulfill({ contentType: "application/json", body: JSON.stringify(taskSts) });
  });
  await target.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
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
  await page.locator(".dispatch-trips-table-wrap tbody tr", { hasText: "5701" }).click();
  await page.locator(".dispatch-trip-detail-section", { hasText: "Рейс #5701" }).waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_quick_add_empty.png"), fullPage: true });
  await page.locator(".dispatch-quick-add-input").fill("QUICK-ST-001");
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_quick_add_ready.png"), fullPage: true });
  await page.locator(".dispatch-quick-add-input").press("Enter");
  await page.locator(".dispatch-toast", { hasText: "СТ QUICK-ST-001 добавлен" }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-trip-sts-wrap .dispatch-gc-stnum", { hasText: "QUICK-ST-001" }).waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_quick_add_success.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 57</title></head><body><h1>ТМС-2 Sprint 57: быстрое добавление СТ</h1><p>Блок позволяет диспетчеру добавить СТ в выбранный рейс по номеру, не прокручивая и не фильтруя общий список заявок.</p><h2>Структура данных</h2><p>Форма отправляет существующий endpoint <code>POST /tasks/{id}/sts</code> с payload <code>{ st_numbers: [номер] }</code>. После успеха input очищается, состав рейса и списки перезагружаются.</p><h2>Бизнес-процесс</h2><ol><li>Выбрать рейс.</li><li>Ввести номер СТ в поле <code>+ СТ №</code>.</li><li>Нажать Enter или «Добавить».</li><li>Проверить toast и появление СТ в составе рейса.</li></ol><h2>Результат</h2><p>Sprint 57 закрыт functional, no-mutation load и UI smoke проверками.</p><img src="screenshots/01_quick_add_empty.png" width="100%"><img src="screenshots/02_quick_add_ready.png" width="100%"><img src="screenshots/03_quick_add_success.png" width="100%"></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
