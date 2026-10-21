const fs = require('fs'), assert = require('assert');
const { chromium } = require('../../admin/wms_admin_frontend/node_modules/playwright');
const out = 'runtime/test-evidence/tradecase/2026-10-21/T06';
const pass = fs.readFileSync('AGENTS.md', 'utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const report = { checks: [], errors: [], writes: [], http: [] };let browser;
(async () => {
  browser = await chromium.launch();
  for (const width of [1440, 390]) {
    const ctx = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 1000 } });
    const page = await ctx.newPage();page.on('pageerror', e => report.errors.push(String(e)));
    await page.route('**/api/**', route => {
      const req = route.request();
      if (req.method() === 'POST' && req.url().includes('/picking/shift-overview')) return route.continue();
      if (!['GET', 'OPTIONS'].includes(req.method()) && !req.url().includes('/auth/')) { report.writes.push(req.url());return route.abort(); }
      return route.continue();
    });
    await page.goto('http://127.0.0.1:3000/?page=tradecase&tc_wh=220639789&tc_tab=STOCK');
    if (await page.locator('input[type=password]').count()) {
      await page.fill('input[autocomplete=username]', 'admin');await page.fill('input[type=password]', pass);await page.click('button[type=submit]');
    }
    await page.locator('[data-help-id="tradecase.shift"]').click();
    await page.locator('input[type=datetime-local]').fill('2026-10-21T20:15');
    const reply = page.waitForResponse(r => r.url().includes('/api/resources/timeline?') && r.url().includes('20%3A15') && r.status() === 200);
    await page.locator('input[type=number][max="168"]').fill('1');
    const native = await (await reply).json();
    assert(native.events.some(e => e.event_id === 'WAREHOUSE_TASK:1221'));
    const gantt = page.locator('.rg[aria-label="Общий Гант ресурсов"]');await gantt.waitFor();
    const warning = gantt.locator('.rg-tz-warn');assert.equal((await warning.innerText()).trim(), '· время UTC');
    assert((await warning.getAttribute('title')).includes('Часовой пояс склада'));
    const type = gantt.locator('[role=group][aria-label="Типы ресурсов"] button').filter({ hasText: 'Ричтраки' });
    if (await type.getAttribute('aria-pressed') !== 'true') await type.click();
    await gantt.locator('button.rg-bar').filter({ hasText: '1221' }).waitFor();
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await gantt.screenshot({ path: out+'/fullpal-gantt-'+width+'.png' });
    report.checks.push({ width, nativeTask: 1221, resource: 'EQUIPMENT:32', window: [native.start_at,native.finish_at], compactUtc: true });
    await ctx.close();
  }
  assert.deepEqual(report.errors, []);assert.deepEqual(report.writes, []);report.status = 'PASS';
  fs.writeFileSync(out+'/fullpal-gantt-ui.json', JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser.close();
})().catch(async e => {report.status='FAIL';report.error=String(e);fs.writeFileSync(out+'/fullpal-gantt-ui.json',JSON.stringify(report,null,2));console.error(e);if(browser)await browser.close();process.exit(1);});
