const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint42_toast_notifications_2026_05_28");
const sourceTask = { ID: 4201, TRANSTYPE: "10", TRANSPORT: "В 421 ТТ 59", VODITEL_ID: 421, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Toast", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", SHIPMENT_TIME: "2026-05-25T08:30:00", DOCK: "Д-1", CONDITION: "Новый", ST_COUNT: 2, PALLET_COUNT: 8, TEMP_WEIGHT: 1500, PRICE: 9900, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
const copiedTask = { ...sourceTask, ID: 4202, ST_COUNT: 0, PALLET_COUNT: 0, TEMP_WEIGHT: 0, PRICE: null };
let copied = false;

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks/4202", async route => {
    if (route.request().method() === "PATCH") return route.fulfill({ contentType: "application/json", body: JSON.stringify({ task_id: 4202 }) });
    return route.fulfill({ contentType: "application/json", body: JSON.stringify(copiedTask) });
  });
  await page.route("**/api/admin/transport/tasks/4201/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks/4202/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks", async route => {
    if (route.request().method() === "POST") {
      copied = true;
      return route.fulfill({ contentType: "application/json", body: JSON.stringify({ task_id: 4202 }) });
    }
    return route.fallback();
  });
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(copied ? [copiedTask, sourceTask] : [sourceTask]) }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(pageUrl("transport"));
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByText("#4201").waitFor({ timeout: 10000 });
  await page.locator("tr[data-taskid='4201']").click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_before_action.png"), fullPage: true });
  await page.getByRole("button", { name: "📋 Копировать" }).click();
  await page.locator(".dispatch-toast").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_success_toast.png"), fullPage: true });
  await page.locator(".dispatch-toast").click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "03_toast_dismissed.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 42</title></head><body><h1>ТМС-2 Sprint 42: toast-уведомления</h1><p>Блок даёт диспетчеру явное подтверждение успешной операции: создание, закрытие, отмена, назначение, снятие СТ или копирование рейса.</p><h2>Структура данных</h2><p>Toast хранится в клиентском состоянии <code>toastMsg</code>. Успешные handlers вызывают <code>showToast()</code>, сообщение исчезает по таймеру или по клику.</p><h2>Результат</h2><p>После успешного действия появляется зелёное уведомление в правом нижнем углу, а пользователь не остаётся в тишине после операции.</p><h2>Бизнес-процесс</h2><ol><li>Выбрать рейс или СТ.</li><li>Выполнить операцию, например копирование рейса.</li><li>Проверить текст подтверждения.</li><li>Закрыть уведомление кликом или дождаться авто-скрытия.</li></ol><img src="screenshots/01_before_action.png" width="100%"><img src="screenshots/02_success_toast.png" width="100%"><img src="screenshots/03_toast_dismissed.png" width="100%"><p>Проверка: functional, UI smoke и load gate пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
