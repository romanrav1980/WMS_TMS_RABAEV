const fs = require('fs'), assert = require('assert');
const { chromium } = require('../../admin/wms_admin_frontend/node_modules/playwright');
const out = 'runtime/test-evidence/tradecase/2026-10-21/T09';
const pass = fs.readFileSync('AGENTS.md', 'utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const proof = JSON.parse(fs.readFileSync(out + '/allocation-199585691.json', 'utf8'));
const report = { checks: [], errors: [], http: [], businessWrites: [] };let browser;
(async () => {
  browser = await chromium.launch();
  for (const width of [1440, 390]) {
    const ctx = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 1000 } });
    const page = await ctx.newPage();page.on('pageerror', e => report.errors.push(String(e)));
    page.on('requestfinished', async req => { if (req.url().includes('/api/')) report.http.push({ method: req.method(), url: req.url(), ms: req.timing().responseEnd, status: (await req.response())?.status() }); });
    await page.route('**/api/**', route => {
      const req = route.request();
      if (req.method() === 'POST' && new URL(req.url()).pathname.endsWith('/topup-preview')) return route.continue();
      if (!['GET', 'OPTIONS'].includes(req.method()) && !req.url().includes('/auth/')) { report.businessWrites.push(req.url());return route.abort(); }
      return route.continue();
    });
    const began = Date.now();
    await page.goto('http://127.0.0.1:3000/?' + new URLSearchParams({ page: 'tradecase', tc_wh: String(proof.warehouse_id), tc_tab: 'TRIP', tc_open: 'R1' }));
    if (await page.locator('input[type=password]').count()) { await page.fill('input[autocomplete=username]', 'admin');await page.fill('input[type=password]', pass);await page.click('button[type=submit]'); }
    const panel = page.locator('section[aria-label="Распределение места под добивку"]');await panel.waitFor({ timeout: 30000 });
    const calculate = panel.locator('[data-help-id="tradecase.topup.calculate"]');assert(await calculate.isDisabled());
    for (const id of ['N.A', 'N.B']) { await panel.locator('[data-help-id="tradecase.topup.need.id"]').fill(id);await panel.locator('[data-help-id="tradecase.topup.add"]').click(); }
    await panel.locator('[data-help-id="tradecase.topup.age"]').fill('60');await calculate.click();
    const result = panel.locator('[aria-label="Результат распределения"]');await result.waitFor({ timeout: 30000 });
    assert((await result.innerText()).includes('Всего предложено: 60 кор.'));
    assert.deepEqual(await result.locator('article dd').allTextContents(), ['40 кор.', '40 кор.', '0 кор.', '30 кор.', '20 кор.', '10 кор.']);
    report.checks.push({ width, test: 'live40A+20B, uncovered10B, no order/reserve', usefulScreenMs: Date.now() - began });
    assert((await panel.locator('a[href$="#topup"]').getAttribute('href')).includes('tradecase-documents.html'));
    for (const el of await panel.locator('button').all()) assert(await el.getAttribute('title'));
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'page overflow ' + width);
    await panel.screenshot({ path: out + '/topup-' + width + '.png' });
    await panel.locator('[data-help-id="tradecase.topup.up"]').nth(1).click();assert.equal(await result.count(), 0);
    await calculate.click();await result.waitFor();assert.deepEqual(await result.locator('article dd').allTextContents(), ['30 кор.', '30 кор.', '0 кор.', '40 кор.', '30 кор.', '10 кор.']);
    report.checks.push({ width, test: 'priority change clears stale result; live30B+30A' });
    await page.route('**/topup-preview', r => r.fulfill({ status: 403, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ detail: { code: 'TRADECASE_ACCESS_DENIED' } }) }));
    await calculate.click();await panel.getByRole('alert').filter({ hasText: 'Нет доступа' }).waitFor();assert.equal(await result.count(), 0);
    report.checks.push({ width, test: 'denied request clears result; plain error/help/no overflow' });
    await ctx.close();
  }
  assert.deepEqual(report.errors, []);assert.deepEqual(report.businessWrites, []);report.status = 'PASS';
  fs.writeFileSync(out + '/topup-ui.json', JSON.stringify(report, null, 2));console.log(JSON.stringify({ status: report.status, checks: report.checks }));await browser.close();
})().catch(async e => { report.status = 'FAIL';report.error = String(e);fs.writeFileSync(out + '/topup-ui.json', JSON.stringify(report, null, 2));console.error(e);if (browser) await browser.close();process.exit(1); });
