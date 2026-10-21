const fs = require('fs'), assert = require('assert');
const { chromium } = require('../../admin/wms_admin_frontend/node_modules/playwright');
const out = 'runtime/test-evidence/tradecase/2026-10-22/T11';
const pass = fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const proof = JSON.parse(fs.readFileSync(out+'/pallet-floor-scope.json','utf8'));
const report = {checks:[],errors:[],writes:[],fixtureCommands:[]};let browser;
(async()=>{
  browser=await chromium.launch();
  for(const width of [1440,390]) {
    const ctx=await browser.newContext({viewport:{width,height:width===390?844:1000}}),page=await ctx.newPage();
    page.on('pageerror',e=>report.errors.push(String(e)));
    await page.route('**/api/**',route=>{
      const r=route.request();if(!['GET','OPTIONS'].includes(r.method())&&!r.url().includes('/auth/')){report.writes.push(r.url());return route.abort();}return route.continue();
    });
    const login=async()=>{if(await page.locator('input[type=password]').count()){await page.fill('input[autocomplete=username]','admin');await page.fill('input[type=password]',pass);await page.click('button[type=submit]');}};
    const began=Date.now();await page.goto('http://127.0.0.1:3000/?page=tradecase&tc_wh=219023232&tc_tab=STOCK');await login();
    const panel=page.locator('section[aria-label="Тип физической паллеты"]');await panel.waitFor({timeout:30000});
    const field=id=>panel.locator('[data-help-id="tradecase.palletfloor.'+id+'"]');
    await field('identifier').fill(proof.uid);
    const reply=page.waitForResponse(r=>r.url().includes('/api/inventory/pallet-floor-types?')&&r.status()===200);
    await field('read').click();const native=await(await reply).json();assert.equal(native.warehouse,219023232);assert(native.types.some(t=>t.id===1));
    await field('type').waitFor();assert((await panel.innerText()).includes(native.cell));
    assert(await panel.locator('a[href$="#pallet-floor"]').count());
    for(const button of await panel.locator('button').all())assert(await button.getAttribute('title'));
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    await panel.screenshot({path:out+'/pallet-floor-'+width+'.png'});
    report.checks.push({width,test:'native current type/catalog/cell and help; no overflow',usefulScreenMs:Date.now()-began});
    let mode='ok',attempt=0,first;
    await page.route('**/api/inventory/pallet-floor-types*',route=>{
      const req=route.request();if(req.method()==='GET')return route.fulfill({status:mode==='denied'?403:200,contentType:'application/json',body:JSON.stringify(mode==='denied'?{detail:{code:'PALLET_FLOOR_CURRENT_WARE_FORBIDDEN'}}:{...native,warehouse:mode==='foreign'?222823304:native.warehouse})});
      const body=req.postDataJSON();report.fixtureCommands.push(body);attempt++;if(attempt===1){first=body;return route.abort('connectionreset');}
      assert.deepEqual(body,first);return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({...proof.declared,operation_id:body.operation_id,version:body.expected_version+1})});
    });
    await field('type').selectOption('1');await field('scan').fill(native.uid);await field('cell').fill(native.cell);await field('reference').fill('Осмотр поддона: тест интерфейса');await field('confirm').click();await field('retry').waitFor();
    await page.reload();await login();await field('retry').waitFor({timeout:30000});await field('retry').click();await panel.getByRole('status').filter({hasText:'Тип паллеты сохранён.'}).waitFor();assert.equal(attempt,2);
    report.checks.push({width,test:'fixture lost reply/reload/exact operation and payload'});
    mode='foreign';await field('identifier').fill(native.uid);await field('read').click();await panel.getByRole('alert').filter({hasText:'Выберите склад'}).waitFor();assert.equal(await field('type').count(),0);
    mode='denied';await field('read').click();await panel.getByRole('alert').filter({hasText:'Паллета недоступна'}).waitFor();assert.equal(await panel.locator('dl').count(),0);
    report.checks.push({width,test:'foreign warehouse and403 clear physical data/form'});await ctx.close();
  }
  assert.deepEqual(report.errors,[]);assert.deepEqual(report.writes,[]);report.status='PASS';fs.writeFileSync(out+'/pallet-floor-ui.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser.close();
})().catch(async e=>{report.status='FAIL';report.error=String(e);fs.writeFileSync(out+'/pallet-floor-ui.json',JSON.stringify(report,null,2));console.error(e);if(browser)await browser.close();process.exit(1);});
