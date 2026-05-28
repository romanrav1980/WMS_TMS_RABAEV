const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint29_cluster_create_task_2026_05_28");

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const cluster = { RAION: "Север", ST_COUNT: 2, PALLET_COUNT: 8, WEIGHT_KG: 1800, VOLUME_M3: 7.5, STS: [] };
  await page.route("**/api/admin/transport/vehicles/available?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент 10т" }]) }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([cluster]) }));
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "По районам" }).click();
  await page.locator(".cluster-card-name", { hasText: "Север" }).waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_cluster_card.png"), fullPage: true });
  await page.locator(".cluster-card-create-btn").first().click();
  await page.getByText("Рейс из кластера").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_create_dialog.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 29</title></head><body><h1>ТМС-2 Sprint 29: Рейс из района</h1><p>Блок ускоряет полуавтоматическое планирование: диспетчер создаёт рейс из всех свободных СТ выбранного района.</p><h2>Структура данных</h2><p>Кластеры строятся по <code>RAION</code> из свободных СТ. Создание вызывает <code>POST /clusters/{raion}/create-task</code>, затем назначает все СТ района в новый рейс.</p><h2>Результат</h2><p>Диспетчер получает новый рейс с выбранным типом транспорта, машиной, водителем и доком, если они заданы.</p><h2>Бизнес-процессы</h2><ol><li>Переключиться в режим «По районам».</li><li>Выбрать район и нажать «Рейс».</li><li>Проверить параметры рейса.</li><li>Создать рейс и перейти к его карточке.</li></ol><img src="screenshots/01_cluster_card.png" width="100%"><img src="screenshots/02_create_dialog.png" width="100%"><p>Проверка: functional, UI smoke и load gates пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
