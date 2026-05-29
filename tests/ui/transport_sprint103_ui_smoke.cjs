/**
 * transport_sprint103_ui_smoke.cjs — Sprint 103-104: DriverMobilePage
 *
 * Проверяет:
 * 1. ?page=driver открывает экран ввода driver_id
 * 2. После ввода ID отображается список рейсов
 * 3. Карточки рейсов содержат num_plat, st_count
 * 4. Клик на рейс открывает вкладку Операции
 * 5. Кнопки «Начать» и «Готово» видны для разных статусов
 */

const { chromium } = require("playwright");

const DRIVER_URL = (process.env.WMS_UI_URL || "http://localhost:3000") + "?page=driver";

const MOCK_TRIPS = [
  {
    task_id: 4501,
    shipment_date: "2026-05-30",
    num_plat: "Е123АВ77",
    transport_type: "10",
    condition: "Новый",
    note: "Тестовый рейс",
    price: 7500,
    st_count: 5,
    weight_kg: 2300,
  },
];

const MOCK_OPS = [
  { op_id: 1, operation_code: "DOCK_ASSIGN", ord: 1, plan_start: "2026-05-30T08:00:00", plan_end: "2026-05-30T08:15:00", fact_start: "", fact_end: "", note: "", status: "pending" },
  { op_id: 2, operation_code: "LOADING",     ord: 3, plan_start: "2026-05-30T08:25:00", plan_end: "2026-05-30T09:10:00", fact_start: "2026-05-30T08:30:00", fact_end: "", note: "", status: "in_progress" },
  { op_id: 3, operation_code: "DEPART",      ord: 6, plan_start: "2026-05-30T09:20:00", plan_end: "2026-05-30T09:20:00", fact_start: "2026-05-30T09:18:00", fact_end: "2026-05-30T09:18:00", note: "", status: "done" },
];

async function installMocks(page) {
  await page.route("**/api/driver/trips?**", r =>
    r.fulfill({ contentType: "application/json", body: JSON.stringify(MOCK_TRIPS) }));
  await page.route("**/api/driver/trips/4501/sts?**", r =>
    r.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/driver/trips/4501/ops?**", r =>
    r.fulfill({ contentType: "application/json", body: JSON.stringify(MOCK_OPS) }));
  await page.route("**/api/driver/ops/*/start?**", r =>
    r.fulfill({ contentType: "application/json", body: '{"status":"in_progress"}' }));
  await page.route("**/api/driver/ops/*/done?**", r =>
    r.fulfill({ contentType: "application/json", body: '{"status":"done"}' }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } }); // iPhone size

  await page.goto(DRIVER_URL);

  // Login screen
  const loginCard = page.locator(".driver-login-card");
  await loginCard.waitFor({ timeout: 8000 });
  const logo = page.locator(".driver-login-logo");
  await logo.waitFor();
  console.log("✓ Driver login screen displayed");

  // Enter driver ID
  const idInput = loginCard.locator("input");
  await idInput.fill("9201");
  await loginCard.locator("button").click();

  await installMocks(page);

  // Should show trips list
  const tripCard = page.locator(".driver-trip-card").first();
  await tripCard.waitFor({ timeout: 8000 });
  await page.getByText("Е123АВ77").waitFor({ timeout: 5000 });
  await page.getByText("5 адресов").waitFor();
  console.log("✓ Trip list displays mock trips");

  // Date navigation
  const todayBtn = page.locator(".driver-today-btn");
  await todayBtn.waitFor();
  const nextBtn = page.locator(".driver-date-row button").last();
  await nextBtn.click();
  console.log("✓ Date navigation controls present");

  // Click on trip to see ops
  await tripCard.click();
  const opsTab = page.locator(".driver-tab").filter({ hasText: /операции/i });
  await opsTab.waitFor({ timeout: 5000 });
  await opsTab.click();

  // Operations list
  const opCards = page.locator(".driver-op-card");
  await opCards.first().waitFor({ timeout: 5000 });
  const opCount = await opCards.count();
  if (opCount < 3) throw new Error(`Expected ≥3 operations, got ${opCount}`);
  console.log(`✓ ${opCount} operation cards visible`);

  // pending op has "Начать" button
  const startBtn = page.locator(".driver-op-start");
  await startBtn.waitFor();
  console.log("✓ 'Начать' button visible for pending operation");

  // in_progress op has "Готово" button
  const doneBtn = page.locator(".driver-op-done").first();
  await doneBtn.waitFor();
  console.log("✓ 'Готово' button visible for in-progress operation");

  // done op has checkmark
  const checkmark = page.locator(".driver-op-check").first();
  await checkmark.waitFor();
  console.log("✓ ✓ checkmark visible for done operation");

  await browser.close();
  console.log("Sprint 103-104 UI smoke: PASSED");
}

main().catch(err => { console.error("Sprint 103-104 UI smoke: FAILED", err.message); process.exit(1); });
