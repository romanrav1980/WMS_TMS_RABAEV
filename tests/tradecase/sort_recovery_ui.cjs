// Built browser flow with injected outcomes; no warehouse POST reaches Oracle.
const fs = require('fs'), assert = require('assert');
const { chromium } = require('../../admin/wms_admin_frontend/node_modules/playwright');
const out = 'runtime/test-evidence/tradecase/2026-10-23/T06';
const pass = fs.readFileSync('AGENTS.md', 'utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const report = { checks: [], errors: [], businessWrites: 0, backend: 'Injected sort outcomes; real login/page' };
(async () => {
 const browser = await chromium.launch();
 try {
  for (const width of [1440, 390]) for (const first of ['conflict', 'unknown']) {
   const ctx = await browser.newContext({ viewport: { width, height: 900 } });
   const page = await ctx.newPage(), bodies = [];
   let phase = first;
   page.on('pageerror', e => report.errors.push(String(e)));
   await page.route('**/api/**', route => {
    const r = route.request(), url = r.url();
    if (r.method() === 'POST' && url.endsWith('/stock/sort')) {
     const body = r.postDataJSON(); bodies.push(body);
     const result = phase === 'unknown' ? { status: 503, detail: { code: 'POSTED_CONNECTION_RESET_FAILED', outcome_confirmed: false } }
      : phase === 'conflict' ? { status: 409, detail: { code: 'STOCK_RULE_REJECTED', reason: 'Changed stored request', operation_id_conflict: true, outcome_confirmed: false } }
      : phase === 'denied' ? { status: 403, detail: { code: 'CURRENT_ACCESS_DENIED' } } : null;
     return route.fulfill(result ? { status: result.status, json: { detail: { ...result.detail, operation_id: body.operation_id } } }
      : { json: { operation_id: body.operation_id, uid: 'fixture-target', base_quantity: '1', base_uom: 'EA', from_cell: 'FROM', cell: 'TO' } });
    }
    if (!['GET', 'OPTIONS'].includes(r.method()) && !url.includes('/auth/')) {
     report.businessWrites++; return route.abort();
    }
    return route.continue();
   });
   const open = async () => {
    await page.goto('http://127.0.0.1:3000/?page=tradecase&tc_wh=219023232&tc_tab=SORT');
    const pw = page.locator('input[type=password]');
    await Promise.race([pw.waitFor({ timeout: 30000 }), page.locator('.tc-sort').waitFor({ timeout: 30000 })]);
    if (await pw.count()) { await page.fill('input[autocomplete=username]', 'admin'); await pw.fill(pass); await page.click('button[type=submit]'); }
    await page.locator('.tc-sort').waitFor({ timeout: 30000 });
    await page.locator('.platform-nav-user').filter({ hasText: 'admin' }).waitFor({ state: 'attached', timeout: 30000 });
    await page.evaluate(() => new Promise(requestAnimationFrame));
   };
   await open();
   for (const [id, value] of [['source', 'OWN'], ['from', 'FROM'], ['to', 'TO']])
    await page.locator(`[data-help-id="tradecase.sort.${id}"]`).fill(value);
   await page.locator('.tc-scanrow input').fill('fixture-code');
   await page.locator('[data-help-id="tradecase.sort.add"]').click();
   await page.locator('[data-help-id="tradecase.sort.confirm"]').check();
   await page.locator('.tc-sort > button').last().click();
   const retry = page.locator('.tc-sort').getByRole('button', { name: '\u041f\u043e\u0432\u0442\u043e\u0440\u0438\u0442\u044c \u0442\u0443 \u0436\u0435 \u043a\u043e\u043c\u0430\u043d\u0434\u0443' });
   await retry.waitFor({ timeout: 5000 }).catch(async e => { console.log(JSON.stringify({ bodies, panel: await page.locator(".tc-sort").innerText() })); throw e; });
   assert.strictEqual(bodies.length, 1);
   report.checks.push({ width, first, check: 'First uncertain/conflicting result keeps original command' });
   await open(); await retry.waitFor();
   phase = 'denied'; await retry.click();
   await page.waitForFunction(() => document.querySelector('.tc-sort')?.textContent.includes('\u043a\u043e\u043c\u0430\u043d\u0434\u0430 \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0430'));
   assert.deepStrictEqual(bodies[1], bodies[0]);
   assert(await retry.isVisible());
   assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
   assert.deepStrictEqual(await page.locator('.tc-sort button').evaluateAll(bs => bs.filter(b => !b.title || !b.dataset.helpId).map(b => b.textContent)), []);
   const help = await page.locator('.tc-sort a[href*="help/"]').getAttribute('href');
   assert((await ctx.request.get(new URL(help, page.url()).href)).ok());
   await page.screenshot({ path: `${out}/sort-recovery-${first}-${width}.png`, fullPage: true });
   phase = 'success'; await retry.click();
   await retry.waitFor({ state: 'detached' });
   assert.deepStrictEqual(bodies[2], bodies[0]);
   report.checks.push({ width, first, check: 'Reload/403/exact retry/confirmed success; help, hints and width' });
   await ctx.close();
  }
  assert.deepStrictEqual(report.errors, []); assert.strictEqual(report.businessWrites, 0);
  report.status = 'PASS';
 } finally {
  fs.writeFileSync(`${out}/sort-recovery-ui.json`, JSON.stringify(report, null, 2));
  await browser.close();
 }
 console.log(JSON.stringify({ status: report.status, checks: report.checks.length }));
})().catch(e => { console.error(e); process.exit(1); });
