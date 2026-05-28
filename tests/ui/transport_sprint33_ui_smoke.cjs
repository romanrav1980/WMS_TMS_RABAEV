const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const task = { ID: 3301, TRANSTYPE: "10", TRANSPORT: "В 501 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Brief-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 1, PALLET_COUNT: 4, TEMP_WEIGHT: 800, PRICE: 1200, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
}

async function headerTexts(page) {
  return page.locator(".dispatch-trips-table-wrap table thead th").evaluateAll(nodes => nodes.map(n => n.textContent.trim()));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("3301").waitFor({ timeout: 10000 });
  const full = await headerTexts(page);
  for (const col of ["Объём", "Тип", "Цена", "ТК", "Логист"]) {
    if (!full.includes(col)) throw new Error(`Full mode missing ${col}: ${full.join("|")}`);
  }
  await page.getByLabel("Кратко").check();
  await page.locator(".routes-brief").waitFor({ timeout: 5000 });
  const brief = await headerTexts(page);
  for (const col of ["Объём", "Тип", "Цена", "ТК", "Логист"]) {
    if (brief.includes(col)) throw new Error(`Brief mode still shows ${col}: ${brief.join("|")}`);
  }
  for (const col of ["Отгрузка", "#", "Пал.", "Вес", "Машина", "Водитель", "ДОК", "Регионы", "Статус"]) {
    if (!brief.includes(col)) throw new Error(`Brief mode missing ${col}: ${brief.join("|")}`);
  }
  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => { console.error(error); process.exit(1); });
