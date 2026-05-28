const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";
const sts = [
  { ST_NUMBER: "СТ-3701", ADDR: "Адрес 1", REGION: "Пермь", RAION: "Ленинский", PALLETS_COUNT: 2, WEIGHT_KG: 400, VOLUME_M3: 1.2, STDATE: "2026-05-25", DATE_LOAD: "2026-05-25", TRANSPORT_TYPE: "10", WARE_ID: 9201, VERIFY_PERC: 100, SUGAR: 0 },
  { ST_NUMBER: "СТ-3702", ADDR: "Адрес 2", REGION: "Пермь", RAION: "Свердловский", PALLETS_COUNT: 3, WEIGHT_KG: 600, VOLUME_M3: 1.8, STDATE: "2026-05-25", DATE_LOAD: "2026-05-25", TRANSPORT_TYPE: "10", WARE_ID: 9201, VERIFY_PERC: 100, SUGAR: 0 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(sts) }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByRole("button", { name: "По СТ" }).click();
  await page.getByText("СТ-3701").waitFor({ timeout: 10000 });
  const rowCheckboxes = page.locator(".dispatch-st-section tbody input[type='checkbox']");
  const headerCheckbox = page.locator(".dispatch-st-section thead input[type='checkbox']");
  await headerCheckbox.check();
  await page.getByText("2 выбр.").waitFor({ timeout: 5000 });
  if (!(await rowCheckboxes.nth(0).isChecked()) || !(await rowCheckboxes.nth(1).isChecked())) {
    throw new Error("Select-all did not check all visible ST rows");
  }
  await headerCheckbox.uncheck();
  if (await page.getByText("2 выбр.").count()) throw new Error("Selection bar still visible after deselect-all");
  const auto = page.getByLabel("Авто");
  if (!(await auto.isChecked())) throw new Error("Auto refresh must be enabled by default");
  await auto.uncheck();
  if (await auto.isChecked()) throw new Error("Auto refresh checkbox did not toggle off");
  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => { console.error(error); process.exit(1); });
