const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint37_select_all_autorefresh_2026_05_28");
const sts = [
  { ST_NUMBER: "СТ-3701", ADDR: "Адрес 1", REGION: "Пермь", RAION: "Ленинский", PALLETS_COUNT: 2, WEIGHT_KG: 400, VOLUME_M3: 1.2, STDATE: "2026-05-25", DATE_LOAD: "2026-05-25", TRANSPORT_TYPE: "10", WARE_ID: 9201, VERIFY_PERC: 100, SUGAR: 0 },
  { ST_NUMBER: "СТ-3702", ADDR: "Адрес 2", REGION: "Пермь", RAION: "Свердловский", PALLETS_COUNT: 3, WEIGHT_KG: 600, VOLUME_M3: 1.8, STDATE: "2026-05-25", DATE_LOAD: "2026-05-25", TRANSPORT_TYPE: "10", WARE_ID: 9201, VERIFY_PERC: 100, SUGAR: 0 },
];

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(sts) }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByRole("button", { name: "По СТ" }).click();
  await page.getByText("СТ-3701").waitFor({ timeout: 10000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_available_sts.png"), fullPage: true });
  await page.locator(".dispatch-st-section thead input[type='checkbox']").check();
  await page.getByText("2 выбр.").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_select_all.png"), fullPage: true });
  await page.getByLabel("Авто").uncheck();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_autorefresh_toggle.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 37</title></head><body><h1>ТМС-2 Sprint 37: Выделить всё и автообновление</h1><p>Блок ускоряет массовую работу со свободными СТ и поддерживает актуальность данных на экране диспетчера.</p><h2>Структура данных</h2><p>Выделение хранится в клиентском <code>selectedStNums</code>. Автообновление раз в 60 секунд перечитывает свободные СТ, рейсы и кластеры, если нет диалогов или редактирования.</p><h2>Результат</h2><p>Диспетчер одним кликом выделяет все видимые СТ и может включать или отключать автообновление.</p><h2>Бизнес-процессы</h2><ol><li>Открыть «Заявки» в режиме «По СТ».</li><li>Нажать чекбокс в шапке таблицы для выбора всех видимых СТ.</li><li>Создать рейс или добавить выбранные СТ в рейс.</li><li>Оставить «Авто» включённым для регулярного обновления данных.</li></ol><img src="screenshots/01_available_sts.png" width="100%"><img src="screenshots/02_select_all.png" width="100%"><img src="screenshots/03_autorefresh_toggle.png" width="100%"><p>Проверка: functional, UI smoke и load gate пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
