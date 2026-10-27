// Read the current owned movement forecast in the integrated application; never mutate business data.
const fs = require('fs'), assert = require('assert');
const { chromium } = require('../../admin/wms_admin_frontend/node_modules/playwright');
const root = 'runtime/test-evidence/tradecase/2026-10-27/T08/program-orders';
const state = JSON.parse(fs.readFileSync(root + '/state.resumed.json', 'utf8'));
assert.equal(state.fixture.warehouse_id, 210069361);
const password = fs.readFileSync('AGENTS.md', 'utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const out = root + '/topup-ui'; fs.mkdirSync(out, { recursive: true });
const report = { checks: [], errors: [], writes: [], reads: [] };
(async () => {
  const browser = await chromium.launch();
  try {
    for (const width of [1440, 390]) {
      const context = await browser.newContext({ viewport: { width, height: 950 } });
      const page = await context.newPage();
      page.on('pageerror', e => report.errors.push(String(e)));
      await page.route('**/api/**', async route => {
        const req = route.request();
        if (!['GET', 'OPTIONS'].includes(req.method()) && !req.url().includes('/auth/')) {
          report.writes.push(req.method() + ' ' + req.url()); return route.abort();
        }
        return route.continue();
      });
      page.on('response', r => { if (r.url().includes('/needs/')) report.reads.push({ url: r.url(), status: r.status() }); });
      await page.goto('http://127.0.0.1:3000/?page=tradecase&tc_wh=210069361&tc_tab=NEED&tc_open=N1');
      if (await page.locator('input[type=password]').count()) {
        await page.fill('input[autocomplete=username]', 'admin');
        await page.fill('input[type=password]', password);
        await page.click('button[type=submit]');
      }
      const panel = page.locator('section[aria-label="Расчёт потребности получателя"]');
      await panel.waitFor({ timeout: 30000 });
      const calc = panel.locator('[data-help-id="tradecase.need.calculate"]');
      assert(await calc.isDisabled());
      await panel.locator('input').fill('1440'); await calc.click();
      await panel.locator('dl').waitFor({ timeout: 30000 });
      const text = await panel.innerText();
      assert(text.includes('Прогноз перемещений') && text.includes('80 кор.'), text);
      assert(text.includes('не более 3 дн.'), text);
      assert(!text.includes('Целевой запас') && !text.includes('Доступно у получателя'), text);
      assert(text.includes('согласованные предложения и свободное место'), text);
      assert((await panel.locator('a[href$="#need"]').getAttribute('href')).includes('tradecase-documents.html'));
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'page overflow ' + width);
      await page.screenshot({ path: out + '/forecast-' + width + '.png', fullPage: true });
      await panel.locator('input').fill('1439');
      assert.equal(await panel.locator('dl').count(), 0, 'stale displayed result');
      report.checks.push({ width, liveMovementForecast: true, horizonDays: 3, help: true, noOverflow: true, resultCleared: true });
      await context.close();
    }
    assert.deepEqual(report.errors, []); assert.deepEqual(report.writes, []);
    assert.equal(report.reads.length, 2); assert(report.reads.every(x => x.status === 200));
    report.status = 'PASS';
  } finally { await browser.close(); }
  fs.writeFileSync(out + '/report.json', JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report));
})().catch(error => {
  report.status = 'FAIL'; report.error = String(error);
  fs.writeFileSync(out + '/report.json', JSON.stringify(report, null, 2)); console.error(error); process.exit(1);
});
