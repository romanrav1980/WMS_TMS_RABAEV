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

const rows = [
  { ST_NUMBER: "FP-ST-001", ADDR: "Пермь, Ленина 1", REGION: "Пермь", RAION: "Центр", ORD: 1, TRANSPORT_TYPE: "Тент", WARE_ID: 9201, NAPR: "Пермь", PALLETS_COUNT: 5, WEIGHT_KG: 300, VOLUME_M3: 2, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 50 },
  { ST_NUMBER: "FP-ST-002", ADDR: "Чусовой, Мира 2", REGION: "Чусовой", RAION: "Север", ORD: 2, TRANSPORT_TYPE: "Реф", WARE_ID: 9202, NAPR: "Чусовой", PALLETS_COUNT: 8, WEIGHT_KG: 500, VOLUME_M3: 3, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: null },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "Тент", NAME: "Тент" }]) }));
  await page.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(rows) }));
  await page.route("**/api/admin/transport/tasks?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.addInitScript(() => {
    localStorage.setItem("tms_activeTab", "tasks");
    localStorage.setItem("tms_viewMode", "flat");
    if (!sessionStorage.getItem("sprint53_initialized")) {
      localStorage.removeItem("tms_fpCollapsed");
      sessionStorage.setItem("sprint53_initialized", "1");
    }
  });
  await page.goto(APP_URL);
  await page.getByText("FP-ST-001").waitFor({ timeout: 10000 });

  const panel = page.locator(".dispatch-right-panel").first();
  const collapseButton = panel.locator(".dispatch-fp-collapse-btn");
  await panel.locator(".dispatch-fp-title", { hasText: "Фильтры" }).waitFor({ timeout: 5000 });
  if (await panel.locator(".dispatch-fp-input").count() === 0) throw new Error("Expanded filter controls are missing");

  await collapseButton.click();
  await panel.evaluate(node => {
    if (!node.classList.contains("dispatch-fp-collapsed")) throw new Error("Panel did not collapse");
    const width = Math.round(node.getBoundingClientRect().width);
    if (width > 45) throw new Error(`Collapsed panel width too large: ${width}`);
  });
  if (await panel.locator(".dispatch-fp-input").count() !== 0) throw new Error("Collapsed panel still shows filter inputs");
  if ((await collapseButton.innerText()).trim() !== "›") throw new Error("Collapsed icon is not right arrow");
  if (await page.evaluate(() => localStorage.getItem("tms_fpCollapsed")) !== "1") throw new Error("Collapsed state was not persisted");

  await collapseButton.click();
  await panel.locator(".dispatch-fp-title", { hasText: "Фильтры" }).waitFor({ timeout: 5000 });
  if ((await collapseButton.innerText()).trim() !== "‹") throw new Error("Expanded icon is not left arrow");
  if (await page.evaluate(() => localStorage.getItem("tms_fpCollapsed")) !== "0") throw new Error("Expanded state was not persisted");

  await panel.locator("input.dispatch-fp-input[placeholder='Адрес / регион']").fill("Пермь");
  await panel.locator(".dispatch-fp-badge", { hasText: "1" }).waitFor({ timeout: 5000 });
  await collapseButton.click();
  await panel.locator(".dispatch-fp-badge-alone", { hasText: "1" }).waitFor({ timeout: 5000 });

  await page.reload();
  await panel.locator(".dispatch-fp-collapse-btn").waitFor({ timeout: 10000 });
  await panel.evaluate(node => {
    if (!node.classList.contains("dispatch-fp-collapsed")) throw new Error("Panel did not restore collapsed state");
  });

  await browser.close();
  console.log(JSON.stringify({ ok: true }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
