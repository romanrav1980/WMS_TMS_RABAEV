const fs = require('fs'), assert = require('assert');
const { chromium } = require('../../admin/wms_admin_frontend/node_modules/playwright');
const out = 'runtime/test-evidence/tradecase/2026-10-21/T02';
const files = fs.readdirSync(out).filter(x => /^deferred-.*\.json$/.test(x)).sort((a,b) => fs.statSync(out+'/'+a).mtimeMs - fs.statSync(out+'/'+b).mtimeMs);
const fixture = files.map(x => JSON.parse(fs.readFileSync(out + '/' + x))).filter(x => x.status === 'PASS').at(-1);
const pass = fs.readFileSync('AGENTS.md', 'utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const report = { checks: [], errors: [], http: [], liveWrites: [], fixtureWrites: [] };
let browser;
(async () => {
  assert(fixture, 'native proof missing');
  const wh = fixture.warehouse_id, event = fixture.event_id;
  const api = `/api/tradecase/warehouses/${wh}/messages/${encodeURIComponent(event)}`;
  const auth = 'Basic ' + Buffer.from('admin:' + pass).toString('base64');
  const response = await fetch('http://127.0.0.1:8088' + api, { headers: { Authorization: auth } });
  assert.equal(response.status, 200);
  const actual = await response.json();
  assert.equal(actual.result.status, 'WAITING');assert.equal(actual.current_result.status, 'ACCEPTED');
  browser = await chromium.launch();
  for (const width of [1440, 390]) {
    const ctx = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 1000 } });
    const page = await ctx.newPage();
    page.on('pageerror', e => report.errors.push(String(e)));
    page.on('response', r => { if (r.url().includes('/api/tradecase/')) report.http.push({ status: r.status(), url: r.url(), ms: r.request().timing().responseEnd }); });
    await page.route('**/api/**', async route => {
      const req = route.request();
      if (!['GET', 'OPTIONS'].includes(req.method()) && !req.url().includes('/auth/')) {
        report.liveWrites.push(req.method() + ' ' + req.url());return route.abort();
      }
      return route.continue();
    });
    const url = 'http://127.0.0.1:3000/?' + new URLSearchParams({ page: 'tradecase', tc_wh: String(wh), tc_tab: 'MESSAGES', tc_open: event });
    const began = Date.now();
    await page.goto(url);
    if (await page.locator('input[type=password]').count()) {
      await page.fill('input[autocomplete=username]', 'admin');await page.fill('input[type=password]', pass);await page.click('button[type=submit]');
    }
    const card = page.locator('section.tc-card');
    await card.getByText('Первоначальная квитанция', { exact: true }).waitFor({ timeout: 30000 });
    assert((await card.innerText()).includes('Принято основание'));
    assert((await card.innerText()).includes('Ожидает справочник'));
    report.checks.push({ width, test: 'live initial WAITING + final ACCEPTED', usefulScreenMs: Date.now() - began });
    let state = 'WAITING', mode = 'lost', posts = 0;
    const current = () => ({ ...actual, current_result: state === 'WAITING' ? { ...actual.result, code: 'MASTER_MISSING:SKU:A' } : actual.current_result });
    await page.route('**/api/tradecase/**', async route => {
      const req = route.request(), path = new URL(req.url()).pathname;
      if (req.method() === 'POST' && path.endsWith('/retry')) {
        posts++;report.fixtureWrites.push({ width, path, body: req.postData() });
        assert.equal(decodeURIComponent(path), decodeURIComponent(api + '/retry'));
        if (mode === 'lost') return route.abort();
        if (mode === 'denied') return route.fulfill({ status: 403, json: { detail: { code: 'TRADECASE_ACCESS_DENIED' } } });
        state = 'ACCEPTED';return route.fulfill({ json: actual.current_result });
      }
      if (req.method() === 'GET' && decodeURIComponent(path) === decodeURIComponent(api)) {
        if (mode === 'denied') return route.fulfill({ status: 403, json: { detail: { code: 'TRADECASE_ACCESS_DENIED' } } });
        return route.fulfill({ json: current() });
      }
      return route.fallback();
    });
    await page.getByRole('button', { name: 'Обновить', exact: true }).click();
    const button = card.locator('[data-help-id="tradecase.message.retry"]');
    await button.waitFor();
    assert(await button.getAttribute('title'));assert((await button.getAttribute('data-help-url')).endsWith('#deferred'));
    await button.click();await card.getByRole('alert').waitFor();
    assert((await card.innerText()).includes('Сервер не подтвердил результат'));
    await page.screenshot({ path: out + '/deferred-lost-' + width + '.png', fullPage: true });
    await page.reload();
    if (await page.locator('input[type=password]').count()) {
      await page.fill('input[autocomplete=username]', 'admin');await page.fill('input[type=password]', pass);await page.click('button[type=submit]');
    }
    await button.waitFor({ timeout: 30000 });
    mode = 'accept';await button.click();
    await card.getByText('Принято основание', { exact: true }).waitFor();
    assert.equal(await button.count(), 0);assert.equal(posts, 2);
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await page.screenshot({ path: out + '/deferred-resolved-' + width + '.png', fullPage: true });
    report.checks.push({ width, test: 'WAITING reason/help, lost reply/reload/exact endpoint retry, final state, no overflow' });
    state = 'WAITING';mode = 'lost';
    await page.getByRole('button', { name: 'Обновить', exact: true }).click();await button.waitFor();
    mode = 'denied';await button.click();
    await page.getByText('Нет права просмотра СНС/BLC на этом складе.', { exact: true }).waitFor();
    assert.equal(await card.locator('dl').count(), 0);
    report.checks.push({ width, test: '403 clears prior document data' });
    await ctx.close();
  }
  assert.deepEqual(report.errors, []);assert.deepEqual(report.liveWrites, []);
  report.status = 'PASS';
  fs.writeFileSync(out + '/ui-deferred.json', JSON.stringify(report, null, 2));
  console.log(JSON.stringify({ status: report.status, checks: report.checks, liveWrites: report.liveWrites.length, fixtureWrites: report.fixtureWrites.length }));
  await browser.close();
})().catch(async error => {
  report.status = 'FAIL';report.error = String(error);
  fs.writeFileSync(out + '/ui-deferred.json', JSON.stringify(report, null, 2));console.error(error);
  if (browser) await browser.close();process.exit(1);
});
