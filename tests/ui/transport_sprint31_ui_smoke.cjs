const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";

const clusters = [
  { RAION: "Север", ST_COUNT: 3, PALLET_COUNT: 12, WEIGHT_KG: 1200, VOLUME_M3: 5.5, STS: [] },
  { RAION: "Юг", ST_COUNT: 2, PALLET_COUNT: 7, WEIGHT_KG: 730, VOLUME_M3: 2.8, STS: [] },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify([{ ID: 1, NUM: "В 501 ТТ 59", MARKA: "MAN", PALLETS: 20 }]),
  }));
  await page.route("**/api/admin/transport/vehicles/available?**", route => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify([{ vehicle_num: "В 501 ТТ 59", status: "green", detail: "свободна", free_at: null }]),
  }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент" }]),
  }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(clusters) }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByRole("button", { name: "По районам" }).click();
  await page.locator(".cluster-sidebar").waitFor({ timeout: 10000 });
  await page.getByText("2 р-нов · 5 СТ · 19 пал").waitFor({ timeout: 5000 });
  await page.locator(".cluster-card").filter({ hasText: "Север" }).click();
  await page.locator(".cluster-card-active").filter({ hasText: "Север" }).waitFor({ timeout: 5000 });
  await page.locator(".cluster-card").filter({ hasText: "Север" }).getByRole("button", { name: "⚡ Рейс" }).click();
  await page.getByText("Рейс из кластера «Север»").waitFor({ timeout: 5000 });
  await page.locator(".cluster-dialog-summary").filter({ hasText: "3 СТ · 12 пал · 1200 кг" }).waitFor({ timeout: 5000 });
  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => { console.error(error); process.exit(1); });
