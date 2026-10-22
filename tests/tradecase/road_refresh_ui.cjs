// Real route reads, intercepted command responses; no business writes.
const fs = require('fs'), path = require('path'), assert = require('assert');
const ROOT = path.resolve(__dirname, '../..'), OUT = path.join(ROOT, 'runtime/test-evidence/tradecase/2026-10-23/T09');
const { chromium } = require(path.join(ROOT, 'admin/wms_admin_frontend/node_modules/playwright'));
const report = { status: 'FAIL', checks: [], errors: [], writes: [] };
(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    for (const width of [1440, 390]) {
      const context = await browser.newContext({ viewport: { width, height: 1000 } });
      const p = await context.newPage(); let loggedIn = false, requests = [];
      p.on('pageerror', e => report.errors.push(e.message));
      await p.route('**/api/**', async route => {
        const req = route.request();
        if (req.method() === 'POST' && req.url().endsWith('/road-refreshes')) {
          requests.push(req.postData()); const body = JSON.parse(req.postData());
          return route.fulfill({ headers: { 'access-control-allow-origin': '*' }, status: requests.length === 1 ? 503 : 200,
            json: requests.length === 1 ? { detail: { code: 'ROAD_PROVIDER_UNAVAILABLE' } }
              : { operation_id: requests.length === 2 ? 'WRONG' : body.operation_id, trip_id: body.trip_id, updated_legs: 2, provider: 'osrm' } });
        }
        if (!['GET', 'OPTIONS'].includes(req.method())) { report.writes.push(req.method() + ' ' + req.url()); return route.abort(); }
        return route.continue();
      });
      async function open() {
        await p.goto('http://127.0.0.1:3000/?page=tradecase&tc_wh=220793322&tc_tab=TRIP&tc_open=R1.1168');
        {
          const password = p.locator('input[type=password]');
          await Promise.race([password.waitFor({ timeout: 30000 }), p.locator("summary[data-help-id='tradecase.route.settings']").waitFor({ timeout: 30000 })]);
          if (await password.isVisible()) {
            await p.locator('input[autocomplete=username]').fill('admin'); await password.fill('admin123');
            await p.locator('button[type=submit]').click();
          }
          loggedIn = true;
        }
        await p.locator("summary[data-help-id='tradecase.route.settings']").click();
      }
      await open();
      const refresh = p.locator("button[data-help-id='tradecase.route.road.refresh']");
      assert(await refresh.getAttribute('title')); assert(await refresh.getAttribute('data-help-url'));
      await refresh.click();
      const retry = p.locator("button[data-help-id='tradecase.route.road.retry']");
      await retry.waitFor();
      await p.waitForFunction(() => !document.querySelector("button[data-help-id='tradecase.route.road.retry']")?.disabled);
      await open(); await retry.click();
      await p.waitForFunction(() => !document.querySelector("button[data-help-id='tradecase.route.road.retry']")?.disabled);
      assert(await retry.count()); await retry.click(); await retry.waitFor({ state: 'detached' });
      assert(requests.length === 3 && requests.every(value => value === requests[0]));
      const size = await p.evaluate(() => ({ viewport: innerWidth, document: document.documentElement.scrollWidth }));
      assert(size.document <= size.viewport + 1);
      await p.screenshot({ path: path.join(OUT, `road-refresh-${width}.png`), fullPage: true });
      report.checks.push({ width, case: '503/reload/wrong receipt preserves exact request; valid receipt clears it; help and no overflow', size });
      await context.close();
    }
    assert(report.errors.length === 0, report.errors.join(';')); assert(report.writes.length === 0);
    report.status = 'PASS';
  } finally { fs.writeFileSync(path.join(OUT, 'road-refresh-ui.json'), JSON.stringify(report, null, 2)); await browser.close(); }
  console.log(JSON.stringify(report));
})().catch(e => { console.error(e); process.exitCode = 1; });
