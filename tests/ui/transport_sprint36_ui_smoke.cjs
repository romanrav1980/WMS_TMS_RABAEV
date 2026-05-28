const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const task = { ID: 3601, TRANSTYPE: "10", TRANSPORT: "В 501 ТТ 59", VODITEL_ID: 501, VODITEL_NAME: "Иванов И.И.", TK_NAME: "ООО Bulk-Транс", IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 3, PALLET_COUNT: 9, TEMP_WEIGHT: 1800, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
let taskSts = [
  { ST_NUMBER: "СТ-3601", ADDR: "Адрес 1", REGION: "Пермь", RAION: "Ленинский", PALLETS_COUNT: 3, WEIGHT_KG: 600, VOLUME_M3: 2, ORD: 1, WARE_ID: 9201, VERIFY_PERC: 100 },
  { ST_NUMBER: "СТ-3602", ADDR: "Адрес 2", REGION: "Пермь", RAION: "Ленинский", PALLETS_COUNT: 3, WEIGHT_KG: 600, VOLUME_M3: 2, ORD: 2, WARE_ID: 9201, VERIFY_PERC: 100 },
  { ST_NUMBER: "СТ-3603", ADDR: "Адрес 3", REGION: "Пермь", RAION: "Ленинский", PALLETS_COUNT: 3, WEIGHT_KG: 600, VOLUME_M3: 2, ORD: 3, WARE_ID: 9201, VERIFY_PERC: 100 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([task]) }));
  await page.route("**/api/admin/transport/tasks/3601/sts", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(taskSts) }));
  await page.route("**/api/admin/transport/tasks/3601/sts/*", route => {
    const st = decodeURIComponent(route.request().url().split("/").pop());
    taskSts = taskSts.filter(row => row.ST_NUMBER !== st);
    return route.fulfill({ contentType: "application/json", body: JSON.stringify({ unassigned: true }) });
  });
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  page.on("dialog", dialog => dialog.accept());
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByText("#3601").waitFor({ timeout: 10000 });
  await page.locator("tr[data-taskid='3601']").click();
  await page.locator(".dispatch-trip-sts-wrap tbody input[type='checkbox']").nth(0).check();
  await page.locator(".dispatch-trip-sts-wrap tbody input[type='checkbox']").nth(1).check();
  await page.getByText("2 СТ выбрано").waitFor({ timeout: 5000 });
  await page.getByRole("button", { name: "Снять выбранные" }).click();
  await page.getByText("2 СТ снято с рейса #3601").waitFor({ timeout: 5000 });
  await page.getByText("СТ-3603").waitFor({ timeout: 5000 });
  if (await page.getByText("СТ-3601").count()) throw new Error("СТ-3601 still visible after bulk unassign");
  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => { console.error(error); process.exit(1); });
