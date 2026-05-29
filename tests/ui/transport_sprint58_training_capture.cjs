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
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint58_expand_collapse_clusters_2026_05_29");

const clusters = [
  { RAION: "Север", ST_COUNT: 1, PALLET_COUNT: 5, WEIGHT_KG: 300, VOLUME_M3: 2.5, STS: [{ ST_NUMBER: "CL-ST-001", ADDR: "Первый", REGION: "Пермь", RAION: "Север", ORD: 1, TRANSPORT_TYPE: "Тент", WARE_ID: 9201, PALLETS_COUNT: 5, WEIGHT_KG: 300, VOLUME_M3: 2.5, VERIFY_PERC: 100 }] },
  { RAION: "Юг", ST_COUNT: 1, PALLET_COUNT: 8, WEIGHT_KG: 500, VOLUME_M3: 3.0, STS: [{ ST_NUMBER: "CL-ST-002", ADDR: "Второй", REGION: "Пермь", RAION: "Юг", ORD: 2, TRANSPORT_TYPE: "Реф", WARE_ID: 9202, PALLETS_COUNT: 8, WEIGHT_KG: 500, VOLUME_M3: 3.0, VERIFY_PERC: 75 }] },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(clusters) }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.addInitScript(() => {
    localStorage.setItem("tms_activeTab", "tasks");
    localStorage.setItem("tms_viewMode", "clusters");
  });
  await page.goto(pageUrl("transport"));
  await page.locator(".cluster-sidebar").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_collapsed_clusters.png"), fullPage: true });
  await page.getByTitle("Развернуть все районы").click();
  await page.locator(".dispatch-st-section", { hasText: "CL-ST-001" }).waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_all_expanded.png"), fullPage: true });
  await page.getByTitle("Свернуть все районы").click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_all_collapsed.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 58</title></head><body><h1>ТМС-2 Sprint 58: развернуть и свернуть все районы</h1><p>Блок ускоряет работу в кластерном режиме, когда диспетчеру нужно быстро увидеть все СТ по районам или снова свернуть список.</p><h2>Структура данных</h2><p>Состояние раскрытия хранится в <code>expandedRaions</code>. Кнопка «⊞ Все» записывает все <code>RAION</code> из <code>clusters</code>, «⊟ Нет» очищает набор.</p><h2>Бизнес-процесс</h2><ol><li>Включить режим «По районам».</li><li>Нажать «⊞ Все» для обзора всех СТ внутри районов.</li><li>Нажать «⊟ Нет», чтобы вернуться к компактному списку кластеров.</li></ol><h2>Результат</h2><p>Sprint 58 закрыт functional, load и UI smoke проверками.</p><img src="screenshots/01_collapsed_clusters.png" width="100%"><img src="screenshots/02_all_expanded.png" width="100%"><img src="screenshots/03_all_collapsed.png" width="100%"></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
