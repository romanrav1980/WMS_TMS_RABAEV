const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const task = { ID: 2901, TRANSTYPE: "10", TRANSPORT: null, VODITEL_ID: null, VODITEL_NAME: null, TK_NAME: null, IS_OWN_DRIVER: 0, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 2, PALLET_COUNT: 8, TEMP_WEIGHT: 1800, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 100, UNREADY_COUNT: 0 };
const cluster = { RAION: "Север", ST_COUNT: 2, PALLET_COUNT: 8, WEIGHT_KG: 1800, VOLUME_M3: 7.5, STS: [
  { ST_NUMBER: "СТ-2901", ADDR: "Пермь, Северная 1", REGION: "Пермь", RAION: "Север", PALLETS_COUNT: 4, WEIGHT_KG: 900, VOLUME_M3: 3.7, STDATE: "2026-05-25", DATE_LOAD: "2026-05-25", TRANSTASK_ID: null, TRANSPORT_TYPE: "10", NEEDS_HYDRO_BOARD: 0, STOL: 0, PRIM1: null, NAPR: null, WARE_ID: 9201, VERIFY_PERC: 100, SUGAR: 0 },
  { ST_NUMBER: "СТ-2902", ADDR: "Пермь, Северная 2", REGION: "Пермь", RAION: "Север", PALLETS_COUNT: 4, WEIGHT_KG: 900, VOLUME_M3: 3.8, STDATE: "2026-05-25", DATE_LOAD: "2026-05-25", TRANSTASK_ID: null, TRANSPORT_TYPE: "10", NEEDS_HYDRO_BOARD: 0, STOL: 0, PRIM1: null, NAPR: null, WARE_ID: 9201, VERIFY_PERC: 100, SUGAR: 0 },
] };
const calls = { create: 0 };

async function installMocks(page) {
  await page.route("**/api/admin/transport/tasks/2901", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(task) }));
  await page.route("**/api/admin/transport/vehicles/available?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент 10т" }]) }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([]) }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([cluster]) }));
  await page.route("**/api/admin/transport/clusters/%D0%A1%D0%B5%D0%B2%D0%B5%D1%80/create-task", route => { calls.create += 1; route.fulfill({ contentType: "application/json", body: JSON.stringify({ task_id: 2901, raion: "Север", st_count: 2, warnings: [] }) }); });
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "По районам" }).click();
  await page.locator(".cluster-card-name", { hasText: "Север" }).waitFor({ timeout: 10000 });
  await page.locator(".cluster-card-create-btn").first().click();
  await page.getByText("Рейс из кластера").waitFor({ timeout: 5000 });
  await page.getByRole("button", { name: /Создать рейс/ }).click();
  await page.getByText("Рейс #2901", { exact: true }).waitFor({ timeout: 5000 });
  if (calls.create !== 1) throw new Error(`Expected one cluster create call, got ${JSON.stringify(calls)}`);
  await browser.close();
  console.log(JSON.stringify({ ok: true, calls }));
}

main().catch(error => { console.error(error); process.exit(1); });
