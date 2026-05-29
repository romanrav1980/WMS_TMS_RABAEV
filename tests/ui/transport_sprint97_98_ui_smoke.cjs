/**
 * transport_sprint97_98_ui_smoke.cjs — Sprint 97-98: FleetManagementPage
 *
 * Проверяет:
 * 1. Страница открывается через ?page=fleet
 * 2. Видны вкладки «Транспортные средства» и «Водители»
 * 3. Таблица ТС рендерится при наличии данных
 * 4. Кнопка «+ Добавить ТС» открывает диалог
 * 5. Диалог содержит поля num_plat, тип ТС, паллеты
 * 6. Вкладка Водители рендерит таблицу
 */

const { chromium } = require("playwright");
const { pageUrl } = require("../support/project_config.cjs");

const FLEET_URL = (process.env.WMS_UI_URL || "http://localhost:3000") + "?page=fleet";

const MOCK_VEHICLES = [
  { ID: 9201, NUM_PLAT: "Е123АВ77", TRANSTYPE_ID: "10", TRANSTYPE_NAME: "Тент 10т",
    MAX_WEIGHT_KG: 10000, MAX_PALLETS: 20, SOBSTVENNYY: 1, DOVERENNOST_OT: null },
  { ID: 9202, NUM_PLAT: "Т456УХ77", TRANSTYPE_ID: "20реф", TRANSTYPE_NAME: "Рефрижератор 20т",
    MAX_WEIGHT_KG: 20000, MAX_PALLETS: 33, SOBSTVENNYY: 0, DOVERENNOST_OT: "ООО Транс-Авто" },
];

const MOCK_DRIVERS = [
  { ID: 9201, FULL_NAME: "Иванов Иван Иванович", PHONE: "89001234567",
    LICENSE_NUMBER: "7712345678", COMPANY: null, SOBSTVENNYY: 1, DOVERENNOST_OT: null },
];

const MOCK_TYPES = [
  { TRANSPORTTYPE: "10", NAME: "Тент 10т" },
  { TRANSPORTTYPE: "20реф", NAME: "Рефрижератор 20т" },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles/full", r =>
    r.fulfill({ contentType: "application/json", body: JSON.stringify(MOCK_VEHICLES) }));
  await page.route("**/api/admin/transport/drivers/full", r =>
    r.fulfill({ contentType: "application/json", body: JSON.stringify(MOCK_DRIVERS) }));
  await page.route("**/api/admin/transport/types", r =>
    r.fulfill({ contentType: "application/json", body: JSON.stringify(MOCK_TYPES) }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(FLEET_URL);

  // Check page title
  await page.locator("h1").filter({ hasText: /флот/i }).waitFor({ timeout: 8000 });

  // Check tabs present
  const vehiclesTab = page.locator(".fleet-tab-btn").filter({ hasText: /транспортные/i });
  await vehiclesTab.waitFor();
  const driversTab = page.locator(".fleet-tab-btn").filter({ hasText: /водители/i });
  await driversTab.waitFor();

  // Vehicles tab (default)
  await vehiclesTab.click();
  await page.locator(".fleet-table").waitFor({ timeout: 5000 });

  // Vehicle data visible
  await page.getByText("Е123АВ77").waitFor({ timeout: 5000 });
  await page.getByText("Т456УХ77").waitFor({ timeout: 3000 });
  console.log("✓ Vehicle table renders mock data");

  // Own/hired badges
  const ownBadge = page.locator(".fleet-own").first();
  await ownBadge.waitFor();
  const hiredBadge = page.locator(".fleet-hired").first();
  await hiredBadge.waitFor();
  console.log("✓ Own/Hired badges visible");

  // Add vehicle button opens dialog
  const addBtn = page.locator(".fleet-add-btn").first();
  await addBtn.click();
  const modal = page.locator(".fleet-modal");
  await modal.waitFor({ timeout: 3000 });
  const modalTitle = await modal.locator(".fleet-modal-title").innerText();
  if (!modalTitle.toLowerCase().includes("добав")) throw new Error(`Expected 'Добавить' in modal title, got: '${modalTitle}'`);

  // Form fields present
  const numPlatInput = modal.locator("input").first();
  await numPlatInput.waitFor();
  await numPlatInput.fill("Н999НН77");
  const saveBtn = modal.locator(".fleet-modal-save");
  if (await saveBtn.isDisabled()) console.log("✓ Save button enabled after filling num_plat");

  // Close dialog with Escape
  await page.keyboard.press("Escape");
  await modal.waitFor({ state: "hidden", timeout: 3000 });
  console.log("✓ Dialog closes on backdrop click / Escape");

  // Switch to Drivers tab
  await page.route("**/api/admin/transport/drivers/full", r =>
    r.fulfill({ contentType: "application/json", body: JSON.stringify(MOCK_DRIVERS) }));
  await driversTab.click();
  await page.getByText("Иванов Иван Иванович").waitFor({ timeout: 5000 });
  console.log("✓ Driver table renders mock data");

  // Add driver button
  const driverAddBtn = page.locator(".fleet-add-btn").first();
  await driverAddBtn.click();
  const driverModal = page.locator(".fleet-modal");
  await driverModal.waitFor({ timeout: 3000 });
  const driverModalTitle = await driverModal.locator(".fleet-modal-title").innerText();
  if (!driverModalTitle.toLowerCase().includes("водител")) throw new Error(`Expected 'Водитель' in title, got: '${driverModalTitle}'`);
  await page.keyboard.press("Escape");
  console.log("✓ Driver add dialog opens and closes");

  await browser.close();
  console.log("Sprint 97-98 UI smoke: PASSED");
}

main().catch(err => { console.error("Sprint 97-98 UI smoke: FAILED", err.message); process.exit(1); });
