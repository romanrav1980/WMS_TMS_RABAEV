// Built UI + actual API reads. No inventory or business-result mutations.
const fs = require('fs'), assert = require('assert');
const { chromium } = require('../../admin/wms_admin_frontend/node_modules/playwright');
const out = 'runtime/test-evidence/tradecase/2026-10-23/T02';
fs.mkdirSync(out, { recursive: true });
const pass = fs.readFileSync('AGENTS.md', 'utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const report = { checks: [], errors: [], writes: [], http: [] };
const supply = JSON.parse(fs.readFileSync(out + '/supply-parts-live.json'));
const rejected = 'FP21.221164919.ORDER';
(async () => {
 const browser = await chromium.launch();
 try {
  for (const width of [1440, 390]) {
   const ctx = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 1000 } });
   const page = await ctx.newPage();
   page.on('pageerror', e => report.errors.push(String(e)));
   page.on('requestfinished', async req => {
    if (req.url().includes('/api/')) report.http.push({ method: req.method(), url: req.url(), ms: req.timing().responseEnd, status: (await req.response())?.status() });
   });
   await page.route('**/api/**', route => {
    const r = route.request();
    if (!['GET', 'OPTIONS'].includes(r.method()) && !r.url().includes('/auth/')) {
     report.writes.push(r.method() + ' ' + r.url()); return route.abort();
    }
    return route.continue();
   });
   const open = async wh => {
    await page.goto(`http://127.0.0.1:3000/?page=tradecase&tc_wh=${wh}&tc_tab=MESSAGES`);
    const pw = page.locator('input[type=password]');
    const panel = page.locator('section.tc-bind').first();
    await Promise.race([pw.waitFor({ timeout: 30000 }), panel.waitFor({ timeout: 30000 })]);
    if (await pw.count()) { await page.fill('input[autocomplete=username]', 'admin'); await pw.fill(pass); await page.click('button[type=submit]'); }
   };
   const began = Date.now();
   await open(221164919);
   const compositions = page.locator('[aria-label="\u041f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u0435 \u0441\u043e\u0441\u0442\u0430\u0432\u0430 \u0437\u0430\u043a\u0430\u0437\u043e\u0432"]');
   const item = compositions.locator('li').filter({ hasText: rejected });
   await item.waitFor({ timeout: 30000 });
   const text = await item.innerText();
   assert(text.includes('SAP TC03.SAP: \u043f\u0440\u0438\u043d\u044f\u043b') && text.includes('\u0421\u041a\u041c TC03.SKM: \u043e\u0442\u043a\u043b\u043e\u043d\u0438\u043b'), text);
   report.checks.push({ width, name: 'Live independent SAP accepted / SKM rejected', usefulMs: Date.now() - began });
   assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), 'composition overflow');
   assert.deepStrictEqual(await compositions.locator('button').evaluateAll(bs => bs.filter(b => !b.title || !b.dataset.helpId).map(b => b.textContent)), []);
   const help = await compositions.locator('a[href*="help/"]').first().getAttribute('href');
   assert((await ctx.request.get(new URL(help, page.url()).href)).ok());
   await compositions.screenshot({ path: `${out}/composition-live-${width}.png` });
   await item.getByRole('button').first().click();
   await page.waitForFunction(() => new URLSearchParams(location.search).get('tc_open') === 'FP21.221164919.ORDER');
   report.checks.push({ width, name: 'Order navigation, help and button hints; no horizontal overflow' });
   await open(210564699);
   const parts = page.locator('[aria-label="\u0421\u043e\u0441\u0442\u0430\u0432 \u043f\u043e\u0441\u0442\u0430\u0432\u043e\u043a \u0447\u0430\u0441\u0442\u044f\u043c\u0438"]');
   const part = parts.locator('li').filter({ hasText: supply.ordered_body.document_id }).filter({ hasText: '\u0432\u0435\u0440\u0441\u0438\u044f 2' });
   await part.waitFor({ timeout: 30000 });
   assert.deepStrictEqual(await parts.locator('button').evaluateAll(bs => bs.filter(b => !b.title || !b.dataset.helpId).map(b => b.textContent)), []);
   assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), 'parts overflow');
   await parts.screenshot({ path: `${out}/supply-parts-live-${width}.png` });
   await part.getByRole('button', { name: '\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442 \u043f\u0440\u0438\u0451\u043c\u0430' }).click();
   await page.waitForFunction(() => new URLSearchParams(location.search).get('tc_open')?.startsWith('PARTS.'));
   report.checks.push({ width, name: 'Actual delivered parts open existing intake result; hints and no overflow' });
   await ctx.close();
  }
  assert.deepStrictEqual(report.errors, []); assert.deepStrictEqual(report.writes, []);
  report.status = 'PASS';
 } catch (e) { report.status = 'FAIL'; report.error = String(e.stack || e); console.error(e); }
 finally { await browser.close(); fs.writeFileSync(out + '/composition-parts-read-ui.json', JSON.stringify(report, null, 2)); }
 console.log(report.status, report.checks.length, 'checks');
 process.exitCode = report.status === 'PASS' ? 0 : 1;
})();
