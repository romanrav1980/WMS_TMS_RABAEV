const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint31_cluster_sidebar_2026_05_28");

const clusters = [
  { RAION: "Север", ST_COUNT: 3, PALLET_COUNT: 12, WEIGHT_KG: 1200, VOLUME_M3: 5.5, STS: [] },
  { RAION: "Юг", ST_COUNT: 2, PALLET_COUNT: 7, WEIGHT_KG: 730, VOLUME_M3: 2.8, STS: [] },
  { RAION: "(без района)", ST_COUNT: 1, PALLET_COUNT: 2, WEIGHT_KG: 180, VOLUME_M3: 0.9, STS: [] },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify([{ ID: 1, NUM: "В 501 ТТ 59", MARKA: "MAN", PALLETS: 20 }]),
  }));
  await page.route("**/api/admin/transport/vehicles/available?**", route => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify([{ vehicle_num: "В 501 ТТ 59", status: "green", detail: "свободна", free_at: null }]),
  }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент" }]),
  }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(clusters) }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByRole("button", { name: "По районам" }).click();
  await page.locator(".cluster-sidebar").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_cluster_sidebar.png"), fullPage: true });
  await page.locator(".cluster-card").filter({ hasText: "Север" }).click();
  await page.locator(".cluster-card-active").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_cluster_selected.png"), fullPage: true });
  await page.locator(".cluster-card").filter({ hasText: "Север" }).getByRole("button", { name: "⚡ Рейс" }).click();
  await page.getByText("Рейс из кластера «Север»").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_cluster_create_dialog.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 31</title></head><body><h1>ТМС-2 Sprint 31: Панель районов</h1><p>Блок нужен диспетчеру для быстрого обзора свободных СТ по районам без прокрутки основной таблицы.</p><h2>Структура данных</h2><p>Панель строится из <code>GET /api/admin/transport/clusters</code>: район, количество СТ, паллеты, вес, объём и список СТ внутри района.</p><h2>Результат</h2><p>Диспетчер видит все районы слева, раскрывает нужный район в таблице и может начать создание рейса из карточки.</p><h2>Бизнес-процессы</h2><ol><li>Переключиться в режим «По районам».</li><li>Оценить район по количеству СТ, паллетам и весу.</li><li>Раскрыть район кликом по карточке.</li><li>Открыть диалог «Рейс» для создания маршрута из района.</li></ol><h2>Скриншоты</h2><img src="screenshots/01_cluster_sidebar.png" width="100%"><img src="screenshots/02_cluster_selected.png" width="100%"><img src="screenshots/03_cluster_create_dialog.png" width="100%"><p>Проверка: functional и UI smoke пройдены; live load gate заблокирован зависшим владельцем порта 8088.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
