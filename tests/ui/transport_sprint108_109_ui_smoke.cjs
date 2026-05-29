/**
 * transport_sprint108_109_ui_smoke.cjs — Sprint 108-109: KpiDashboardPage
 *
 * Проверяет:
 * 1. ?page=kpi открывает KPI дашборд
 * 2. Вкладки «Операционные метрики» и «Финансы»
 * 3. Summary-карточки рендерятся с данными
 * 4. Bar chart отображается
 * 5. Таблица регионов видна
 * 6. Биллинг-вкладка: карточки и горизонтальные бары
 */

const { chromium } = require("playwright");

const KPI_URL = (process.env.WMS_UI_URL || "http://localhost:3000") + "?page=kpi";

const MOCK_SUMMARY = {
  trips_total: 142,
  trips_closed: 128,
  vehicles_used: 12,
  pallets: 1840,
  weight_kg: 422000,
  avg_pallets_per_trip: 12.9,
};

const MOCK_FLEET_DAYS = [
  { day: "2026-05-01", trips_total: 5, trips_closed: 5, pallets: 60, weight_kg: 14000 },
  { day: "2026-05-02", trips_total: 7, trips_closed: 6, pallets: 88, weight_kg: 20000 },
  { day: "2026-05-03", trips_total: 4, trips_closed: 4, pallets: 52, weight_kg: 12000 },
];

const MOCK_REGIONS = [
  { region: "Пермь", trips: 55, pallets: 680, weight_kg: 156000 },
  { region: "Лысьва", trips: 22, pallets: 280, weight_kg: 64000 },
  { region: "Чусовой", trips: 18, pallets: 220, weight_kg: 50000 },
];

const MOCK_BILLING = {
  orders_total: 14,
  orders_paid: 8,
  orders_closed: 3,
  total_amount: 325450,
  paid_amount: 198000,
  unpaid_amount: 127450,
};

const MOCK_BILLING_COMPANIES = [
  { company: "ООО Ромашка", orders: 6, amount: 189000, paid_amount: 125000 },
  { company: "ИП Иванов",   orders: 4, amount: 86450,  paid_amount: 73000  },
];

async function installMocks(page) {
  await page.route("**/api/admin/transport/kpi/summary?**", r =>
    r.fulfill({ contentType: "application/json", body: JSON.stringify(MOCK_SUMMARY) }));
  await page.route("**/api/admin/transport/kpi/fleet?**", r =>
    r.fulfill({ contentType: "application/json", body: JSON.stringify(MOCK_FLEET_DAYS) }));
  await page.route("**/api/admin/transport/kpi/regions?**", r =>
    r.fulfill({ contentType: "application/json", body: JSON.stringify(MOCK_REGIONS) }));
  await page.route("**/api/admin/transport/kpi/billing?**", r =>
    r.fulfill({ contentType: "application/json", body: JSON.stringify(MOCK_BILLING) }));
  await page.route("**/api/admin/transport/kpi/billing/by-company?**", r =>
    r.fulfill({ contentType: "application/json", body: JSON.stringify(MOCK_BILLING_COMPANIES) }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(KPI_URL);

  // Page header
  await page.locator("h1").filter({ hasText: /kpi/i }).waitFor({ timeout: 8000 });

  // Tabs
  const opsTab = page.locator(".kpi-tab-btn").filter({ hasText: /операцион/i });
  await opsTab.waitFor();
  const billingTab = page.locator(".kpi-tab-btn").filter({ hasText: /финанс/i });
  await billingTab.waitFor();
  console.log("✓ KPI tabs visible");

  // Default: ops tab
  await opsTab.click();

  // Summary cards
  await page.getByText("142").waitFor({ timeout: 6000 }); // trips_total
  await page.getByText("1 840").waitFor(); // pallets formatted
  console.log("✓ Summary cards show trips=142, pallets=1840");

  // Bar chart
  const barChart = page.locator(".kpi-bar-chart");
  await barChart.waitFor({ timeout: 5000 });
  const bars = barChart.locator(".kpi-bar");
  const barCount = await bars.count();
  if (barCount < 3) throw new Error(`Expected ≥3 bars, got ${barCount}`);
  console.log(`✓ Bar chart has ${barCount} bars`);

  // Regions table
  const regTable = page.locator(".kpi-table");
  await regTable.waitFor();
  await page.getByText("Пермь").waitFor({ timeout: 3000 });
  await page.getByText("Лысьва").waitFor();
  console.log("✓ Regions table: Пермь, Лысьва visible");

  // Date range inputs
  const dateInputs = page.locator(".kpi-date-range input");
  const dateCount = await dateInputs.count();
  if (dateCount < 2) throw new Error(`Expected 2 date inputs, got ${dateCount}`);
  console.log("✓ Date range inputs present");

  // Billing tab
  await billingTab.click();
  await page.waitForTimeout(500);

  // Billing summary cards
  await page.getByText("325 450 ₽").waitFor({ timeout: 6000 }).catch(() =>
    page.getByText(/325/).waitFor({ timeout: 3000 }));
  console.log("✓ Billing total amount visible");

  // Company bars
  const hbarRows = page.locator(".kpi-hbar-row");
  await hbarRows.first().waitFor({ timeout: 5000 });
  const hbarCount = await hbarRows.count();
  if (hbarCount < 2) throw new Error(`Expected ≥2 company bars, got ${hbarCount}`);
  await page.getByText("ООО Ромашка").waitFor();
  console.log(`✓ ${hbarCount} company horizontal bars visible`);

  await browser.close();
  console.log("Sprint 108-109 UI smoke: PASSED");
}

main().catch(err => { console.error("Sprint 108-109 UI smoke: FAILED", err.message); process.exit(1); });
