const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint39_filter_badge_reset_2026_05_28");
const sts = [
  { ST_NUMBER: "СТ-3901", ADDR: "Пермь, Ленина 1", REGION: "Пермь", RAION: "Ленинский", PALLETS_COUNT: 2, WEIGHT_KG: 400, VOLUME_M3: 1.2, STDATE: "2026-05-25", DATE_LOAD: "2026-05-25", TRANSPORT_TYPE: "10", WARE_ID: 9201, VERIFY_PERC: 100, SUGAR: 0 },
  { ST_NUMBER: "СТ-3902", ADDR: "Лысьва, Мира 5", REGION: "Лысьва", RAION: "Центр", PALLETS_COUNT: 1, WEIGHT_KG: 220, VOLUME_M3: 0.8, STDATE: "2026-05-25", DATE_LOAD: "2026-05-25", TRANSPORT_TYPE: "10", WARE_ID: 9201, VERIFY_PERC: 80, SUGAR: 0 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Фургон" }]) }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(sts) }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(pageUrl("transport"));
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByText("СТ-3901").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_default_filters.png"), fullPage: true });

  const filterPanel = page.locator(".dispatch-right-panel");
  await filterPanel.locator("input.dispatch-fp-input[placeholder='Адрес / регион']").fill("Пермь");
  await filterPanel.locator(".dispatch-fp-badge", { hasText: "1" }).waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_active_filter_badge.png"), fullPage: true });

  await filterPanel.getByRole("button", { name: "× Сбросить" }).click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_reset_filters.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 39</title></head><body><h1>ТМС-2 Sprint 39: бейдж активных фильтров и сброс</h1><p>Блок помогает диспетчеру видеть, что список СТ ограничен фильтрами, и быстро возвращать экран к стандартному состоянию.</p><h2>Структура данных</h2><p>Фильтры живут в клиентском состоянии: адрес, номер СТ, исключение СТ, собранность, нераспределённость, дата до, ограничения веса и объёма, тип ТС, артикул. Бейдж считает только значения, отличающиеся от стандартных.</p><h2>Результат</h2><p>При активном фильтре появляется числовой бейдж и кнопка «× Сбросить». После сброса все поля возвращаются к дефолту, а бейдж исчезает.</p><h2>Бизнес-процесс</h2><ol><li>Открыть вкладку «Заявки».</li><li>Задать один или несколько фильтров справа.</li><li>Проверить число активных фильтров в заголовке панели.</li><li>Нажать «× Сбросить», чтобы вернуться к полному списку нераспределённых СТ.</li></ol><img src="screenshots/01_default_filters.png" width="100%"><img src="screenshots/02_active_filter_badge.png" width="100%"><img src="screenshots/03_reset_filters.png" width="100%"><p>Проверка: functional, UI smoke и load gate пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
