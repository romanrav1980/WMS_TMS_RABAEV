// Real read-only WMS route; depot GET and command responses are fixtures. No business writes reach API.
const fs = require('fs'), path = require('path'), assert = require('assert');
const ROOT = path.resolve(__dirname, '../..');
const { chromium } = require(path.join(ROOT, 'admin/wms_admin_frontend/node_modules/playwright'));
const OUT = path.join(ROOT, 'runtime/test-evidence/tradecase/2026-10-23/T09');
const cors = { 'access-control-allow-origin': '*' };
const report = { status: 'FAIL', checks: [], errors: [], businessWrites: [] };

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    for (const width of [1440, 390]) {
      const context = await browser.newContext({ viewport: { width, height: 1000 } });
      const p = await context.newPage();
      let posts = [], mode = 0, denied = false;
      p.on('pageerror', e => report.errors.push(e.message));
      await p.route('**/api/**', async route => {
        const req = route.request(), url = req.url(), m = req.method();
        if (url.includes('/warehouse-depots/220793322') && m === 'GET') return route.fulfill({ headers: cors, status: denied ? 403 : 200,
          json: denied ? { detail: { code: 'ACCESS_DENIED' } } : { version: 8, depot_address: 'Synthetic depot QA', configured: true } });
        if (m === 'POST' && (url.endsWith('/warehouse-depots') || url.endsWith('/route-inputs'))) {
          posts.push({ url, body: req.postData() });
          const body = JSON.parse(req.postData());
          if (url.endsWith('/warehouse-depots')) {
            mode++;
            return route.fulfill({ headers: cors, status: mode === 1 ? 503 : 200, json: mode === 1 ? { detail: { code: 'UNKNOWN' } }
              : { operation_id: mode === 2 ? 'WRONG.OPERATION' : body.operation_id, warehouse_id: 220793322, version: 9 } });
          }
          return route.fulfill({ headers: cors, json: { operation_id: body.operation_id, trip_id: 33665, version: 1 } });
        }
        if (!['GET', 'OPTIONS'].includes(m)) { report.businessWrites.push(m + ' ' + url); return route.abort(); }
        return route.continue();
      });
      async function open() {
        await p.goto('http://127.0.0.1:3000/?page=tradecase&tc_wh=220793322&tc_tab=TRIP');
        const login = p.locator('input[type=password]');
        await Promise.race([login.waitFor({ timeout: 30000 }), p.locator('.tc-body .tc-table tbody tr').first().waitFor({ timeout: 30000 })]);
        if (await login.count()) {
          await p.locator('input[autocomplete=username]').fill('admin'); await login.fill('admin123');
          await p.locator('button[type=submit]').click();
        }
        await p.locator('.tc-body .tc-table tbody tr', { hasText: 'R1.1168' }).first().getByRole('button', { name: 'Открыть', exact: true }).click();
        await p.locator("summary[data-help-id='tradecase.route.settings']").click({ timeout: 30000 });
      }
      await open();
      let section = p.locator("details:has(> summary[data-help-id='tradecase.route.settings'])");
      await section.locator('input').nth(0).fill('Synthetic route settings test');
      await section.locator('input').nth(1).fill('Synthetic depot requested');
      await section.locator("button[data-help-id='tradecase.route.depot.save']").click();
      await section.locator("button[data-help-id='tradecase.route.retry']").waitFor();
      await p.waitForFunction(() => !document.querySelector("button[data-help-id='tradecase.route.retry']")?.disabled);
      await open(); section = p.locator("details:has(> summary[data-help-id='tradecase.route.settings'])");
      const retry = section.locator("button[data-help-id='tradecase.route.retry']");
      await retry.click();
      await p.waitForFunction(() => !document.querySelector("button[data-help-id='tradecase.route.retry']")?.disabled);
      assert(await retry.count());
      await retry.click(); await retry.waitFor({ state: 'detached' });
      assert(posts.length === 3); assert(posts.every(x => x.body === posts[0].body));
      report.checks.push({ width, case: '503/reload, wrong receipt retained, exact body retried three times' });
      await section.locator('input').nth(0).fill('Synthetic duration test');
      await section.locator('input').nth(2).fill('15'); await section.locator('input').nth(3).fill('45');
      await section.locator('input').nth(4).fill('Synthetic dispatch estimate');
      await section.locator("button[data-help-id='tradecase.route.duration.save']").click();
      await p.waitForFunction(() => !document.querySelector("button[data-help-id='tradecase.route.refresh']")?.disabled);
      assert(posts.length === 4);
      const duration = JSON.parse(posts[3].body);
      assert(duration.drive_min === 15 && duration.drive_back_min === 45 && duration.trip_id === 33665 && !('kind' in duration));
      report.checks.push({ width, case: 'Duration uses existing command, current source hash and version' });
      denied = true; await section.locator("button[data-help-id='tradecase.route.refresh']").click();
      await section.locator('[role=alert]').waitFor();
      assert(!await section.locator("button[data-help-id='tradecase.route.depot.save']").isEnabled());
      assert(!await section.getByText('Synthetic depot QA', { exact: false }).count());
      const size = await p.evaluate(() => ({ viewport: innerWidth, document: document.documentElement.scrollWidth }));
      assert(size.document <= size.viewport + 1, JSON.stringify(size));
      await p.screenshot({ path: path.join(OUT, `route-settings-${width}.png`), fullPage: true });
      report.checks.push({ width, case: '403 clears depot data; save disabled; no horizontal overflow', size });
      await context.close();
    }
    assert(report.errors.length === 0, report.errors.join(';')); assert(report.businessWrites.length === 0);
    report.status = 'PASS';
  } finally {
    fs.mkdirSync(OUT, { recursive: true });
    fs.writeFileSync(path.join(OUT, 'route-settings-ui.json'), JSON.stringify(report, null, 2));
    await browser.close();
  }
  console.log(JSON.stringify(report));
})().catch(e => { console.error(e); process.exitCode = 1; });
