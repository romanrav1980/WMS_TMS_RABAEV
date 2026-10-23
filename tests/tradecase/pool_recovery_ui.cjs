// Browser regression of pending-intent recovery and incomplete pool presentation; all fetches are fixtures, warehouse writes0.
const fs = require('fs'), path = require('path'), assert = require('assert');
const { chromium } = require('../../admin/wms_admin_frontend/node_modules/playwright');
const out = path.resolve('runtime/test-evidence/tradecase/2026-10-23/T08');
const report = { checks: [], backend: 'FIXTURE', warehouseWrites: 0 };
(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    for (const width of [1440, 390]) {
      const context = await browser.newContext({ viewport: { width, height: 900 } });
      const page = await context.newPage();
      await page.route('http://127.0.0.1:39999/**', route => route.fulfill({ contentType: 'text/html', body: '<html></html>' }));
      await page.goto('http://127.0.0.1:39999/');
      await page.setContent('<input id=poolWarehouse value=210564699><input id=poolArticle value=SKU><input id=poolClass><input id=poolFlag><input id=poolStep><button id=poolLoad>Load</button><button id=poolSave>Save</button><button id=poolAllocate>Allocate</button><p id=poolMessage></p><p id=poolAvailable></p><table><tbody id=poolRows></tbody></table>');
      await page.evaluate(() => {
        window.wmsAdminAuth = { state: { apiBase: 'http://pool.test' }, headers: () => ({}), hasPermission: () => true };
        window.poolWrites = []; window.poolPhase = 0; window.denyRead = false;
        window.fetch = async (url, options = {}) => {
          if (options.method === 'POST') {
            window.poolWrites.push(options.body);
            const phase = window.poolPhase++;
            if (phase === 0) throw new TypeError('Response lost');
            if (phase === 1) return new Response(JSON.stringify({ detail: { code: 'ACCESS_DENIED', outcome_confirmed: true } }), { status: 403 });
            return new Response(JSON.stringify({ allocated_quantity: '20', unit: 'EA', operation_id: JSON.parse(options.body).operation_id }));
          }
          if (String(url).includes('/api/sku-allocation')) return new Response(JSON.stringify({ detail: 'Configuration denied' }), { status: 403 });
          if (window.denyRead) return new Response(JSON.stringify({ detail: 'Pool denied' }), { status: 403 });
          return new Response(JSON.stringify({ complete: false, available_quantity: null, unit: 'EA', from_stock: true,
            orders: [{ order_id: 1, line_id: 2, quantity: '20' }], allocations: { '2': '20' } }));
        };
      });
      await page.addScriptTag({ path: path.resolve('wiki-raw/wms_admin_ui_reference/stock-pool.js') });
      const click = async id => { await page.locator('#' + id).click(); await page.waitForFunction(() => !document.getElementById('poolLoad').disabled); };
      await click('poolLoad');
      assert.equal(await page.locator('#poolRows tr').count(), 1);
      assert(!(await page.locator('#poolAvailable').innerText()).includes('null'));
      report.checks.push({ width, name: 'Partial authorized result shown without null total, despite403 on settings' });
      await click('poolAllocate');
      const key = 'retailcase.soft-pool.pending.v1';
      const first = await page.evaluate(k => localStorage.getItem(k), key); assert(first);
      await click('poolAllocate');
      assert.equal(await page.evaluate(k => localStorage.getItem(k), key), first);
      assert.equal(await page.locator('#poolRows tr').count(), 0);
      report.checks.push({ width, name: '403 on retry retains unknown original intent and clears stale pool data' });
      await click('poolAllocate');
      assert.equal(await page.evaluate(k => localStorage.getItem(k), key), null);
      const writes = await page.evaluate(() => window.poolWrites);
      assert.equal(writes.length, 3); assert(writes.every(body => body === writes[0]));
      report.checks.push({ width, name: 'Three identical bodies; only confirmed successful result clears intent' });
      await page.evaluate(() => { window.poolPhase = 1; });
      await click('poolAllocate');
      assert.equal(await page.evaluate(k => localStorage.getItem(k), key), null);
      report.checks.push({ width, name: 'First definitively denied command has no retained unknown outcome' });
      await click('poolLoad'); await page.evaluate(() => { window.denyRead = true; }); await click('poolLoad');
      assert.equal(await page.locator('#poolRows tr').count(), 0);
      assert(!(await page.locator('#poolAvailable').innerText()).includes('20'));
      report.checks.push({ width, name: '403 during refresh clears previous rows and total' });
      await context.close();
    }
    report.status = 'PASS';
  } catch (error) { report.status = 'FAIL'; report.error = String(error); throw error; }
  finally { fs.mkdirSync(out, { recursive: true }); fs.writeFileSync(path.join(out, 'pool-recovery-ui.json'), JSON.stringify(report, null, 2)); await browser.close(); }
  console.log(report.status, report.checks.length);
})();
