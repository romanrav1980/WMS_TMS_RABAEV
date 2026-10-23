// Real inventory markup/script with labelled fixture responses; no Oracle or stock commands.
const fs = require('fs'), path = require('path'), assert = require('assert');
const { chromium } = require('../../admin/wms_admin_frontend/node_modules/playwright');
const out = 'runtime/test-evidence/tradecase/2026-10-23/T11';
const report = { kind: 'FIXTURE_BROWSER', checks: [], errors: [] };
(async () => {
 const browser = await chromium.launch();
 try {
  for (const width of [1440, 390]) {
   const ctx = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 1000 } });
   const p = await ctx.newPage(); p.on('pageerror', e => report.errors.push(String(e)));
   await p.route('http://127.0.0.1:33339/**', r => r.fulfill({ status: 200, body: '' }));
   await p.goto('http://127.0.0.1:33339/');
   let html = fs.readFileSync('wiki-raw/wms_admin_ui_reference/inventory-count.html', 'utf8');
   html = html.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '').replace(/<link\b[^>]*>/gi, () => '<style>' + fs.readFileSync('wiki-raw/wms_admin_ui_reference/styles.css', 'utf8') + '</style>');
   await p.setContent(html);
   await p.evaluate(() => {
    document.body.classList.remove('auth-pending');
    window.wmsAdminAuth = { state: { apiBase: 'http://inventory.test', user: null }, headers: () => ({}) };
    window.fixture = { deny: false, delayed: false, urls: [], writes: [] };
    window.fetch = async (url, options = {}) => {
     window.fixture.urls.push(String(url));
     if (options.method === 'POST') {
      window.fixture.writes.push(options.body);
      return new Response(JSON.stringify({ detail: { code: 'DENIED', outcome_confirmed: true } }), { status: 403 });
     }
     const cell = new URL(url).searchParams.get('cell');
     if (cell === 'SLOW') await new Promise(resolve => { window.fixture.resolveOld = resolve; });
     if (window.fixture.deny) return new Response(JSON.stringify({ detail: 'Owner view denied' }), { status: 403 });
     return new Response(JSON.stringify({ lots: [{ uid: 'UID.' + cell, cell, article: 'A', unit: 'EA', physical_qty: '20', hard_qty: '0', stock_version: 1, marking_profiles: [] }] }));
    };
   });
   await p.addScriptTag({ path: path.resolve('wiki-raw/wms_admin_ui_reference/inventory-count.js') });
   const pending = { operation_id: 'COUNT.unknown', revision_id: 1, reason: 'Saved original fixture command', counts: [] };
   await p.evaluate(body => {
    window.wmsAdminAuth.state.user = { username: 'counter' };
    const key = JSON.stringify(['retailcase.inventoryIntent', 'http://inventory.test', 'counter']);
    localStorage.setItem(key, JSON.stringify(body)); localStorage.setItem(key + ':delivery', 'unknown');
   }, pending);
   await p.fill('#countRevision', '1'); await p.fill('#countCell', 'A'); await p.fill('#countArticle', 'A'); await p.fill('#countInventoryTask', '42');
   await p.click('#countLoad'); await p.locator('#countRows tr').waitFor();
   assert.equal(await p.locator('#countRows tr').count(), 1);
   assert((await p.evaluate(() => window.fixture.urls)).some(u => new URL(u).searchParams.get('inventory_task_id') === '42'));
   report.checks.push({ width, name: 'Selected task identity forwarded to existing scoped lots API' });
   await p.evaluate(() => { window.fixture.deny = true; }); await p.click('#countLoad');
   await p.waitForFunction(() => document.getElementById('countMessage').textContent.includes('\u041d\u0435\u0442 \u0434\u043e\u0441\u0442\u0443\u043f\u0430'));
   assert.equal(await p.locator('#countRows tr').count(), 0);
   await p.click('#countRetry');
   await p.waitForFunction(() => !document.getElementById('countRetry').disabled);
   const stored = await p.evaluate(() => {
    const key = JSON.stringify(['retailcase.inventoryIntent', 'http://inventory.test', 'counter']);
    return { body: localStorage.getItem(key), delivery: localStorage.getItem(key + ':delivery'), writes: window.fixture.writes };
   });
   assert.deepStrictEqual(JSON.parse(stored.body), pending); assert.equal(stored.delivery, 'unknown');
   assert.deepStrictEqual(JSON.parse(stored.writes[0]), pending);
   report.checks.push({ width, name: '403 clears stale rows; retry preserves unknown original body even after confirmed denial' });
   await p.evaluate(() => { window.fixture.deny = false; });
   await p.fill('#countCell', 'SLOW'); await p.click('#countLoad'); await p.waitForFunction(() => !!window.fixture.resolveOld);
   await p.fill('#countCell', 'NEXT'); await p.click('#countLoad'); await p.getByText('UID.NEXT', { exact: true }).waitFor();
   await p.evaluate(() => window.fixture.resolveOld()); await p.waitForTimeout(50);
   assert(!(await p.locator('#countRows').innerText()).includes('UID.SLOW'));
   report.checks.push({ width, name: 'Late previous-cell result never replaces current-cell rows' });
   await p.fill('#countCell', 'SLOW'); await p.click('#countLoad');
   await p.evaluate(() => { window.wmsAdminAuth.state.user = { username: 'other' }; window.fixture.resolveOld(); });
   await p.waitForTimeout(50); assert.equal(await p.locator('#countRows tr').count(), 0);
   report.checks.push({ width, name: 'Actor change discards in-flight data' });
   assert(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), 'horizontal overflow');
   assert.deepStrictEqual(await p.locator('button').evaluateAll(bs => bs.filter(b => !b.title || !b.dataset.helpId).map(b => b.id)), []);
   report.checks.push({ width, name: 'Actual page CSS fits viewport; every button has hint and help id' });
   await p.screenshot({ path: `${out}/inventory-read-recovery-${width}.png`, fullPage: true });
   await ctx.close();
  }
  assert.deepStrictEqual(report.errors, []); report.status = 'PASS';
 } catch (e) { report.status = 'FAIL'; report.error = String(e.stack || e); console.error(e); }
 finally { await browser.close(); fs.mkdirSync(out, { recursive: true }); fs.writeFileSync(out + '/inventory-read-recovery-ui.json', JSON.stringify(report, null, 2)); }
 console.log(report.status, report.checks.length, 'checks'); process.exitCode = report.status === 'PASS' ? 0 : 1;
})();
