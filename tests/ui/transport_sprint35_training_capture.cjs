const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint35_raion_filter_2026_05_28");
const clusters = [
  { RAION: "Ленинский", ST_COUNT: 2, PALLET_COUNT: 8, WEIGHT_KG: 1200, VOLUME_M3: 4.2, STS: [] },
  { RAION: "Свердловский", ST_COUNT: 1, PALLET_COUNT: 3, WEIGHT_KG: 480, VOLUME_M3: 1.4, STS: [] },
];

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify([{ ID: 1, NUM: "В 501 ТТ 59", MARKA: "MAN", PALLETS: 20 }]),
  }));
  await page.route("**/api/admin/transport/vehicles/available?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент" }]),
  }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks/3501", route => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify({ ID: 3501, TRANSTYPE: "10", TRANSPORT: null, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 2, PALLET_COUNT: 8, TEMP_WEIGHT: 1200, PAY_ORDER_ID: null, DELETED: 0 }),
  }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(clusters) }));
  await page.route("**/api/admin/transport/clusters/*/create-task", route => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify({ task_id: 3501, raion: "Ленинский", st_count: 2, warnings: [] }),
  }));
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByRole("button", { name: "По районам" }).click();
  await page.locator(".cluster-sidebar").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_clusters_mode.png"), fullPage: true });
  await page.locator(".cluster-card").filter({ hasText: "Ленинский" }).getByRole("button", { name: "⚡ Рейс" }).click();
  await page.getByText("Рейс из кластера «Ленинский»").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_create_from_raion.png"), fullPage: true });
  await page.getByRole("button", { name: "Создать рейс (2 СТ)" }).click();
  await page.getByText("Рейс #3501 создан из кластера").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_created_from_raion.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 35</title></head><body><h1>ТМС-2 Sprint 35: Фильтр района на стороне Oracle</h1><p>Блок ускоряет создание рейса из района: API больше не тянет все свободные СТ, а передаёт район сразу в SQL.</p><h2>Структура данных</h2><p><code>GET /available-sts</code> принимает <code>raion</code>. Обычный район превращается в <code>A.RAION = :raion</code>, а <code>(без района)</code> — в <code>A.RAION IS NULL</code>.</p><h2>Результат</h2><p>Кнопка «Рейс» в карточке района создаёт рейс только из СТ выбранного района и делает меньше работы в Oracle/API.</p><h2>Бизнес-процессы</h2><ol><li>Открыть «Заявки» в режиме «По районам».</li><li>Выбрать район.</li><li>Нажать «Рейс».</li><li>Создать рейс: backend фильтрует СТ района в Oracle.</li></ol><img src="screenshots/01_clusters_mode.png" width="100%"><img src="screenshots/02_create_from_raion.png" width="100%"><img src="screenshots/03_created_from_raion.png" width="100%"><p>Проверка: functional, UI smoke и безопасный load gate пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
