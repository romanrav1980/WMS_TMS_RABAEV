const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";

const orders = [
  { order_id: 1701, num: "B-1701", company: "ООО Альфа-Транс", date_from: "2026-05-25", date_to: "2026-05-25", closed: 0, payed: 0, total_price: 12500, task_count: 1, num_plat: null },
  { order_id: 1702, num: "B-1702", company: "ООО Бета-Логистик", date_from: "2026-05-25", date_to: "2026-05-25", closed: 1, payed: 1, total_price: 8000, task_count: 2, num_plat: "ПП-22" },
];

const calls = { list: 0 };

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/orders?**", route => {
    calls.list += 1;
    const url = new URL(route.request().url());
    const company = url.searchParams.get("company") || "";
    const statusClosed = url.searchParams.get("closed");
    const statusPayed = url.searchParams.get("payed");
    let data = orders;
    if (company) data = data.filter(o => o.company.includes(company));
    if (statusClosed === "1") data = data.filter(o => o.closed);
    if (statusPayed === "1") data = data.filter(o => o.payed);
    route.fulfill({ contentType: "application/json", body: JSON.stringify(data) });
  });
  await page.route("**/api/admin/transport/billing/orders/1701/tasks", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ tt_id: 1501, transport: "В 415 ТТ 59", shipment_date: "2026-05-25", price: 12500 }]) }));
}

async function main() {
  const browser = await chromium.launch();
  const context = await browser.newContext({ acceptDownloads: true, viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  await installMocks(page);

  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Биллинг" }).click();
  await page.getByText("Реестр счетов").waitFor({ timeout: 10000 });
  await page.getByText("B-1701").waitFor({ timeout: 5000 });
  await page.locator(".billing-totals").waitFor({ timeout: 5000 });
  await page.locator(".billing-fp-input[placeholder='Компания (ТК)']").fill("Альфа");
  await page.getByText("B-1701").waitFor({ timeout: 5000 });
  await page.getByText("B-1702").waitFor({ state: "hidden", timeout: 5000 });
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: /CSV/ }).click();
  await downloadPromise;

  if (calls.list < 2) throw new Error(`Billing registry did not reload: ${JSON.stringify(calls)}`);
  await browser.close();
  console.log(JSON.stringify({ ok: true, calls }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
