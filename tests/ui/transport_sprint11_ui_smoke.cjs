const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=gantt";

const gantt = [
  {
    vehicle_id: 9201,
    vehicle_num: "В 415 ТТ 59",
    vehicle_type: "10т",
    operations: [
      {
        op_id: 111,
        tt_id: 6101,
        operation_code: "DOCK_ASSIGN",
        ord: 1,
        duration_min: 10,
        plan_start: "2026-05-25 06:00",
        plan_end: "2026-05-25 06:10",
        fact_start: null,
        fact_end: null,
        delta_min: null,
        note: null,
      },
      {
        op_id: 112,
        tt_id: 6101,
        operation_code: "LOADING",
        ord: 2,
        duration_min: 35,
        plan_start: "2026-05-25 06:10",
        plan_end: "2026-05-25 06:45",
        fact_start: "2026-05-25 06:15",
        fact_end: "2026-05-25 06:55",
        delta_min: 10,
        note: null,
      },
      {
        op_id: 113,
        tt_id: 6101,
        operation_code: "DRIVE",
        ord: 3,
        duration_min: 60,
        plan_start: "2026-05-25 06:45",
        plan_end: "2026-05-25 07:45",
        fact_start: null,
        fact_end: null,
        delta_min: null,
        note: null,
      },
    ],
  },
];

const planFact = [
  {
    tt_id: 6101,
    vehicle: "В 415 ТТ 59",
    shipment_date: "2026-05-25",
    status: "В рейсе",
    total_delta_min: 10,
    rest_violations: 0,
    operations: gantt[0].operations,
  },
];

async function installMocks(page, calls) {
  await page.route("**/api/admin/transport/vehicles/gantt?**", (route) => {
    calls.gantt += 1;
    route.fulfill({ contentType: "application/json", body: JSON.stringify(gantt) });
  });
  await page.route("**/api/admin/transport/plan-fact?**", (route) => {
    calls.planFact += 1;
    route.fulfill({ contentType: "application/json", body: JSON.stringify(planFact) });
  });
  await page.route("**/api/admin/transport/operations/111/fact", (route) => {
    calls.factPatch += 1;
    route.fulfill({ contentType: "application/json", body: JSON.stringify({ updated: true }) });
  });
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const calls = { gantt: 0, planFact: 0, factPatch: 0 };
  await installMocks(page, calls);

  await page.goto(APP_URL);
  await page.getByRole("heading", { name: "Диаграмма Ганта" }).waitFor({ timeout: 10000 });
  await page.locator(".gantt-date-input").fill("2026-05-25");
  await page.locator(".gantt-veh-num", { hasText: "В 415 ТТ 59" }).waitFor({ timeout: 5000 });
  await page.locator("svg rect[fill='#4A90D9']").first().waitFor({ timeout: 5000 });

  const firstOp = page.locator("svg rect[fill='#4A90D9']").first();
  await firstOp.click();
  await page.getByText("Рейс #6101").waitFor({ timeout: 5000 });
  await page.getByText("Цепочка операций").waitFor({ timeout: 5000 });
  await page.getByRole("button", { name: "Закрыть" }).click();

  await firstOp.click({ button: "right" });
  await page.getByText("Отметить факт").waitFor({ timeout: 5000 });
  await page.getByText("Отметить факт").click();
  await page.getByText("Отметить факт · Ворота").waitFor({ timeout: 5000 });
  await page.locator("input[type='datetime-local']").first().fill("2026-05-25T06:05");
  await page.locator("input[type='datetime-local']").nth(1).fill("2026-05-25T06:17");
  await page.getByRole("button", { name: "Сохранить" }).click();
  await page.getByRole("button", { name: "Аналитика" }).click();
  await page.getByText("План-факт анализ").waitFor({ timeout: 5000 });
  await page.locator(".gantt-pf-delta-total", { hasText: "+10 мин" }).waitFor({ timeout: 5000 });
  await page.getByRole("button", { name: /Экспорт CSV/ }).waitFor({ timeout: 5000 });

  if (calls.gantt < 2 || calls.planFact < 1 || calls.factPatch !== 1) {
    throw new Error(`Unexpected API calls: ${JSON.stringify(calls)}`);
  }

  await browser.close();
  console.log(JSON.stringify({ ok: true, calls }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
