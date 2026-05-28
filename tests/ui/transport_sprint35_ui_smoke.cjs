const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";

const clusters = [
  { RAION: "Ленинский", ST_COUNT: 2, PALLET_COUNT: 8, WEIGHT_KG: 1200, VOLUME_M3: 4.2, STS: [] },
];

async function installMocks(page) {
  let createUrl = "";
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify([{ ID: 1, NUM: "В 501 ТТ 59", MARKA: "MAN", PALLETS: 20 }]),
  }));
  await page.route("**/api/admin/transport/vehicles/available?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент" }]),
  }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks/3501", route => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify({ ID: 3501, TRANSTYPE: "10", TRANSPORT: null, SHIPMENT_DATE: "2026-05-25T00:00:00", CONDITION: "Новый", ST_COUNT: 2, PALLET_COUNT: 8, TEMP_WEIGHT: 1200, PAY_ORDER_ID: null, DELETED: 0 }),
  }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(clusters) }));
  await page.route("**/api/admin/transport/clusters/*/create-task", route => {
    createUrl = route.request().url();
    return route.fulfill({ contentType: "application/json", body: JSON.stringify({ task_id: 3501, raion: "Ленинский", st_count: 2, warnings: [] }) });
  });
  return () => createUrl;
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const getCreateUrl = await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByRole("button", { name: "По районам" }).click();
  await page.locator(".cluster-card").filter({ hasText: "Ленинский" }).getByRole("button", { name: "⚡ Рейс" }).click();
  await page.getByText("Рейс из кластера «Ленинский»").waitFor({ timeout: 5000 });
  await page.getByRole("button", { name: "Создать рейс (2 СТ)" }).click();
  await page.getByText("Рейс #3501 создан из кластера").waitFor({ timeout: 5000 });
  if (!decodeURIComponent(getCreateUrl()).includes("/clusters/Ленинский/create-task")) {
    throw new Error(`create-task URL did not include target raion: ${getCreateUrl()}`);
  }
  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => { console.error(error); process.exit(1); });
