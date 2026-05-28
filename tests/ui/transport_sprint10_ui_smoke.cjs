const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=planner";

async function installMocks(page, calls) {
  await page.route("**/api/admin/transport/planner/orders?**", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/routing/status", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify({ provider: "haversine", provider_available: true, total_addresses: 0, geocoded_count: 0, ungeocoded_count: 0 }) }));
  await page.route("**/api/admin/transport/types", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/planner/history?**", (route) => {
    calls.history += 1;
    route.fulfill({
      contentType: "application/json",
      body: JSON.stringify([
        { plan_id: 1001, plan_date: "2026-05-24", solver: "clarke-wright", score: 72.4, routes: 3, total_km: 240, fleet_utilization_pct: 86.5, tw_violations: 0, applied: true },
        { plan_id: 1002, plan_date: "2026-05-25", solver: "dbscan-cluster", score: 69.1, routes: 4, total_km: 310, fleet_utilization_pct: 81.2, tw_violations: 1, applied: false },
      ]),
    });
  });
  await page.route("**/api/admin/transport/planner/demand-forecast?**", (route) => {
    calls.forecast += 1;
    route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        target_date: "2026-05-25",
        day_of_week: 0,
        forecast_sts: 77,
        confidence: "high",
        samples: 8,
        sample_counts: [70, 74, 76, 77, 79, 80, 75, 78],
        stddev: 3.1,
      }),
    });
  });
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const calls = { history: 0, forecast: 0 };
  await installMocks(page, calls);

  await page.goto(APP_URL);
  await page.getByRole("heading", { name: "Планировщик маршрутов" }).waitFor({ timeout: 10000 });
  await page.getByRole("button", { name: "Аналитика" }).click();

  await page.getByText("История планов").waitFor({ timeout: 5000 });
  await page.getByText("Планов применено").waitFor({ timeout: 5000 });
  await page.getByText("86.5%").waitFor({ timeout: 5000 });
  await page.locator(".analytics-solver-badge", { hasText: "clarke-wright" }).waitFor({ timeout: 5000 });
  await page.getByText("Настройки целевой функции").waitFor({ timeout: 5000 });
  await page.getByText("Прогноз спроса").waitFor({ timeout: 5000 });
  await page.getByText("77").waitFor({ timeout: 5000 });
  await page.getByText("Уверенность: высокая").waitFor({ timeout: 5000 });

  if (calls.history < 1 || calls.forecast < 1) {
    throw new Error(`Analytics endpoints were not called: ${JSON.stringify(calls)}`);
  }

  await browser.close();
  console.log(JSON.stringify({ ok: true, historyCalls: calls.history, forecastCalls: calls.forecast }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
