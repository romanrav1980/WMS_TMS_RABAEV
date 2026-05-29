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

const clusters = [
  { RAION: "Север", ST_COUNT: 1, PALLET_COUNT: 5, WEIGHT_KG: 300, VOLUME_M3: 2.5, STS: [{ ST_NUMBER: "CL-ST-001", ADDR: "Первый", REGION: "Пермь", RAION: "Север", ORD: 1, TRANSPORT_TYPE: "Тент", WARE_ID: 9201, PALLETS_COUNT: 5, WEIGHT_KG: 300, VOLUME_M3: 2.5, VERIFY_PERC: 100 }] },
  { RAION: "Юг", ST_COUNT: 1, PALLET_COUNT: 8, WEIGHT_KG: 500, VOLUME_M3: 3.0, STS: [{ ST_NUMBER: "CL-ST-002", ADDR: "Второй", REGION: "Пермь", RAION: "Юг", ORD: 2, TRANSPORT_TYPE: "Реф", WARE_ID: 9202, PALLETS_COUNT: 8, WEIGHT_KG: 500, VOLUME_M3: 3.0, VERIFY_PERC: 75 }] },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(clusters) }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.addInitScript(() => {
    localStorage.setItem("tms_activeTab", "tasks");
    localStorage.setItem("tms_viewMode", "clusters");
  });
  await page.goto(APP_URL);
  await page.locator(".cluster-sidebar").waitFor({ timeout: 10000 });
  if (await page.locator(".dispatch-st-section", { hasText: "CL-ST-001" }).count() !== 0) {
    throw new Error("Cluster rows should be collapsed initially");
  }

  await page.getByTitle("Развернуть все районы").click();
  await page.locator(".dispatch-st-section", { hasText: "CL-ST-001" }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-st-section", { hasText: "CL-ST-002" }).waitFor({ timeout: 5000 });
  if ((await page.locator(".cluster-card-active").count()) !== 2) {
    throw new Error("All cluster sidebar cards should be active after expand-all");
  }

  await page.getByTitle("Свернуть все районы").click();
  if (await page.locator(".dispatch-st-section", { hasText: "CL-ST-001" }).count() !== 0) {
    throw new Error("Cluster rows should be hidden after collapse-all");
  }
  if ((await page.locator(".cluster-card-active").count()) !== 0) {
    throw new Error("Sidebar cards should be inactive after collapse-all");
  }

  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
