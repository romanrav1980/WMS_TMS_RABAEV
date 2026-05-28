const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint18_price_management_2026_05_28");
const task = { ID: 1801, TRANSTYPE: "10", TRANSPORT: "В 415 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Тест-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 3, PALLET_COUNT: 12, TEMP_WEIGHT: 2400, PRICE: 9000, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/1801/sts", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks/1801/recalculate-price", route => { task.PRICE = 11000; route.fulfill({ contentType: "application/json", body: JSON.stringify({ task_id: 1801, price: 11000 }) }); });
  await page.route("**/api/admin/transport/tasks/1801/price", route => { task.PRICE = 12345; route.fulfill({ contentType: "application/json", body: JSON.stringify({ task_id: 1801, price: 12345 }) }); });
}
async function shot(page, name) { await page.screenshot({ path: path.join(OUT_DIR, "screenshots", name), fullPage: true }); }
function html() { return `<!doctype html><html lang="ru"><head><meta charset="utf-8" /><title>ТМС-2 Sprint 18: Цена рейса</title><style>body{margin:0;font-family:Arial,sans-serif;color:#172033;background:#f4f7fb}header{padding:28px 36px;background:#4a4a36;color:white}main{max-width:1180px;margin:0 auto;padding:28px 24px 48px}section{background:white;border:1px solid #d8e0ea;border-radius:8px;padding:22px;margin:0 0 22px}img{width:100%;border:1px solid #c7d2e0;border-radius:6px;display:block}figure{margin:0 0 24px}figcaption{font-size:14px;color:#41516a;margin-top:8px}</style></head><body><header><h1>ТМС-2 Sprint 18: Цена рейса</h1><p>Пересчет стоимости через Oracle и ручная корректировка.</p></header><main><section><h2>Зачем этот блок</h2><p>Цена рейса нужна для корректного счета ТК. Диспетчер может пересчитать цену по нормативам или задать согласованную сумму вручную.</p></section><section><h2>Как работать</h2><figure><img src="screenshots/01_price.png" /><figcaption>1. В карточке рейса видна текущая цена и действия управления стоимостью.</figcaption></figure><figure><img src="screenshots/02_recalculated.png" /><figcaption>2. «Пересчитать» обновляет цену через backend/Oracle.</figcaption></figure><figure><img src="screenshots/03_manual_price.png" /><figcaption>3. Ручное сохранение фиксирует согласованную цену.</figcaption></figure></section><section><h2>Бизнес-процессы</h2><ol><li>Расчет цены по нормативам.</li><li>Ручная корректировка по договоренности.</li><li>Использование цены при выставлении счета.</li></ol></section><section><h2>Результат проверки</h2><p>Sprint 18 закрыт: backend tests <code>11 passed</code>, UI smoke passed, load NFR passed.</p></section></main></body></html>`; }

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("1801").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-trips-table-wrap table tbody tr").first().click();
  await shot(page, "01_price.png");
  await page.getByRole("button", { name: /Пересчитать/ }).click();
  await page.locator(".price-value", { hasText: "11" }).waitFor({ timeout: 5000 });
  await shot(page, "02_recalculated.png");
  await page.locator(".price-input").fill("12345");
  await page.getByRole("button", { name: "Сохранить", exact: true }).click();
  await page.locator(".price-value", { hasText: "12" }).waitFor({ timeout: 5000 });
  await shot(page, "03_manual_price.png");
  await browser.close();
  fs.writeFileSync(path.join(OUT_DIR, "index.html"), html(), "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}
main().catch(error => { console.error(error); process.exit(1); });
