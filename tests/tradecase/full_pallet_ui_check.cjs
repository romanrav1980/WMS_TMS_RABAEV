const fs = require('fs'), assert = require('assert');
const { chromium } = require('../../admin/wms_admin_frontend/node_modules/playwright');
const out = 'runtime/test-evidence/tradecase/2026-10-21/T06';
const pass = fs.readFileSync('AGENTS.md', 'utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const proof = JSON.parse(fs.readFileSync(out + '/fullpal-shipment.json', 'utf8'));
const report = { checks: [], errors: [], liveWrites: [], fixtureCommands: [] };let browser;
(async () => {
  browser = await chromium.launch();
  for (const width of [1440, 390]) {
    const ctx = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 1000 } });
    const page = await ctx.newPage();page.on('pageerror', e => report.errors.push(String(e)));
    await page.route('**/api/**', route => {
      const req = route.request();
      if (!['GET', 'OPTIONS'].includes(req.method()) && !req.url().includes('/auth/')) { report.liveWrites.push(req.url());return route.abort(); }
      return route.continue();
    });
    const login = async () => { if (await page.locator('input[type=password]').count()) { await page.fill('input[autocomplete=username]', 'admin');await page.fill('input[type=password]', pass);await page.click('button[type=submit]'); } };
    const start = Date.now();
    await page.goto('http://127.0.0.1:3000/?page=tradecase&tc_wh=221164919&tc_tab=STOCK');await login();
    const panel = page.locator('section[aria-label="Целая паллета в отгрузке"]');await panel.waitFor({ timeout: 30000 });
    const input = panel.locator('[data-help-id="tradecase.fullpal.task"]'), read = panel.locator('[data-help-id="tradecase.fullpal.read"]');
    await input.fill('1219');const response = page.waitForResponse(r => r.request().method() === 'GET' && r.url().endsWith('/1219/full-pallet-shipment'));
    await read.click();const native = await (await response).json();assert.equal(native.warehouse_id, 221164919);
    await panel.getByRole('status').filter({ hasText: 'Связана с местом отгрузки' }).waitFor({ timeout: 30000 });
    assert.equal(await panel.locator('[data-help-id="tradecase.fullpal.bind"]').count(), 0);
    assert((await panel.innerText()).includes('10 шт.'));assert(await panel.locator('a[href$="#full-pallet"]').count());
    for (const el of await panel.locator('button').all()) assert(await el.getAttribute('title'));
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'page overflow ' + width);
    await panel.screenshot({ path: out + '/fullpal-' + width + '.png' });
    report.checks.push({ width, test: 'live bound ten pieces; duplicate action hidden/help/no overflow', usefulScreenMs: Date.now() - start });
    let mode = 'unbound', attempt = 0, first;
    await page.route('**/1219/full-pallet-shipment', route => {
      const req = route.request();
      if (req.method() === 'GET') return route.fulfill({ status: mode === 'denied' ? 403 : 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' },
        body: JSON.stringify(mode === 'denied' ? { detail: { code: 'TRADE_OWNER_ACCESS_DENIED' } } : { ...native, bound_shipments: 0, bound_shipment_identifier: null }) });
      const body = req.postDataJSON();report.fixtureCommands.push(body);attempt++;
      if (attempt === 1) { first = body;return route.abort('connectionreset'); }
      assert.deepEqual(body, first);return route.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ ...proof.result, operation_id: body.operation_id }) });
    });
    await input.fill('');await input.fill('1219');await read.click();await panel.locator('[data-help-id="tradecase.fullpal.pallet"]').waitFor();
    await panel.locator('[data-help-id="tradecase.fullpal.pallet"]').fill(native.pallet_identifier);
    await panel.locator('[data-help-id="tradecase.fullpal.shipment"]').fill(proof.shipment_identifier);
    await panel.locator('[data-help-id="tradecase.fullpal.bind"]').click();await panel.locator('[data-help-id="tradecase.fullpal.retry"]').waitFor();
    await page.reload();await login();await panel.locator('[data-help-id="tradecase.fullpal.retry"]').waitFor({ timeout: 30000 });
    await panel.locator('[data-help-id="tradecase.fullpal.retry"]').click();await panel.getByRole('status').filter({ hasText: 'Паллета связана' }).waitFor();
    assert.equal(attempt, 2);assert.deepEqual(first, report.fixtureCommands.at(-1));assert.equal(await panel.locator('[data-help-id="tradecase.fullpal.retry"]').count(), 0);
    report.checks.push({ width, test: 'fixture lost reply/reload/exact original operation and payload retained' });
    mode = 'denied';await input.fill('1219');await read.click();await panel.getByRole('alert').filter({ hasText: 'Паллета недоступна' }).waitFor();
    assert.equal(await panel.locator('dl').count(), 0);report.checks.push({ width, test: '403 clears physical data; no live mutation' });
    await ctx.close();
  }
  assert.deepEqual(report.errors, []);assert.deepEqual(report.liveWrites, []);report.status = 'PASS';
  fs.writeFileSync(out + '/fullpal-ui.json', JSON.stringify(report, null, 2));console.log(JSON.stringify({ status: report.status, checks: report.checks, liveWrites: report.liveWrites.length }));await browser.close();
})().catch(async e => { report.status = 'FAIL';report.error = String(e);const pg=browser?.contexts().at(-1)?.pages().at(-1);if(pg){report.dom=await pg.locator('section[aria-label]').filter({has:pg.locator('[data-help-id="tradecase.fullpal.task"]')}).innerText().catch(()=>null);report.saved=await pg.evaluate(()=>Object.keys(localStorage).filter(k=>k.startsWith('tradecase.fullpal:')).map(k=>({key:k,value:localStorage.getItem(k)})));await pg.screenshot({path:out+'/fullpal-failure.png',fullPage:true});}fs.writeFileSync(out + '/fullpal-ui.json', JSON.stringify(report, null, 2));console.error(e);if (browser) await browser.close();process.exit(1); });
