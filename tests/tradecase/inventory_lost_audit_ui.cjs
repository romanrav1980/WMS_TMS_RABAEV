// Real served shell; replay an exact audited zero-stock API response, no business writes.
const fs = require('fs'), assert = require('assert');
const { chromium } = require('../../admin/wms_admin_frontend/node_modules/playwright');
const out = 'runtime/test-evidence/tradecase/2026-10-23/T11';
const audit = JSON.parse(fs.readFileSync(out + '/inventory-api-audit-recovered.json'));
const sample = audit.calls.find(r => r.method === 'GET' && r.response?.lots?.some(l => l.physical_qty === '0' && l.lost_codes?.length === 20));
assert(sample && !sample.response_truncated);
const pass = fs.readFileSync('AGENTS.md', 'utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const report = { checks: [], errors: [], writes: [], sourceApiCall: sample.api_call_id, mode: 'Audited actual GET replay; real page/auth; injected403' };
(async () => {
 const browser = await chromium.launch();
 try {
  for (const width of [1440, 390]) {
   const ctx = await browser.newContext({ viewport: { width, height: 900 } });
   await ctx.addInitScript(basic => sessionStorage.setItem('wmsAdminAuth', JSON.stringify({ apiBase: 'http://127.0.0.1:8088', basic })), 'Basic ' + Buffer.from('admin:' + pass).toString('base64'));
   const p = await ctx.newPage(); let denied = false;
   p.on('pageerror', e => report.errors.push(String(e)));
   await p.route('**/api/**', route => {
    const r = route.request();
    if (!['GET', 'OPTIONS'].includes(r.method())) { report.writes.push(r.method() + ' ' + r.url()); return route.abort(); }
    if (r.url().includes('/inventory/418/lots')) return route.fulfill(denied ? { status: 403, json: { detail: 'revoked' } } : { json: sample.response });
    return route.continue();
   });
   await p.goto('http://127.0.0.1:8088/wms-admin/inventory-count.html?revision_id=418&cell=ALS303760e2f0');
   await p.locator('.count-lost').waitFor();
   assert.equal(await p.locator('.count-lost').getAttribute('open'), null);
   if (width === 390) assert.equal(await p.locator('.count-task-queue').getAttribute('open'), null);
   await p.locator('.count-lost summary').click();
   const lost = sample.response.lots.find(l => l.lost_codes?.length === 20);
   const text = await p.locator('.count-lost').innerText();
   assert(text.includes('(20)') && text.includes(lost.lost_codes[0]) && text.includes(lost.lost_codes[19]));
   assert(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
   assert.deepStrictEqual(await p.locator('button[id^=count]').evaluateAll(bs => bs.filter(b => !b.title || !b.dataset.helpId).map(b => b.id)), []);
   await p.locator('#countHelp').click(); assert(await p.locator('#countHelpDialog').isVisible());
   await p.locator('#countHelpClose').click();
   await p.evaluate(() => window.scrollTo(0, 0));
   await p.screenshot({ path: `${out}/inventory-lost-audit-expanded-${width}.png`, fullPage: true });
   await p.locator('.count-lost summary').click();
   await p.evaluate(() => window.scrollTo(0, 0));
   await p.screenshot({ path: `${out}/inventory-lost-audit-${width}.png`, fullPage: true });
   report.checks.push({ width, check: 'Actual archived zero quantity and20lost codes render; hints/help/width' });
   denied = true; await p.locator('#countLoad').click();
   await p.waitForFunction(() => document.querySelectorAll('.count-lost').length === 0);
   report.checks.push({ width, check: 'Revoked read clears archived codes and rows' });
   await ctx.close();
  }
  assert.deepStrictEqual(report.errors, []); assert.deepStrictEqual(report.writes, []); report.status = 'PASS';
 } finally { fs.writeFileSync(out + '/inventory-lost-audit-ui.json', JSON.stringify(report, null, 2)); await browser.close(); }
 console.log(JSON.stringify({ status: report.status, checks: report.checks.length }));
})().catch(e => { console.error(e); process.exit(1); });
