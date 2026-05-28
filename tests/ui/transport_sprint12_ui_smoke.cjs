const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=gantt";

const dayA = [
  {
    vehicle_id: 9201,
    vehicle_num: "В 415 ТТ 59",
    vehicle_type: "10т",
    operations: [
      { op_id: 1201, tt_id: 6201, operation_code: "DOCK_ASSIGN", ord: 1, duration_min: 10, plan_start: "2026-05-25 06:00", plan_end: "2026-05-25 06:10", fact_start: "2026-05-25 06:04", fact_end: "2026-05-25 06:14", delta_min: 4, note: null },
      { op_id: 1202, tt_id: 6201, operation_code: "LOADING", ord: 2, duration_min: 35, plan_start: "2026-05-25 06:10", plan_end: "2026-05-25 06:45", fact_start: null, fact_end: null, delta_min: null, note: null },
      { op_id: 1203, tt_id: 6201, operation_code: "DRIVE", ord: 3, duration_min: 70, plan_start: "2026-05-25 06:45", plan_end: "2026-05-25 07:55", fact_start: null, fact_end: null, delta_min: null, note: null },
      { op_id: 1204, tt_id: 6201, operation_code: "UNLOAD", ord: 4, duration_min: 45, plan_start: "2026-05-25 07:55", plan_end: "2026-05-25 08:40", fact_start: null, fact_end: null, delta_min: null, note: null },
    ],
  },
  {
    vehicle_id: 9202,
    vehicle_num: "Е 714 НО 59",
    vehicle_type: "15т",
    operations: [
      { op_id: 2201, tt_id: 6202, operation_code: "REST", ord: 1, duration_min: 30, plan_start: "2026-05-25 09:00", plan_end: "2026-05-25 09:30", fact_start: null, fact_end: null, delta_min: null, note: null },
      { op_id: 2202, tt_id: 6202, operation_code: "LOAD_RETURNS", ord: 2, duration_min: 20, plan_start: "2026-05-25 09:30", plan_end: "2026-05-25 09:50", fact_start: "2026-05-25 09:42", fact_end: "2026-05-25 10:08", delta_min: 18, note: null },
    ],
  },
];

async function installMocks(page, calls) {
  await page.route("**/api/admin/transport/vehicles/gantt?**", (route) => {
    calls.gantt += 1;
    const url = new URL(route.request().url());
    const date = url.searchParams.get("gantt_date");
    route.fulfill({ contentType: "application/json", body: JSON.stringify(date === "2026-05-26" ? [] : dayA) });
  });
  await page.route("**/api/admin/transport/plan-fact?**", (route) => {
    calls.planFact += 1;
    route.fulfill({ contentType: "application/json", body: "[]" });
  });
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const calls = { gantt: 0, planFact: 0 };
  await installMocks(page, calls);

  await page.goto(APP_URL);
  await page.getByRole("heading", { name: "Диаграмма Ганта" }).waitFor({ timeout: 10000 });
  await page.locator(".gantt-date-input").fill("2026-05-25");

  await page.locator(".gantt-veh-num", { hasText: "В 415 ТТ 59" }).waitFor({ timeout: 5000 });
  await page.locator(".gantt-veh-num", { hasText: "Е 714 НО 59" }).waitFor({ timeout: 5000 });
  await page.locator(".gantt-legend-item", { hasText: "Склад" }).waitFor({ timeout: 5000 });
  await page.locator(".gantt-legend-item", { hasText: "Переезд" }).waitFor({ timeout: 5000 });
  await page.locator(".gantt-legend-item", { hasText: "Разгрузка" }).waitFor({ timeout: 5000 });
  await page.locator(".gantt-legend-item", { hasText: "Возвраты" }).waitFor({ timeout: 5000 });
  await page.getByText("Всего машин").waitFor({ timeout: 5000 });
  await page.getByText("Фактические отклонения").waitFor({ timeout: 5000 });
  await page.locator(".gantt-panel-delta", { hasText: "+18 мин" }).waitFor({ timeout: 5000 });

  const driveBlock = page.locator("svg rect[fill='#52C41A']").first();
  await driveBlock.hover();
  await page.locator(".gantt-tooltip", { hasText: "Переезд" }).waitFor({ timeout: 5000 });

  await page.locator(".gantt-veh-filter").fill("Е 714");
  await page.locator(".gantt-veh-num", { hasText: "Е 714 НО 59" }).waitFor({ timeout: 5000 });
  await page.locator(".gantt-veh-num", { hasText: "В 415 ТТ 59" }).waitFor({ state: "hidden", timeout: 5000 });

  await page.locator(".gantt-veh-filter").fill("");
  await page.locator(".gantt-date-input").fill("2026-05-26");
  await page.locator(".gantt-empty", { hasText: "Нет рейсов" }).waitFor({ timeout: 5000 });
  await page.locator(".gantt-date-input").fill("2026-05-25");
  await page.locator(".gantt-veh-num", { hasText: "В 415 ТТ 59" }).waitFor({ timeout: 5000 });

  if (calls.gantt < 3) {
    throw new Error(`Gantt endpoint was not refreshed enough: ${JSON.stringify(calls)}`);
  }

  await browser.close();
  console.log(JSON.stringify({ ok: true, calls }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
