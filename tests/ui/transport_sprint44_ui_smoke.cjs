const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const APP_URL = process.env.WMS_UI_URL || pageUrl("transport");
const sts = [
  { ST_NUMBER: "СТ-4401", ADDR: "Пермь, Ленина 1", REGION: "Пермь", RAION: "Ленинский", PALLETS_COUNT: 2, WEIGHT_KG: 400, VOLUME_M3: 1.2, STDATE: "2026-05-25", DATE_LOAD: "2026-05-25", TRANSPORT_TYPE: "10", WARE_ID: 9201, VERIFY_PERC: 100, SUGAR: 0 },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Фургон" }]) }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(sts) }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(APP_URL);
  await page.getByRole("button", { name: "Заявки" }).click();
  await page.getByText("СТ-4401").waitFor({ timeout: 10000 });

  await page.locator(".dispatch-st-section tbody input[type='checkbox']").check();
  await page.getByText("1 выбр.").waitFor({ timeout: 5000 });
  await page.keyboard.press("Escape");
  if (await page.getByText("1 выбр.").count()) throw new Error("Escape did not clear selected STs");

  await page.getByRole("button", { name: "+ Создать маршрут" }).click();
  await page.locator(".dispatch-dialog-overlay").waitFor({ timeout: 5000 });
  await page.keyboard.press("Escape");
  if (await page.locator(".dispatch-dialog-overlay").count()) throw new Error("Escape did not close create dialog");

  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => { console.error(error); process.exit(1); });
