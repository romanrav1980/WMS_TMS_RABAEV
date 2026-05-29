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
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint53_filter_panel_collapse_2026_05_29");

const rows = [
  { ST_NUMBER: "FP-ST-001", ADDR: "Пермь, Ленина 1", REGION: "Пермь", RAION: "Центр", ORD: 1, TRANSPORT_TYPE: "Тент", WARE_ID: 9201, NAPR: "Пермь", PALLETS_COUNT: 5, WEIGHT_KG: 300, VOLUME_M3: 2, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 50 },
  { ST_NUMBER: "FP-ST-002", ADDR: "Чусовой, Мира 2", REGION: "Чусовой", RAION: "Север", ORD: 2, TRANSPORT_TYPE: "Реф", WARE_ID: 9202, NAPR: "Чусовой", PALLETS_COUNT: 8, WEIGHT_KG: 500, VOLUME_M3: 3, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: null },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "Тент", NAME: "Тент" }]) }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(rows) }));
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
    if (!sessionStorage.getItem("sprint53_initialized")) {
      localStorage.removeItem("tms_fpCollapsed");
      sessionStorage.setItem("sprint53_initialized", "1");
    }
  });
  await page.goto(pageUrl("transport"));
  await page.getByText("FP-ST-001").waitFor({ timeout: 10000 });
  const panel = page.locator(".dispatch-right-panel").first();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_panel_expanded.png"), fullPage: true });
  await panel.locator("input.dispatch-fp-input[placeholder='Адрес / регион']").fill("Пермь");
  await panel.locator(".dispatch-fp-badge", { hasText: "1" }).waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_active_filter_badge.png"), fullPage: true });
  await panel.locator(".dispatch-fp-collapse-btn").click();
  await panel.locator(".dispatch-fp-badge-alone", { hasText: "1" }).waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_panel_collapsed.png"), fullPage: true });
  await page.reload();
  await panel.locator(".dispatch-fp-collapse-btn").waitFor({ timeout: 10000 });
  await panel.evaluate(node => {
    if (!node.classList.contains("dispatch-fp-collapsed")) throw new Error("Collapsed state was not restored");
  });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "04_restored_collapsed.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 53</title></head><body><h1>ТМС-2 Sprint 53: сворачивание панели фильтров</h1><p>Блок освобождает горизонтальное место в диспетчерской таблице, когда фильтры уже настроены или временно не нужны.</p><h2>Структура данных</h2><p>Состояние хранится в <code>fpCollapsed</code> и сохраняется в <code>localStorage.tms_fpCollapsed</code>. При активных фильтрах в свернутом состоянии остается компактный бейдж.</p><h2>Бизнес-процесс</h2><ol><li>Диспетчер настраивает фильтры справа.</li><li>Нажимает «‹», чтобы свернуть панель до узкой полосы.</li><li>Продолжает работать с таблицей СТ; бейдж напоминает о включенных фильтрах.</li><li>После reload панель восстанавливается в выбранном состоянии.</li></ol><h2>Результат</h2><p>Sprint 53 закрыт functional, load и UI smoke проверками.</p><img src="screenshots/01_panel_expanded.png" width="100%"><img src="screenshots/02_active_filter_badge.png" width="100%"><img src="screenshots/03_panel_collapsed.png" width="100%"><img src="screenshots/04_restored_collapsed.png" width="100%"></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
