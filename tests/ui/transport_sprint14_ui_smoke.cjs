const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=gantt";

const operations = [
  { op_id: 1401, tt_id: 6401, operation_code: "LOADING", ord: 1, duration_min: 45, plan_start: "2026-05-25 06:00", plan_end: "2026-05-25 06:45", fact_start: "2026-05-25 06:05", fact_end: "2026-05-25 07:12", delta_min: 27, note: null },
  { op_id: 1402, tt_id: 6401, operation_code: "REST", ord: 2, duration_min: 30, plan_start: "2026-05-25 07:15", plan_end: "2026-05-25 07:45", fact_start: "2026-05-25 07:50", fact_end: "2026-05-25 08:05", delta_min: 20, note: null },
  { op_id: 1403, tt_id: 6401, operation_code: "UNLOAD", ord: 3, duration_min: 30, plan_start: "2026-05-25 08:10", plan_end: "2026-05-25 08:40", fact_start: null, fact_end: null, delta_min: null, note: null },
];

async function installMocks(page, calls) {
  await page.route("**/api/admin/transport/vehicles/gantt?**", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/plan-fact?**", (route) => {
    calls.planFact += 1;
    route.fulfill({
      contentType: "application/json",
      body: JSON.stringify([
        {
          tt_id: 6401,
          vehicle: "В 415 ТТ 59",
          shipment_date: "2026-05-25",
          status: "В рейсе",
          total_delta_min: 47,
          rest_violations: 2,
          operations,
        },
      ]),
    });
  });
}

async function main() {
  const browser = await chromium.launch();
  const context = await browser.newContext({ acceptDownloads: true, viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  const calls = { planFact: 0 };
  await installMocks(page, calls);

  await page.goto(APP_URL);
  await page.getByRole("heading", { name: "Диаграмма Ганта" }).waitFor({ timeout: 10000 });
  await page.getByRole("button", { name: "Аналитика" }).click();
  await page.getByText("План-факт анализ").waitFor({ timeout: 5000 });
  await page.getByText("Рейс #6401").waitFor({ timeout: 5000 });
  await page.getByText("В 415 ТТ 59").waitFor({ timeout: 5000 });
  await page.locator(".gantt-pf-violations", { hasText: "2 нар. отдыха" }).waitFor({ timeout: 5000 });
  await page.locator(".gantt-pf-delta-total", { hasText: "+47 мин" }).waitFor({ timeout: 5000 });
  await page.locator(".gantt-pf-table td", { hasText: "Погрузка" }).waitFor({ timeout: 5000 });
  await page.locator(".gantt-pf-bar").first().waitFor({ timeout: 5000 });

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: /Экспорт CSV/ }).click();
  const download = await downloadPromise;
  if (!download.suggestedFilename().includes("plan-fact")) {
    throw new Error(`Unexpected CSV filename: ${download.suggestedFilename()}`);
  }

  if (calls.planFact < 1) {
    throw new Error("Plan-fact endpoint was not called");
  }

  await browser.close();
  console.log(JSON.stringify({ ok: true, calls }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
