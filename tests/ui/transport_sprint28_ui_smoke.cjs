const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const tasks = [{ ID: 2801, TRANSTYPE: "10", TRANSPORT: "В 481 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Рейсы-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Отгружен", ST_COUNT: 3, PALLET_COUNT: 12, TEMP_WEIGHT: 2400, PRICE: 12500, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 }];
const xlsxBytes = Buffer.from("UEsDBAoAAAAAA", "base64");
const calls = { export: 0 };

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(tasks) }));
  await page.route("**/api/admin/transport/tasks/export.xlsx?**", route => {
    calls.export += 1;
    route.fulfill({ contentType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers: { "Content-Disposition": 'attachment; filename="transport_tasks_2026-05-25.xlsx"' }, body: xlsxBytes });
  });
}

async function main() {
  const browser = await chromium.launch();
  const context = await browser.newContext({ acceptDownloads: true, viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Маршруты" }).click();
  await page.getByText("2801").waitFor({ timeout: 10000 });
  const downloadPromise = page.waitForEvent("download");
  await page.locator(".routes-xlsx-btn").click();
  const download = await downloadPromise;
  if (!download.suggestedFilename().endsWith(".xlsx")) throw new Error(`Bad filename: ${download.suggestedFilename()}`);
  if (calls.export !== 1) throw new Error(`Expected one export call, got ${JSON.stringify(calls)}`);
  await browser.close();
  console.log(JSON.stringify({ ok: true, calls }));
}

main().catch(error => { console.error(error); process.exit(1); });
