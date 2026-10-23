// C-0166: the real inventory-count markup/script with labelled FIXTURE responses (native NOT_APPLIED; no Oracle, no stock command).
// Checks: lost codes shown per lot with the closing action; a posted shortage/found outcome is reported in plain words; the found code is
// sent as an ordinary scan (server derives found keys); 503 keeps the same operation id for retry; 403 does not hide an unknown outcome.
const fs = require('fs'), path = require('path'), assert = require('assert');
const { chromium } = require('C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright');
const ROOT = 'C:/projects/TMS', UI = ROOT + '/wiki-raw/wms_admin_ui_reference';
const OUT = path.join(__dirname, '..'), SHOTS = path.join(OUT, 'screenshots'); fs.mkdirSync(SHOTS, { recursive: true });
const report = { kind: 'FIXTURE_BROWSER', checks: [], errors: [] };
const ok = (w, name) => { report.checks.push({ width: w, name }); console.log('PASS', w, name); };
(async () => {
 const browser = await chromium.launch();
 try {
  for (const width of [1440, 390]) {
   const ctx = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 1000 } });
   const p = await ctx.newPage(); p.on('pageerror', e => report.errors.push(width + ': ' + e));
   await p.route('http://127.0.0.1:33340/**', r => r.fulfill({ status: 200, body: '' }));
   await p.goto('http://127.0.0.1:33340/');
   let html = fs.readFileSync(UI + '/inventory-count.html', 'utf8');
   html = html.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '').replace(/<link\b[^>]*>/gi, () => '<style>' + fs.readFileSync(UI + '/styles.css', 'utf8') + '</style>');
   await p.setContent(html);
   await p.evaluate(() => {
    document.body.classList.remove('auth-pending');
    window.wmsAdminAuth = { state: { apiBase: 'http://inventory.test', user: { username: 'counter' } }, headers: () => ({}) };
    window.fixture = { posts: [], mode: 'ok' };
    window.fetch = async (url, options = {}) => {
     if (options.method === 'POST') {
      const body = JSON.parse(options.body); window.fixture.posts.push(body);
      if (window.fixture.mode === 'unknown') return new Response(JSON.stringify({ detail: { code: 'REQUEST_DEADLINE', outcome_confirmed: false, retry_same_operation_id: true } }), { status: 503 });
      if (window.fixture.mode === 'denied') return new Response(JSON.stringify({ detail: { code: 'STOCK_RULE_REJECTED', outcome_confirmed: true } }), { status: 403 });
      return new Response(JSON.stringify({ operation_id: body.operation_id, counts: [{ uid: 'LOT1', delta: '1', lost_units: 0, found_units: 1 }] }));
     }
     return new Response(JSON.stringify({ lots: [
      { uid: 'LOT1', cell: 'A-1', article: 'SKU', unit: 'EA', physical_qty: '19', hard_qty: '0', stock_version: 4, expiry_date: '2027-01-01',
        marking_profiles: [{ system_code: 'CRPT', profile_code: 'TOBACCO' }], lost_codes: ['0104600000000001215LOSTCODE01'] },
      { uid: 'LOT2', cell: 'A-1', article: 'SKU', unit: 'EA', physical_qty: '0', hard_qty: '0', stock_version: 2, expiry_date: '2027-01-01',
        marking_profiles: [{ system_code: 'CRPT', profile_code: 'TOBACCO' }], lost_codes: ['0104600000000001215LOSTCODE02', '0104600000000001215LOSTCODE03'] }] }));
    };
   });
   await p.addScriptTag({ path: UI + '/inventory-count.js' });
   await p.fill('#countRevision', '418'); await p.fill('#countCell', 'A-1'); await p.click('#countLoad');
   await p.locator('[data-lost="0"]').waitFor();
   assert.match(await p.locator('[data-lost="0"]').innerText(), /Не найдены ранее \(1\): 0104600000000001215LOSTCODE01/);
   assert.match(await p.locator('[data-lost="1"]').innerText(), /Не найдены ранее \(2\)/);
   assert.match(await p.locator('[data-lost="0"]').getAttribute('title'), /отсканируйте его.*увеличьте количество/);
   ok(width, 'FIXTURE lost codes per lot (also a zero-quantity lot) with the closing action in the hint');
   await p.fill('[data-count="0"]', '20'); await p.fill('[data-units="0"]', '0104600000000001215LOSTCODE01'); await p.fill('#countReason', 'Найден код при пересчёте');
   await p.evaluate(() => { window.fixture.mode = 'unknown'; }); await p.click('#countPost');
   await p.waitForFunction(() => /сохранена для повтора/.test(document.getElementById('countMessage').textContent));
   const first = await p.evaluate(() => window.fixture.posts[0]);
   assert.deepStrictEqual(first.counts.map(c => [c.uid, c.quantity, c.scans.map(s => s.code)]), [['LOT1', '20', ['0104600000000001215LOSTCODE01']]]);
   assert(!('found_unit_keys' in first.counts[0]), 'found keys are derived by the server from the scans');
   ok(width, 'FIXTURE found code is posted as an ordinary scan; 503 keeps the command for retry');
   await p.evaluate(() => { window.fixture.mode = 'denied'; }); await p.click('#countRetry');
   await p.waitForFunction(() => window.fixture.posts.length === 2);
   const retried = await p.evaluate(() => window.fixture.posts);
   assert.equal(retried[1].operation_id, retried[0].operation_id); assert.deepStrictEqual(retried[1], retried[0]);
   assert(await p.evaluate(() => !document.getElementById('countRetry').hidden), '403 after an unknown outcome must not drop the saved command');
   ok(width, 'retry sends the same operation id and bytes; 403 after an unknown outcome keeps the saved command');
   await p.evaluate(() => { window.fixture.mode = 'ok'; }); await p.click('#countRetry');
   await p.waitForFunction(() => /Пересчёт подтверждён/.test(document.getElementById('countMessage').textContent));
   assert.match(await p.locator('#countMessage').innerText(), /LOT1: найдено 1 ед\., возвращены в остаток/);
   ok(width, 'FIXTURE confirmed outcome names the found units in plain words');
   const bad = await p.locator('button').evaluateAll(bs => bs.filter(b => !b.title || !b.dataset.helpId).map(b => b.id));
   assert.deepStrictEqual(bad, []); ok(width, 'every button has title and help id');
   await p.click('#countHelp'); assert.match(await p.locator('#countHelpDialog').innerText(), /Не найдены ранее[\s\S]*Отгруженную или списанную иначе единицу так вернуть нельзя/);
   await p.click('#countHelpClose'); ok(width, 'local help explains lost/found and what cannot be restored');
   await p.fill('#countCell', 'A-1'); await p.click('#countLoad'); await p.locator('[data-lost="0"]').waitFor();
   const over = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); assert(over <= 1, 'overflow ' + over);
   ok(width, 'no horizontal page scroll');
   await p.screenshot({ path: path.join(SHOTS, `inventory-found-${width}.png`), fullPage: true });
   await ctx.close();
  }
  assert.deepStrictEqual(report.errors, []); report.status = 'PASS';
 } catch (e) { report.status = 'FAIL'; report.error = String(e.stack || e); console.error(e); }
 finally { await browser.close(); }
 fs.writeFileSync(path.join(OUT, 'c0166-ui.json'), JSON.stringify(report, null, 1));
 console.log(report.status, report.checks.length, 'checks');
 process.exit(report.status === 'PASS' ? 0 : 1);
})();
