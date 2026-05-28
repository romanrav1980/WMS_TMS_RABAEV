const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const APP_URL = process.env.WMS_UI_URL || pageUrl("transport");
const sts = [
  { ST_NUMBER: "СТ-3901", ADDR: "Пермь, Ленина 1", REGION: "Пермь", RAION: "Ленинский", PALLETS_COUNT: 2, WEIGHT_KG: 400, VOLUME_M3: 1.2, STDATE: "2026-05-25", DATE_LOAD: "2026-05-25", TRANSPORT_TYPE: "10", WARE_ID: 9201, VERIFY_PERC: 100, SUGAR: 0 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Фургон" }]) }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(sts) }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByText("СТ-3901").waitFor({ timeout: 10000 });

  const filterPanel = page.locator(".dispatch-right-panel");
  const addrInput = filterPanel.locator("input.dispatch-fp-input[placeholder='Адрес / регион']");
  await addrInput.fill("Пермь");
  await filterPanel.locator(".dispatch-fp-badge", { hasText: "1" }).waitFor({ timeout: 5000 });
  await filterPanel.getByRole("button", { name: "× Сбросить" }).waitFor({ timeout: 5000 });

  await filterPanel.getByRole("button", { name: "× Сбросить" }).click();
  if (await addrInput.inputValue() !== "") throw new Error("Reset did not clear address filter");
  if (await filterPanel.locator(".dispatch-fp-badge").count()) throw new Error("Badge still visible after reset");
  if (await filterPanel.getByRole("button", { name: "× Сбросить" }).count()) throw new Error("Reset button still visible after reset");

  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => { console.error(error); process.exit(1); });
