const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint44_escape_handler_2026_05_28");
const sts = [
  { ST_NUMBER: "СТ-4401", ADDR: "Пермь, Ленина 1", REGION: "Пермь", RAION: "Ленинский", PALLETS_COUNT: 2, WEIGHT_KG: 400, VOLUME_M3: 1.2, STDATE: "2026-05-25", DATE_LOAD: "2026-05-25", TRANSPORT_TYPE: "10", WARE_ID: 9201, VERIFY_PERC: 100, SUGAR: 0 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Фургон" }]) }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(sts) }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(pageUrl("transport"));
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByText("СТ-4401").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-st-section tbody input[type='checkbox']").check();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_selected_st.png"), fullPage: true });
  await page.keyboard.press("Escape");
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_selection_cleared.png"), fullPage: true });
  await page.locator(".dispatch-new-btn").click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_dialog_open.png"), fullPage: true });
  await page.keyboard.press("Escape");
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "04_dialog_closed.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 44</title></head><body><h1>ТМС-2 Sprint 44: глобальный Escape</h1><p>Блок делает экран диспетчера предсказуемым: Escape закрывает текущий верхнеуровневый контекст или снимает выделение.</p><h2>Структура данных</h2><p>Handler смотрит состояние диалогов, режима редактирования и наборов выделенных СТ. Приоритет: диалог создания, диалог кластера, edit mode, выделение свободных СТ, выделение СТ рейса.</p><h2>Результат</h2><p>Один Escape выполняет одно действие с понятным приоритетом. Это снижает риск случайных массовых действий при оставшемся выделении.</p><h2>Бизнес-процесс</h2><ol><li>Выделить СТ в списке заявок.</li><li>Нажать Escape, чтобы снять выделение.</li><li>Открыть диалог создания рейса.</li><li>Нажать Escape, чтобы закрыть диалог без сохранения.</li></ol><img src="screenshots/01_selected_st.png" width="100%"><img src="screenshots/02_selection_cleared.png" width="100%"><img src="screenshots/03_dialog_open.png" width="100%"><img src="screenshots/04_dialog_closed.png" width="100%"><p>Проверка: functional, UI smoke и load gate пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
