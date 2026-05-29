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

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function yesterdayIso() {
  const d = new Date();
  d.setDate(d.getDate() - 1);
  return d.toISOString().slice(0, 10);
}

async function installMocks(page, calls) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => {
    calls.availableSts.push(new URL(route.request().url()).searchParams.get("stdate") || "");
    route.fulfill({ contentType: "application/json", body: "[]" });
  });
  await page.route("**/api/admin/transport/tasks?**", route => {
    route.fulfill({ contentType: "application/json", body: "[]" });
  });
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function waitForCall(calls, expected, label) {
  const deadline = Date.now() + 5000;
  while (Date.now() < deadline) {
    if (calls.includes(expected)) return;
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error(`${label} endpoint was not reloaded for ${expected}; saw ${JSON.stringify(calls)}`);
}

async function expectToolbarDate(toolbar, expected) {
  const value = await toolbar.locator("input[type='date']").inputValue();
  assert(value === expected, `expected toolbar date ${expected}, got ${value}`);
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const calls = { tasks: [], availableSts: [] };
  const today = todayIso();
  const yesterday = yesterdayIso();
  page.on("request", request => {
    const url = request.url();
    if (url.includes("/api/admin/transport/tasks?")) {
      calls.tasks.push(new URL(url).searchParams.get("shipment_date") || "");
    }
  });

  await installMocks(page, calls);
  await page.addInitScript(({ yesterday }) => {
    localStorage.setItem("tms_filterDate", yesterday);
    localStorage.setItem("tms_stDate", yesterday);
    localStorage.setItem("tms_routeShipDate", yesterday);
    localStorage.setItem("tms_activeTab", "tasks");
  }, { yesterday });

  await page.goto(APP_URL);
  await page.locator(".dispatch-shell").waitFor({ timeout: 10000 });

  const tasksToolbar = page.locator(".dispatch-trips-section .dispatch-trips-toolbar").first();
  await expectToolbarDate(tasksToolbar, yesterday);
  await tasksToolbar.getByRole("button", { name: "Сегодня" }).click();
  await expectToolbarDate(tasksToolbar, today);
  assert(await tasksToolbar.getByRole("button", { name: "Сегодня" }).count() === 0, "tasks Today button should disappear after reset");
  await waitForCall(calls.tasks, today, "tasks");

  await page.getByRole("button", { name: "Маршруты" }).click();
  const routesToolbar = page.locator(".dispatch-trips-toolbar").filter({ hasText: "Маршруты за" });
  await expectToolbarDate(routesToolbar, yesterday);
  await routesToolbar.getByRole("button", { name: "Сегодня" }).click();
  await expectToolbarDate(routesToolbar, today);
  assert(await routesToolbar.getByRole("button", { name: "Сегодня" }).count() === 0, "routes Today button should disappear after reset");
  await waitForCall(calls.tasks, today, "routes");

  await browser.close();
  console.log(JSON.stringify({ ok: true, today, tasksReloaded: calls.tasks.includes(today) }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
