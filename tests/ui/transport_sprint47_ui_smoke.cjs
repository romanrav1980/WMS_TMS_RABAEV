const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const APP_URL = process.env.WMS_UI_URL || pageUrl("transport");

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.addInitScript(() => {
    localStorage.setItem("tms_filterDate", "2026-06-05");
    localStorage.setItem("tms_routeShipDate", "2026-06-10");
    localStorage.setItem("tms_viewMode", "clusters");
    localStorage.setItem("tms_activeTab", "routes");
  });
  await page.goto(APP_URL);
  await page.locator(".dispatch-tab.active", { hasText: "Маршруты" }).waitFor({ timeout: 10000 });
  const routesToolbar = page.locator(".dispatch-trips-toolbar").filter({ hasText: "Маршруты за" });
  if (await routesToolbar.locator("input[type='date']").inputValue() !== "2026-06-10") {
    throw new Error("routeShipDate was not restored from localStorage");
  }
  await page.getByRole("button", { name: "Заявки" }).click();
  const tasksToolbar = page.locator(".dispatch-trips-section .dispatch-trips-toolbar").first();
  if (await tasksToolbar.locator("input[type='date']").inputValue() !== "2026-06-05") {
    throw new Error("filterDate was not restored from localStorage");
  }
  await page.getByRole("button", { name: "По районам" }).waitFor({ timeout: 5000 });
  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => { console.error(error); process.exit(1); });
