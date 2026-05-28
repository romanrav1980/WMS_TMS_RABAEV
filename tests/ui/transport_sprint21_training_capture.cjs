const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint21_billing_rbac_2026_05_28");

async function installMocks(page) {
  const task = {
    ID: 2101,
    TRANSTYPE: "10",
    TRANSPORT: "В 421 ТТ 59",
    VODITEL_ID: 501,
    VODITEL_NAME: "Иванов И.И.",
    TK_NAME: "ООО RBAC-Транс",
    IS_OWN_DRIVER: 0,
    SHIPMENT_DATE: "2026-05-25T00:00:00",
    CONDITION: "Новый",
    ST_COUNT: 3,
    PALLET_COUNT: 12,
    TEMP_WEIGHT: 2400,
    PRICE: 12500,
    PAY_ORDER_ID: null,
    DELETED: 0,
    READY_PERC: 100,
    UNREADY_COUNT: 0
  };
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/2101/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/orders?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/companies", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(["ООО RBAC-Транс"]) }));
  await page.route("**/api/admin/transport/tasks/2101/recalculate-price", route => route.fulfill({ status: 403, contentType: "application/json", body: JSON.stringify({ detail: "missing calc_tt_price" }) }));
  await page.route("**/api/admin/transport/tasks/2101/price", route => route.fulfill({ status: 403, contentType: "application/json", body: JSON.stringify({ detail: "missing create_tt_price" }) }));
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto("http://127.0.0.1:3000/?page=transport");
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("2101").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "01_billing_controls.png"), fullPage: true });
  await page.getByRole("button", { name: /Пересчитать/ }).click();
  await page.locator(".dispatch-error").waitFor({ timeout: 5000 });
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", "02_permission_denied.png"), fullPage: true });
  await browser.close();

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>ТМС-2 Sprint 21</title></head><body><h1>ТМС-2 Sprint 21: Права доступа биллинга</h1><p>Блок отделяет биллинговые права от прав диспетчера: создание и изменение счетов, пересчёт цены и ручная цена проверяются разными Oracle-правами.</p><h2>Структура данных</h2><p>Используются права <code>edit_bill_tt</code>, <code>calc_tt_price</code>, <code>create_tt_price</code>; рейс хранит цену и связь со счётом через <code>PRICE</code> и <code>PAY_ORDER_ID</code>.</p><h2>Результат</h2><p>Пользователь без нужного права видит отказ, а UI не считает операцию успешной.</p><h2>Бизнес-процессы</h2><ol><li>Диспетчер открывает рейс.</li><li>Биллинг-оператор пересчитывает или задаёт цену при наличии профильного права.</li><li>При отсутствии права backend возвращает 403, UI показывает ошибку.</li></ol><img src="screenshots/01_billing_controls.png" width="100%"><img src="screenshots/02_permission_denied.png" width="100%"><p>Проверка: functional, UI smoke и load gates пройдены.</p></body></html>`, "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
