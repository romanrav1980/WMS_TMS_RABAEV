const fs = require('fs'), assert = require('assert');
const { chromium } = require('../../admin/wms_admin_frontend/node_modules/playwright');
const out = 'runtime/test-evidence/tradecase/2026-10-21/T06';
const fixture = JSON.parse(fs.readFileSync(out + '/factory-case.json', 'utf8'));
const pass = fs.readFileSync('AGENTS.md', 'utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const report = { checks: [], errors: [], http: [], writes: [] };
let browser;
(async () => {
  browser = await chromium.launch();
  for (const width of [1440, 390]) {
    const ctx = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 1000 } });
    const page = await ctx.newPage();
    page.on('pageerror', e => report.errors.push(String(e)));
    page.on('requestfinished', r => { if (r.url().includes('/api/tradecase/')) report.http.push({ method: r.method(), url: r.url(), ms: r.timing().responseEnd }); });
    await page.route('**/api/**', route => {
      const req = route.request();
      if (!['GET', 'OPTIONS'].includes(req.method()) && !req.url().includes('/auth/')) {
        report.writes.push(req.method() + ' ' + req.url());return route.abort();
      }
      return route.continue();
    });
    const started = Date.now();
    await page.goto('http://127.0.0.1:3000/?' + new URLSearchParams({ page: 'tradecase', tc_wh: String(fixture.warehouse_id), tc_tab: 'STOCK' }));
    if (await page.locator('input[type=password]').count()) {
      await page.fill('input[autocomplete=username]', 'admin');await page.fill('input[type=password]', pass);await page.click('button[type=submit]');
    }
    await page.getByText('Итого на этой странице: 10 шт.', { exact: false }).waitFor({ timeout: 30000 });
    await page.getByText('приём включён', { exact: true }).waitFor();
    // RETURN retains the identity of the returned 2-piece lot; it does not merge it into the remaining 5.
    const mobile = width <= 600;
    const rows = page.locator(mobile ? '.tc-stock-cards article' : '.tc-stock-table tbody tr');assert.equal(await rows.count(), 3);
    const quantities = [];
    for (let i = 0; i < 3; i++) {
      const quantity = mobile ? rows.nth(i).locator('header strong') : rows.nth(i).locator('td').nth(6);
      assert(await quantity.isVisible());quantities.push((await quantity.innerText()).trim());
      const reserve = mobile ? rows.nth(i).locator('header span') : rows.nth(i).locator('td').nth(7);
      assert.equal((await reserve.innerText()).trim(), mobile ? 'Резерв: 0 шт.' : '0 шт.');
    }
    assert.deepEqual(quantities.sort(), ['2 шт.', '3 шт.', '5 шт.']);
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    assert(await page.locator('a[href$="#stock"]').count());
    report.checks.push({ width, usefulScreenMs: Date.now() - started, result: 'live 3+5+returned2 pieces, reserve0, total10, help, no page overflow' });
    await page.screenshot({ path: out + '/factory-stock-' + width + '.png', fullPage: true });
    await ctx.close();
  }
  assert.deepEqual(report.errors, []);assert.deepEqual(report.writes, []);report.status = 'PASS';
  fs.writeFileSync(out + '/factory-stock-ui.json', JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report));await browser.close();
})().catch(async e => { report.status = 'FAIL';report.error = String(e);fs.writeFileSync(out + '/factory-stock-ui.json', JSON.stringify(report, null, 2));console.error(e);if(browser)await browser.close();process.exit(1); });
