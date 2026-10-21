const fs = require('fs'), assert = require('assert');
const { chromium } = require('../../admin/wms_admin_frontend/node_modules/playwright');
const out = 'runtime/test-evidence/tradecase/2026-10-21/T10';
const pass = fs.readFileSync('AGENTS.md', 'utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const wh = '219023232';
const report = { checks: [], errors: [], http: [], writes: [], readonlyOverview: [] };
let browser;
(async () => {
  browser = await chromium.launch();
  for (const width of [1440, 390]) {
    const ctx = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 1000 } });
    const page = await ctx.newPage();
    page.on('pageerror', e => report.errors.push(String(e)));
    page.on('requestfinished', async req => { if (req.url().includes('/api/')) report.http.push({ method: req.method(), url: req.url(), ms: req.timing().responseEnd, status: (await req.response())?.status() }); });
    await page.route('**/api/**', route => {
      const req = route.request(), path = new URL(req.url()).pathname;
      if (req.method() === 'POST' && path === '/api/picking/shift-overview') {
        const body = req.postDataJSON();assert.equal(String(body.warehouse_id), wh);report.readonlyOverview.push(body);return route.continue();
      }
      if (!['GET', 'OPTIONS'].includes(req.method()) && !req.url().includes('/auth/')) {
        report.writes.push(req.method() + ' ' + req.url());return route.abort();
      }
      return route.continue();
    });
    await page.goto('http://127.0.0.1:3000/?' + new URLSearchParams({ page: 'tradecase', tc_wh: wh, tc_tab: 'STOCK' }));
    if (await page.locator('input[type=password]').count()) {
      await page.fill('input[autocomplete=username]', 'admin');await page.fill('input[type=password]', pass);await page.click('button[type=submit]');
    }
    await page.getByText('Итого на этой странице: 10 шт.', { exact: false }).waitFor({ timeout: 30000 });
    const shift = page.locator('[data-help-id="tradecase.shift"]');
    assert(await shift.getAttribute('title'));assert((await shift.getAttribute('data-help-url')).endsWith('#shift'));
    const snapshot = page.waitForResponse(r => r.request().method() === 'POST' && new URL(r.url()).pathname === '/api/picking/shift-overview', { timeout: 30000 }).catch(() => null);
    const began = Date.now();await shift.click();
    await page.locator('.rg[aria-label="Общий Гант ресурсов"]').waitFor({ timeout: 30000 });
    assert.equal(new URL(page.url()).searchParams.get('warehouse_id'), wh);
    assert.equal(new URL(page.url()).searchParams.get('workspace'), 'shift');
    assert.equal(await page.locator('[data-help-id="workspace.role.select"]').inputValue(), 'shift');
    assert.equal(await page.locator('.rg[aria-label="Общий Гант ресурсов"]').getAttribute('data-warehouse'), wh);
    assert.equal(await page.locator('input[type=password]').count(), 0);
    assert(!(await page.locator('.ops-brand').innerText()).toLowerCase().includes('retailcase'));
    const overviewResponse = await snapshot;assert(overviewResponse, "shift snapshot response missing");assert.equal(overviewResponse.status(), 200);
    const overview = await overviewResponse.json();assert.equal(overview.commands_executed, false);assert.equal(overview.stock_changed, false);
    assert.equal(String(overview.warehouse_id), wh);assert(overview.wave_ids.includes(601));
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'shift overflow ' + width);
    await page.screenshot({ path: out + '/shift-' + width + '.png', fullPage: true });
    report.checks.push({ width, test: 'same-session shift/Gantt and warehouse context', usefulScreenMs: Date.now() - began });
    await page.locator('[data-help-id="workspace.back"]').click();
    await page.locator('[data-help-id="tradecase.shift"]').waitFor();
    assert.equal(new URL(page.url()).searchParams.get('tc_wh'), wh);assert.equal(new URL(page.url()).searchParams.get('tc_tab'), 'STOCK');
    report.checks.push({ width, test: 'back retains original TRADECASE warehouse/tab without new login' });
    await page.locator('[data-help-id="tradecase.yard"]').click();
    await page.getByText('Двор и ворота · все доступные склады', { exact: true }).waitFor({ timeout: 30000 });
    await page.locator('.rg[aria-label="Общий Гант ресурсов"]').waitFor();
    assert.equal(new URL(page.url()).searchParams.get('workspace'), 'yard');
    assert.equal(await page.locator('.rg[aria-label="Общий Гант ресурсов"]').getAttribute('data-warehouse'), wh);
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'yard overflow ' + width);
    report.checks.push({ width, test: 'yard summary explicitly all permitted warehouses, Gantt retains selected warehouse' });
    await page.screenshot({ path: out + '/yard-' + width + '.png', fullPage: true });
    await page.locator('[data-help-id="workspace.back"]').click();await shift.waitFor();
    assert.equal(new URL(page.url()).searchParams.get('tc_wh'), wh);
    await ctx.close();
  }
  assert.deepEqual(report.errors, []);assert.deepEqual(report.writes, []);
  assert(report.readonlyOverview.length > 0, 'real shift snapshot was not read');
  report.status = 'PASS';fs.writeFileSync(out + '/shift-navigation-ui.json', JSON.stringify(report, null, 2));
  console.log(JSON.stringify({ status: report.status, checks: report.checks, writes: report.writes.length, readonlyOverview: report.readonlyOverview.length, http: report.http.length }));
  await browser.close();
})().catch(async e => { report.status = 'FAIL';report.error = String(e);fs.writeFileSync(out + '/shift-navigation-ui.json', JSON.stringify(report, null, 2));console.error(e);if(browser)await browser.close();process.exit(1); });
