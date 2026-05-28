const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint25_detach_billing_2026_05_28");

async function installMocks(page) {
  const task = { ID: 2501, TRANSTYPE: "10", TRANSPORT: "В 451 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Отвязка-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Отгружен", ST_COUNT: 3, PALLET_COUNT: 12, TEMP_WEIGHT: 2400, PRICE: 12500, PAY_ORDER_ID: 2501, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
  const openOrder = { order_id: 2501, num: "B-2501", company: "ООО Отвязка-Транс", date_from: "2026-05-25", date_to: "2026-05-25", closed: 0, payed: 0, total_price: 12500, task_count: 1 };
  const registryOrder = { order_id: 2502, num: "B-2502", company: "ООО Отвязка-Транс", date_from: "2026-05-25", date_to: "2026-05-25", closed: 0, payed: 0, total_price: 24000, task_count: 2 };
  const detailTasks = [
    { tt_id: 2511, transport: "В 452 ТТ 59", shipment_date: "2026-05-25", status: "Отгружен", price: 12000 },
    { tt_id: 2512, transport: "В 453 ТТ 59", shipment_date: "2026-05-25", status: "Отгружен", price: 12000 },
  ];
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/2501/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/orders/2501", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(openOrder) }));
  await page.route("**/api/admin/transport/billing/orders?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([registryOrder]) }));
  await page.route("**/api/admin/transport/billing/orders/2502/tasks", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(detailTasks) }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("2501").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await page.getByRole("button", { name: "Снять с биллинга" }).waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_task_detach_button.png"), fullPage: true });
  await page.getByRole("button", { name: "Биллинг", exact: true }).click();
  await page.getByText("B-2502").waitFor({ timeout: 10000 });
  await page.getByText("B-2502").click();
  await page.getByText("#2511").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_detail_detach_button.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 25</title></head><body><h1>ТМС-2 Sprint 25: Снять рейс с биллинга</h1><p>Блок позволяет отвязать ошибочно выставленный рейс от открытого счёта из карточки рейса или из панели деталей счёта.</p><h2>Структура данных</h2><p>Операция очищает <code>RRL_TRANSPORT_TASK.PAY_ORDER_ID</code> через <code>DELETE /billing/orders/{order_id}/tasks/{tt_id}</code>.</p><h2>Результат</h2><p>Рейс снова доступен для корректного выставления; закрытые и оплаченные счета защищены от изменения.</p><h2>Бизнес-процессы</h2><ol><li>Открыть рейс со счётом и нажать «Снять с биллинга».</li><li>Или открыть счёт в реестре и нажать крестик напротив рейса.</li><li>Подтвердить операцию и проверить исчезновение связи со счётом.</li></ol><img src="screenshots/01_task_detach_button.png" width="100%"><img src="screenshots/02_detail_detach_button.png" width="100%"><p>Проверка: functional, UI smoke и load gates пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
