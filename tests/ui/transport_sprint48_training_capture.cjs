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
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint48_today_button_2026_05_29");

function yesterdayIso() {
  const d = new Date();
  d.setDate(d.getDate() - 1);
  return d.toISOString().slice(0, 10);
}

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const yesterday = yesterdayIso();

  await installMocks(page);
  await page.addInitScript(({ yesterday }) => {
    localStorage.setItem("tms_filterDate", yesterday);
    localStorage.setItem("tms_stDate", yesterday);
    localStorage.setItem("tms_routeShipDate", yesterday);
    localStorage.setItem("tms_activeTab", "tasks");
  }, { yesterday });

  await page.goto(pageUrl("transport"));
  await page.locator(".dispatch-shell").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_tasks_today_visible.png"), fullPage: true });

  await page.locator(".dispatch-trips-section .dispatch-trips-toolbar .dispatch-today-btn").click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_tasks_after_today.png"), fullPage: true });

  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_routes_today_visible.png"), fullPage: true });

  await page.locator(".dispatch-trips-toolbar").filter({ hasText: "Маршруты за" }).locator(".dispatch-today-btn").click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "04_routes_after_today.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 48</title></head><body><h1>ТМС-2 Sprint 48: кнопка «Сегодня»</h1><p>Блок ускоряет возврат диспетчера к текущей рабочей дате после просмотра прошлых или будущих дней.</p><h2>Структура данных</h2><p>Кнопка управляет клиентскими состояниями <code>filterDate</code> и <code>routeShipDate</code>. При сбросе выполняется немедленная загрузка <code>GET /tasks?shipment_date=today</code>.</p><h2>Бизнес-процесс</h2><ol><li>Диспетчер уходит на другой день стрелками или ручным вводом.</li><li>UI показывает «Сегодня» рядом с датой.</li><li>Клик возвращает дату на сегодня, перезагружает рейсы и скрывает кнопку.</li><li>Поведение одинаково для вкладок «Заявки» и «Маршруты».</li></ol><h2>Результат</h2><p>Sprint 48 закрыт functional, load и UI smoke проверками.</p><img src="screenshots/01_tasks_today_visible.png" width="100%"><img src="screenshots/02_tasks_after_today.png" width="100%"><img src="screenshots/03_routes_today_visible.png" width="100%"><img src="screenshots/04_routes_after_today.png" width="100%"></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
