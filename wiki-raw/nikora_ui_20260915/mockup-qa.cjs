/* Offline mockup QA only: no WMS/ERP endpoints, no production assertions. */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { chromium } = require('../../admin/wms_admin_frontend/node_modules/playwright');
const base = __dirname;
const html = fs.readFileSync(path.join(base, 'nikora-workplaces.html'), 'utf8');
const shots = path.join(base, 'screenshots');
fs.mkdirSync(shots, { recursive: true });
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1040, height: 900 }, colorScheme: 'light' });
  const errors = [];
  page.on('pageerror', err => errors.push(err.message));
  await page.route('**/*', route => route.abort());
  await page.setContent(html);
  const root = page.locator('#nikora-ui');
  const report = { scope: 'Offline interactive mockups; not production UI/API/Oracle/hardware tests', screenshots: [], checks: [] };
  const role = async r => page.selectOption('#nk-role', r);
  const scan = async s => { await page.fill('#nk-scan', s); await page.locator('#nk-scan-form button').click(); };
  const message = () => page.locator('#nk-feedback').innerText();
  const capture = async name => { await root.screenshot({ path: path.join(shots, name + '.png') }); report.screenshots.push(name + '.png'); };
  const roles = await page.locator('#nk-role option').evaluateAll(els => els.map(el => el.value));
  assert.equal(roles.length, 15);
  for (const r of roles) {
    await role(r);
    await page.locator('[data-view="a"]').click();
    await capture(r + '-a');
    if (['reachtruck','reachdispatch','warehouse','crossdock','transport','consolidation','integration'].includes(r)) {
      await page.locator('[data-view="b"]').click();
      await capture(r + '-b');
    }
  }
  report.checks.push('15 roles rendered; 7 alternative views captured');
  await role('reachtruck');
  await scan('WRONG');
  assert.match(await message(), /Ошибка/);
  assert.match(await page.locator('.nk-big').innerText(), /источник/);
  await scan('A-03-02'); await scan('PLT-104'); await page.locator('[data-taken]').click(); await scan('CD-02');
  assert.match(await page.locator('.nk-big').innerText(), /завершено/);
  report.checks.push('Reachtruck: wrong code stays on same step; complete movement on one screen');
  await role('reachdispatch');
  assert.equal(await page.locator('[data-priority]').isDisabled(), true);
  await page.locator('[data-view="a"]').click();
  await page.locator('[data-row="1"]').click();
  assert.equal(await page.locator('[data-priority]').isEnabled(), true);
  await page.locator('[data-priority]').click();
  assert.match(await message(), /не прерывается/);
  report.checks.push('Dispatcher: taken task cannot reprioritize; waiting task has preview');
  await role('quality');
  await scan('SKU-001'); await page.locator('[data-close-pass]').click();
  assert.match(await page.locator('.nk-big').innerText(), /2/);
  await scan('SKU-001'); await scan('SKU-001'); await page.locator('[data-close-pass]').click();
  assert.equal(await page.locator('[data-inspection]').isDisabled(), true);
  report.checks.push('Independent passes: mismatch blocks inspection transition');
  await page.locator('[data-reset]').click();
  for (let pass = 0; pass < 2; pass++) { await scan('SKU-001'); await scan('SKU-001'); await page.locator('[data-close-pass]').click(); }
  assert.equal(await page.locator('[data-inspection]').isEnabled(), true);
  await page.locator('[data-inspection]').click();
  await page.locator('[data-weigh]').click(); assert.match(await message(), /в допуске/);
  await page.locator('[data-bad-weight]').click(); assert.match(await message(), /HOLD/);
  await page.locator('[data-no-weight]').click(); assert.equal(await page.locator('[data-weigh]').isDisabled(), true);
  report.checks.push('Weight: pass, excess, disconnected device blocks recheck');
  await role('loader'); await scan('HU-104');
  assert.match(await page.locator('.nk-device').innerText(), /LOADED/);
  assert.doesNotMatch(await page.locator('.nk-device').innerText(), /ERP ORDER_IN_TRANSIT/);
  await page.locator('[data-depart]').click(); assert.match(await page.locator('.nk-device').innerText(), /ERP ORDER_IN_TRANSIT/);
  report.checks.push('Loaded and departed are distinct; transit only after departure');
  await role('receipt'); await page.fill('#nk-received','10'); await page.locator('[data-receive]').click();
  assert.match(await message(), /нужна причина/);
  await page.selectOption('#nk-reason', { label: 'Недостача' }); await page.locator('[data-receive]').click();
  assert.match(await message(), /Расхождение 2/);
  report.checks.push('Partial receipt requires reason and preserves shortage');
  await page.setViewportSize({ width:360,height:900 });
  for (const r of roles) {
    await role(r); await page.locator('[data-view="a"]').click();
    const dimensions = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, client:document.documentElement.clientWidth }));
    assert.ok(dimensions.scroll <= dimensions.client + 1, r + ': viewport overflow');
  }
  await role('reachtruck'); await capture('reachtruck-phone-360');
  await role('quality'); await capture('quality-phone-360');
  report.checks.push('All 15 roles fit 360px viewport (tables use local scrolling)');
  await page.setViewportSize({ width:1440,height:1000 });
  await page.emulateMedia({ colorScheme:'dark' }); await role('reachdispatch'); await capture('reachdispatch-dark');
  report.checks.push('Dark appearance captured');
  assert.deepEqual(errors, []);
  assert.ok(!html.includes('fetch(') && !html.includes('XMLHttpRequest') && !html.includes('WebSocket'));
  report.checks.push('No JavaScript page errors; no network API calls');
  report.result = 'PASS';
  fs.writeFileSync(path.join(base,'mockup-qa.json'), JSON.stringify(report,null,2)+'\n', 'utf8');
  console.log(JSON.stringify(report,null,2));
  await browser.close();
})().catch(err => { console.error(err); process.exit(1); });

