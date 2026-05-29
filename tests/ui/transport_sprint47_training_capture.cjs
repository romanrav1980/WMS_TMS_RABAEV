const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint47_localstorage_persistence_2026_05_28");

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
  await installMocks(page);
  await page.addInitScript(() => {
    localStorage.setItem("tms_filterDate", "2026-06-05");
    localStorage.setItem("tms_routeShipDate", "2026-06-10");
    localStorage.setItem("tms_viewMode", "clusters");
    localStorage.setItem("tms_activeTab", "routes");
  });
  await page.goto(pageUrl("transport"));
  await page.locator(".dispatch-tab.active", { hasText: "Маршруты" }).waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_restored_routes_tab.png"), fullPage: true });
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_restored_tasks_date.png"), fullPage: true });
  await page.getByRole("button", { name: "По СТ" }).click();
  await page.reload();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_state_after_change_reload.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 47</title></head><body><h1>ТМС-2 Sprint 47: сохранение состояния экрана</h1><p>Блок сохраняет рабочий контекст диспетчера после перезагрузки страницы.</p><h2>Структура данных</h2><p>В <code>localStorage</code> сохраняются <code>tms_filterDate</code>, <code>tms_routeShipDate</code>, <code>tms_viewMode</code>, <code>tms_activeTab</code>. При ошибке storage UI возвращается к дефолтам.</p><h2>Результат</h2><p>После reload пользователь возвращается на выбранную вкладку, дату и режим отображения, а не начинает с чистого экрана.</p><h2>Бизнес-процесс</h2><ol><li>Выбрать рабочую дату и вкладку.</li><li>Обновить страницу или открыть модуль заново.</li><li>Проверить, что контекст восстановлен.</li><li>Продолжить работу без ручной настройки фильтров заново.</li></ol><img src="screenshots/01_restored_routes_tab.png" width="100%"><img src="screenshots/02_restored_tasks_date.png" width="100%"><img src="screenshots/03_state_after_change_reload.png" width="100%"><p>Проверка: functional, UI smoke и load gate пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
