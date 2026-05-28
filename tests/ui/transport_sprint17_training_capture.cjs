const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const OUT_DIR = path.resolve("wiki-raw/tms2_training/sprint17_billing_registry_2026_05_28");
const orders = [
  { order_id: 1701, num: "B-1701", company: "ООО Альфа-Транс", date_from: "2026-05-25", date_to: "2026-05-25", closed: 0, payed: 0, total_price: 12500, task_count: 1, num_plat: null },
  { order_id: 1702, num: "B-1702", company: "ООО Бета-Логистик", date_from: "2026-05-25", date_to: "2026-05-25", closed: 1, payed: 1, total_price: 8000, task_count: 2, num_plat: "ПП-22" },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/orders?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(orders) }));
}

async function shot(page, name) {
  await page.screenshot({ path: path.join(OUT_DIR, "screenshots", name), fullPage: true });
}

function html() {
  return `<!doctype html><html lang="ru"><head><meta charset="utf-8" /><title>ТМС-2 Sprint 17: Реестр счетов</title><style>
body{margin:0;font-family:Arial,sans-serif;color:#172033;background:#f4f7fb}header{padding:28px 36px;background:#51452f;color:white}main{max-width:1180px;margin:0 auto;padding:28px 24px 48px}section{background:white;border:1px solid #d8e0ea;border-radius:8px;padding:22px;margin:0 0 22px}h1,h2{margin-top:0}h2{color:#51452f}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.card{background:#f8fbff;border:1px solid #d8e0ea;border-radius:6px;padding:14px}img{width:100%;border:1px solid #c7d2e0;border-radius:6px;display:block}figure{margin:0 0 24px}figcaption{font-size:14px;color:#41516a;margin-top:8px;line-height:1.45}code{background:#eef4fb;padding:1px 4px;border-radius:3px}</style></head><body>
<header><h1>ТМС-2 Sprint 17: Реестр счетов</h1><p>Общий список счетов с фильтрами, итогами и выгрузкой.</p></header><main>
<section><h2>Зачем этот блок</h2><p>Реестр счетов нужен для ежедневного контроля выставленных, закрытых и оплаченных счетов по транспортным компаниям.</p><div class="grid"><div class="card"><b>Вход</b><br>Биллинг-заказы и связанные рейсы.</div><div class="card"><b>Процесс</b><br>Фильтрация по датам, ТК и статусу.</div><div class="card"><b>Результат</b><br>Таблица счетов, итоги по ТК и CSV/Excel.</div></div></section>
<section><h2>Как работать</h2><figure><img src="screenshots/01_registry.png" /><figcaption><b>1. Реестр.</b> Вкладка «Биллинг» показывает счета, компании, периоды, суммы и статусы.</figcaption></figure><figure><img src="screenshots/02_filters.png" /><figcaption><b>2. Фильтры.</b> Фильтр по компании и статусу сужает список для проверки конкретной ТК.</figcaption></figure><figure><img src="screenshots/03_export.png" /><figcaption><b>3. Выгрузка.</b> CSV/Excel используется для передачи реестра в бухгалтерию.</figcaption></figure></section>
<section><h2>Бизнес-процессы</h2><ol><li>Контроль выставленных счетов.</li><li>Поиск счетов по ТК и периоду.</li><li>Сверка итогов по транспортной компании.</li><li>Выгрузка реестра для бухгалтерии.</li></ol></section>
<section><h2>Результат проверки</h2><p>Sprint 17 закрыт: backend tests <code>12 passed</code>, UI smoke passed, load NFR passed.</p></section>
</main></body></html>`;
}

async function main() {
  fs.mkdirSync(path.join(OUT_DIR, "screenshots"), { recursive: true });
  const browser = await chromium.launch();
  const context = await browser.newContext({ acceptDownloads: true, viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Биллинг" }).click();
  await page.getByText("B-1701").waitFor({ timeout: 10000 });
  await shot(page, "01_registry.png");
  await page.locator(".billing-fp-input[placeholder='Компания (ТК)']").fill("Альфа");
  await shot(page, "02_filters.png");
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: /CSV/ }).click();
  await downloadPromise;
  await shot(page, "03_export.png");
  await browser.close();
  fs.writeFileSync(path.join(OUT_DIR, "index.html"), html(), "utf8");
  console.log(JSON.stringify({ ok: true, outDir: OUT_DIR }));
}

main().catch(error => { console.error(error); process.exit(1); });
