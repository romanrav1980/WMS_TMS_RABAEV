const path = require("path");
const { createRequire } = require("module");
const { pageUrl } = require("../support/project_config.cjs");

function requirePlaywright() {
  try {
    return require("playwright");
  } catch {
    return createRequire(path.resolve("admin/wms_admin_frontend/package.json"))("playwright");
  }
}

const { chromium } = requirePlaywright();
const APP_URL = process.env.WMS_UI_URL || pageUrl("transport");

const tasks = [
  { ID: 5701, TRANSTYPE: "Тент", TRANSPORT: "Е715ТТ", VODITEL_ID: 1, VODITEL_NAME: "Иванов И.И.", DOCK: "Д-3", SHIPMENT_DATE: "2026-05-25", CONDITION: "Новый", ST_COUNT: 0, PALLET_COUNT: 0, TEMP_WEIGHT: 0, PRICE: 0, PAY_ORDER_ID: null, DELETED: 0, READY_PERC: 0, UNREADY_COUNT: 0 },
];

let postedBody = null;
let taskSts = [];

async function installMocks(target) {
  await target.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await target.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await target.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await target.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await target.route(/\/api\/admin\/transport\/tasks(?:\?|$)/, route => route.fulfill({ contentType: "application/json", body: JSON.stringify(tasks) }));
  await target.route(/tasks\/5701\/sts/, async route => {
    if (route.request().method() === "POST") {
      postedBody = JSON.parse(route.request().postData() || "{}");
      taskSts = [{ ST_NUMBER: postedBody.st_numbers[0], ADDR: "Быстро добавленная СТ", REGION: "Пермь", RAION: "Центр", ORD: 1, TRANSPORT_TYPE: "Тент", WARE_ID: 9201, PALLETS_COUNT: 1, WEIGHT_KG: 10, VOLUME_M3: 0.5, VERIFY_PERC: 100 }];
      await route.fulfill({ contentType: "application/json", body: JSON.stringify({ assigned: 1, warnings: [] }) });
      return;
    }
    await route.fulfill({ contentType: "application/json", body: JSON.stringify(taskSts) });
  });
  await target.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function main() {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  await installMocks(context);
  const page = await context.newPage();
  await page.addInitScript(() => {
    localStorage.setItem("tms_activeTab", "tasks");
    localStorage.setItem("tms_viewMode", "flat");
  });
  await page.goto(APP_URL);
  await page.locator(".dispatch-trips-table-wrap tbody tr", { hasText: "5701" }).click();
  await page.locator(".dispatch-trip-detail-section", { hasText: "Рейс #5701" }).waitFor({ timeout: 5000 });
  const input = page.locator(".dispatch-quick-add-input");
  const button = page.locator(".dispatch-quick-add-btn");
  if (!(await button.isDisabled())) throw new Error("Quick-add should be disabled for empty input");

  await input.fill("  QUICK-ST-001  ");
  await input.press("Enter");
  await page.locator(".dispatch-toast", { hasText: "СТ QUICK-ST-001 добавлен в рейс #5701" }).waitFor({ timeout: 5000 });
  if (JSON.stringify(postedBody) !== JSON.stringify({ st_numbers: ["QUICK-ST-001"] })) {
    throw new Error(`Unexpected quick-add payload: ${JSON.stringify(postedBody)}`);
  }
  if ((await input.inputValue()) !== "") throw new Error("Quick-add input was not cleared");
  await page.locator(".dispatch-trip-sts-wrap .dispatch-gc-stnum", { hasText: "QUICK-ST-001" }).waitFor({ timeout: 5000 });

  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
