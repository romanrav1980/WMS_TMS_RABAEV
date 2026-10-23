// Real served inventory page/auth/navigation, read-only closed own revision.
const fs = require('fs'), assert = require('assert');
const { chromium } = require('../../admin/wms_admin_frontend/node_modules/playwright');
const out = 'runtime/test-evidence/tradecase/2026-10-23/T11';
const pass = fs.readFileSync('AGENTS.md', 'utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const report = { checks: [], errors: [], writes: [] };
(async () => {
 const browser = await chromium.launch();
 try {
  for (const width of [1440, 390]) {
   const ctx = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 1000 } });
   await ctx.addInitScript(basic => sessionStorage.setItem('wmsAdminAuth', JSON.stringify({ apiBase: 'http://127.0.0.1:8088', basic })), 'Basic ' + Buffer.from('admin:' + pass).toString('base64'));
   const p = await ctx.newPage(); p.on('pageerror', e => report.errors.push(String(e)));
   await p.route('**/api/**', r => {
    const req = r.request();
    if (!['GET', 'OPTIONS'].includes(req.method())) { report.writes.push(req.method() + ' ' + req.url()); return r.abort(); }
    return r.continue();
   });
   await p.goto('http://127.0.0.1:8088/wms-admin/inventory-count.html?revision_id=417&cell=ALS303760e2f0');
   await p.waitForFunction(() => !document.body.classList.contains('auth-pending'));
   await p.waitForFunction(() => /\u0412 \u044f\u0447\u0435\u0439\u043a\u0435 \u043d\u0435\u0442|\u041d\u0435\u0442 \u0434\u043e\u0441\u0442\u0443\u043f\u0430/.test(document.getElementById('countMessage').textContent));
   assert(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), 'page overflow');
   assert.deepStrictEqual(await p.locator('button[id^=count]').evaluateAll(bs => bs.filter(b => !b.title || !b.dataset.helpId).map(b => b.id)), []);
   if (width === 390) {
    assert.equal(await p.locator('#countNav').getAttribute('open'), null);
    await p.locator('#countNav summary').click();
    assert(await p.locator('#countNav .nav a').count() > 0);
    assert(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    await p.locator('#countNav summary').click();
   }
   await p.locator('#countHelp').click(); assert(await p.locator('#countHelpDialog').isVisible());
   await p.locator('#countHelpClose').click(); assert(!(await p.locator('#countHelpDialog').isVisible()));
   await p.screenshot({ path: `${out}/inventory-served-${width}.png`, fullPage: true });
   report.checks.push({ width, name: 'Actual served auth/closed revision read; responsive navigation, help and hints; no overflow' });
   await ctx.close();
  }
  assert.deepStrictEqual(report.errors, []); assert.deepStrictEqual(report.writes, []); report.status = 'PASS';
 } catch (e) { report.status = 'FAIL'; report.error = String(e.stack || e); console.error(e); }
 finally { await browser.close(); fs.writeFileSync(out + '/inventory-page-read-ui.json', JSON.stringify(report, null, 2)); }
 console.log(report.status, report.checks.length, 'checks'); process.exitCode = report.status === 'PASS' ? 0 : 1;
})();
