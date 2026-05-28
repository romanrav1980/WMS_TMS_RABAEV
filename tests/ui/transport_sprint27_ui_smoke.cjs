const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const orders = [
  { order_id: 2701, num: "B-2701", company: "ООО Реестр-Транс", date_from: "2026-05-01", date_to: "2026-05-31", closed: 0, payed: 0, total_price: 25000, task_count: 1, num_plat: "ПП-2701" },
  { order_id: 2702, num: "B-2702", company: "ООО Реестр-Транс", date_from: "2026-05-01", date_to: "2026-05-31", closed: 1, payed: 1, total_price: 15000, task_count: 1, num_plat: "ПП-2702" },
];
const xlsxBytes = Buffer.from("UEsDBAoAAAAAA", "base64");
const calls = { export: 0 };

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/billing/orders?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(orders) }));
  await page.route("**/api/admin/transport/billing/orders/export.xlsx?**", route => {
    calls.export += 1;
    route.fulfill({ contentType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers: { "Content-Disposition": 'attachment; filename="billing_registry.xlsx"' }, body: xlsxBytes });
  });
}

async function main() {
  const browser = await chromium.launch();
  const context = await browser.newContext({ acceptDownloads: true, viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Биллинг", exact: true }).click();
  await page.getByText("B-2701").waitFor({ timeout: 10000 });
  const downloadPromise = page.waitForEvent("download");
  await page.locator(".billing-registry-toolbar .billing-xlsx-btn").click();
  const download = await downloadPromise;
  if (!download.suggestedFilename().endsWith(".xlsx")) throw new Error(`Bad filename: ${download.suggestedFilename()}`);
  if (calls.export !== 1) throw new Error(`Expected one export call, got ${JSON.stringify(calls)}`);
  await browser.close();
  console.log(JSON.stringify({ ok: true, calls }));
}

main().catch(error => { console.error(error); process.exit(1); });
