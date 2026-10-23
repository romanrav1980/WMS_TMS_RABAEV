// Actual metadata retry with the committed HTTP response deliberately lost; no stock commands.
const fs = require('fs'), assert = require('assert'), crypto = require('crypto');
const { chromium } = require('../../admin/wms_admin_frontend/node_modules/playwright');
const out = 'runtime/test-evidence/tradecase/2026-10-23/T02', file = out + '/composition-retry-live-ui.json';
const res = fs.existsSync(file) ? JSON.parse(fs.readFileSync(file)) : { checks: [], errors: [], unexpectedWrites: [] };
if (res.status === 'PASS') { console.log('Closed; no commands sent'); process.exit(0); }
const save = () => fs.writeFileSync(file, JSON.stringify(res, null, 2));
const pass = fs.readFileSync('AGENTS.md', 'utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const wh = 221164919, order = 'FP21.221164919.ORDER';
const body = { warehouse_id: wh, order_id: order, retry_system: 'SKM', retry_of: 2 };
const headers = { Authorization: 'Basic ' + Buffer.from('admin:' + pass).toString('base64') };
(async () => {
 const browser = await chromium.launch();
 try {
  for (const width of [1440, 390]) {
   const ctx = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 1000 } });
   const p = await ctx.newPage();
   p.on('pageerror', e => res.errors.push(String(e)));
   await p.route('**/api/**', async route => {
    const req = route.request();
    if (['GET', 'OPTIONS'].includes(req.method()) || req.url().includes('/auth/')) return route.continue();
    if (req.method() === 'POST' && req.url().endsWith('/order-compositions/report')) {
     assert.deepStrictEqual(req.postDataJSON(), body);
     res.command = body; save();
     const response = await route.fetch();
     res.retryResponse = { status: response.status(), value: await response.json() }; save();
     assert.equal(res.retryResponse.status, 200);
     return route.abort('failed');
    }
    res.unexpectedWrites.push(req.method() + ' ' + req.url()); save(); return route.abort();
   });
   await p.goto(`http://127.0.0.1:3000/?page=tradecase&tc_wh=${wh}&tc_tab=MESSAGES`);
   const pw = p.locator('input[type=password]');
   const panel = p.locator('[aria-label="\u041f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u0435 \u0441\u043e\u0441\u0442\u0430\u0432\u0430 \u0437\u0430\u043a\u0430\u0437\u043e\u0432"]');
   await Promise.race([pw.waitFor({ timeout: 30000 }), panel.waitFor({ timeout: 30000 })]);
   if (await pw.count()) { await p.fill('input[autocomplete=username]', 'admin'); await pw.fill(pass); await p.click('button[type=submit]'); }
   const row = panel.locator('li').filter({ hasText: order }); await row.waitFor({ timeout: 30000 });
   if (width === 1440 && !res.retryResponse) {
    const retry = row.getByRole('button', { name: '\u041f\u043e\u0432\u0442\u043e\u0440\u0438\u0442\u044c \u0432 \u0421\u041a\u041c' });
    assert(await retry.getAttribute('title')); assert(await retry.getAttribute('data-help-id'));
    await retry.click();
   }
   if (width === 1440 && !res.accepted) {
    await row.getByText('\u0421\u041a\u041c TC03.SKM: \u0436\u0434\u0451\u043c \u043e\u0442\u0432\u0435\u0442\u0430', { exact: false }).waitFor({ timeout: 30000 });
    assert((await row.innerText()).includes('SAP TC03.SAP: \u043f\u0440\u0438\u043d\u044f\u043b'));
    assert.equal(res.retryResponse.value.composition_no, 3);
    assert.equal(await row.getByRole('button', { name: /\u041f\u043e\u0432\u0442\u043e\u0440\u0438\u0442\u044c \u0432/ }).count(), 0);
    await panel.screenshot({ path: `${out}/composition-retry-lost-response-${width}.png` });
    res.checks.push('Real retry committed once; lost reply recovered by current snapshot read; SAP retained'); save();
    res.ackBody = res.ackBody || { schema_version: 1, warehouse_id: wh, system_code: 'SKM', sender_id: 'TC03.SKM',
     event_id: 'CRUI.' + crypto.randomUUID(), order_id: order, composition_no: 3, signature: res.retryResponse.value.signature,
     outcome: 'ACCEPTED', occurred_at: new Date().toISOString() }; save();
    const ack = await ctx.request.post('http://127.0.0.1:8088/api/tradecase/order-compositions/acknowledgments', { headers, data: res.ackBody });
    res.ackResponse = { status: ack.status(), value: await ack.json() }; save(); assert.equal(ack.status(), 200);
    assert.equal(res.ackResponse.value.status, 'CONFIRMED'); res.accepted = true; save();
    await panel.getByRole('button', { name: '\u041e\u0431\u043d\u043e\u0432\u0438\u0442\u044c', exact: true }).click();
   }
   await row.getByText('\u0441\u043e\u0441\u0442\u0430\u0432 \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0451\u043d', { exact: false }).waitFor({ timeout: 30000 });
   assert.deepStrictEqual(await panel.locator('button').evaluateAll(bs => bs.filter(b => !b.title || !b.dataset.helpId).map(b => b.textContent)), []);
   assert(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
   const help = await panel.locator('a[href*="help/"]').first().getAttribute('href');
   const article = await ctx.request.get(new URL(help, p.url()).href); assert(article.ok());
   assert((await article.text()).includes('\u041f\u043e\u0432\u0442\u043e\u0440\u0438\u0442\u044c \u0432 \u0421\u041a\u041c'));
   await panel.screenshot({ path: `${out}/composition-retry-confirmed-${width}.png` });
   res.checks.push({ width, name: 'Real confirmed state, button hints, updated help and no overflow' }); save();
   await ctx.close();
  }
  assert.deepStrictEqual(res.errors, []); assert.deepStrictEqual(res.unexpectedWrites, []);
  res.status = 'PASS'; delete res.error;
 } catch (e) { res.status = 'FAIL'; res.error = String(e.stack || e); console.error(e); }
 finally { await browser.close(); save(); }
 console.log(res.status, res.checks.length, 'checks'); process.exitCode = res.status === 'PASS' ? 0 : 1;
})();
