// Actual Oracle-backed exceptions screen, GET only; the two-unit write-off is already complete.
const fs = require('fs'), path = require('path'), assert = require('assert');
const ROOT = path.resolve(__dirname, '../..'), OUT = path.join(ROOT, 'runtime/test-evidence/tradecase/2026-10-23/T11');
const { chromium } = require(path.join(ROOT, 'admin/wms_admin_frontend/node_modules/playwright'));
const report = { status: 'FAIL', checks: [], errors: [], writes: [] };
(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    for (const width of [1440, 390]) {
      const context = await browser.newContext({ viewport: { width, height: 1000 } });
      const p = await context.newPage(); p.on('pageerror', e => report.errors.push(e.message));
      await p.route('**/api/**', route => {
        if (!['GET', 'OPTIONS'].includes(route.request().method())) { report.writes.push(route.request().url()); return route.abort(); }
        return route.continue();
      });
      await p.goto('http://127.0.0.1:3000/?page=workspace&workspace=exceptions&warehouse_id=212476763');
      const password = p.locator('input[type=password]'); await password.waitFor();
      await p.locator('input[autocomplete=username]').fill('admin'); await password.fill('admin123');
      const start = Date.now(); await p.locator('button[type=submit]').click();
      await p.getByRole('tab', { name: 'Дела качества', exact: true }).click();
      await p.getByText('Списано со склада', { exact: false }).first().waitFor();
      const ready_ms = Date.now() - start;
      const desk = p.locator('section[aria-label="Исключения склада"]');
      assert((await desk.innerText()).includes('ответ SAP/СКМ ожидается'));
      assert(!await desk.getByRole('button', { name: 'Провести списание', exact: true }).count());
      const size = await p.evaluate(() => ({ viewport: innerWidth, document: document.documentElement.scrollWidth }));
      assert(size.document <= size.viewport + 1);
      await desk.scrollIntoViewIfNeeded(); await p.screenshot({ path: path.join(OUT, `quality-live-${width}.png`), fullPage: true });
      report.checks.push({ width, ready_ms, size, case: 'Actual posted case and separate external pending; no repeated posting action' });
      await context.close();
    }
    assert(report.errors.length === 0, report.errors.join(';')); assert(report.writes.length === 0); report.status = 'PASS';
  } finally { fs.writeFileSync(path.join(OUT, 'quality-live-ui.json'), JSON.stringify(report, null, 2)); await browser.close(); }
  console.log(JSON.stringify(report));
})().catch(e => { console.error(e); process.exitCode = 1; });
