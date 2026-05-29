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
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint55_visible_totals_2026_05_29");

const sts = [
  { ST_NUMBER: "TOT-ST-001", ADDR: "Первый", REGION: "Пермь", RAION: "Центр", ORD: 1, TRANSPORT_TYPE: "Тент", WARE_ID: 9201, NAPR: "Пермь", PALLETS_COUNT: 5, WEIGHT_KG: 300, VOLUME_M3: 2.5, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 100 },
  { ST_NUMBER: "TOT-ST-002", ADDR: "Второй", REGION: "Лысьва", RAION: "Север", ORD: 2, TRANSPORT_TYPE: "Реф", WARE_ID: 9202, NAPR: "Лысьва", PALLETS_COUNT: 8, WEIGHT_KG: 500, VOLUME_M3: 3.0, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 75 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(sts) }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.addInitScript(() => {
    localStorage.setItem("tms_activeTab", "tasks");
    localStorage.setItem("tms_viewMode", "flat");
  });
  await page.goto(pageUrl("transport"));
  await page.getByText("TOT-ST-001").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_all_visible_totals.png"), fullPage: true });
  await page.locator(".dispatch-st-section tbody input[type='checkbox']").nth(0).check();
  await page.locator(".dispatch-sel-bar-stat", { hasText: "P=5" }).waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_selected_totals_separate.png"), fullPage: true });
  await page.locator(".dispatch-ware-select").selectOption("9201");
  await page.locator(".dispatch-pmv-all", { hasText: "П=5" }).waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_filtered_visible_totals.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 55</title></head><body><h1>ТМС-2 Sprint 55: итоги по видимым СТ</h1><p>Блок показывает общий объём работы в текущем списке СТ, независимо от того, что выделено для операции.</p><h2>Структура данных</h2><p>Итог <code>П/M/V</code> считается на клиенте по <code>wareFilteredSts</code>: паллеты, вес и объем всех видимых строк. Панель выделения Sprint 51 продолжает считать только выбранные СТ.</p><h2>Бизнес-процесс</h2><ol><li>Диспетчер смотрит общий объём доступных СТ.</li><li>Выделяет часть строк: selected-bar меняется, общий итог остается по видимому списку.</li><li>Фильтрует склад: общий итог пересчитывается по отфильтрованным СТ.</li></ol><h2>Результат</h2><p>Sprint 55 закрыт functional, load и UI smoke проверками.</p><img src="screenshots/01_all_visible_totals.png" width="100%"><img src="screenshots/02_selected_totals_separate.png" width="100%"><img src="screenshots/03_filtered_visible_totals.png" width="100%"></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
