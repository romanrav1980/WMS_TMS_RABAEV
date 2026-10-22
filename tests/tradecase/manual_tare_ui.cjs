const fs=require('fs'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-22/T07',pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const report={checks:[],errors:[],writes:[]};let browser;
(async()=>{
 browser=await chromium.launch();
 for(const width of [1440,390]){
  const ctx=await browser.newContext({viewport:{width,height:width===390?844:1000}}),page=await ctx.newPage();let mode='native',attempt=0,original,native;
  page.on('pageerror',e=>report.errors.push(String(e)));
  await page.route('**/api/**',route=>{const r=route.request();if(!['GET','OPTIONS'].includes(r.method())&&!r.url().includes('/auth/')){report.writes.push(r.url());return route.abort();}return route.continue();});
  const login=async()=>{await page.waitForFunction(()=>window.wmsAdminAuth);await page.waitForFunction(()=>window.wmsAdminAuth.state.user||!window.wmsAdminAuth.state.basic);if(!await page.evaluate(()=>Boolean(window.wmsAdminAuth.state.user))){await page.fill('#loginUser','admin');await page.fill('#loginPassword',pass);await page.click('#adminLoginForm button[type=submit]');}await page.waitForFunction(()=>window.wmsAdminAuth.state.user?.username==='admin');};
  await page.goto('http://127.0.0.1:8088/wms-admin/case-pick-tsd.html');await login();
  await page.evaluate(async()=>{cpTsd.task=await cpTsdFetch('/api/case-pick/tasks/1163');cpTsdRender();});
  const panel=page.locator('#cpManualTare');await panel.getByRole('status').filter({hasText:'0.1 кг'}).waitFor({timeout:30000});
  assert(await panel.getByRole('button',{name:'Сохранить вес тары',exact:true}).isDisabled());
  for(const button of await panel.locator('button').all())assert(await button.getAttribute('title'));
  assert(await panel.locator('a[href="/help/manual-weight.html#empty-tare"]').count());
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'native overflow '+width);
  await panel.screenshot({path:out+'/manual-tare-'+width+'.png'});report.checks.push({width,test:'native manual tare displayed; filled carton cannot remeasure; help/titles/geometry'});
  native=await page.evaluate(()=>cpTsdFetch('/api/case-pick/tasks/1163/sscc-label'));
  await page.route('**/api/case-pick/tasks/1163/sscc-label',route=>mode==='native'?route.continue():route.fulfill({status:mode==='denied'?403:200,contentType:'application/json',body:JSON.stringify(mode==='denied'?{detail:{code:'FORBIDDEN'}}:{...native,manual_empty_tare:null})}));
  await page.route('**/api/inventory/warehouse-scales/tasks/1163/manual-empty-tare',route=>{
   const body=route.request().postDataJSON();attempt++;if(!original)original=body;else assert.deepStrictEqual(body,original);
   return route.fulfill({status:attempt===1?503:200,contentType:'application/json',body:JSON.stringify(attempt===1?{detail:{code:'RESULT_UNCERTAIN',outcome_confirmed:false}}:{operation_id:body.operation_id,case_pick_task_id:1163,sscc:body.scan_container,origin:'MANUAL_CONFIRMED',stock_changed:false,tare_weight_kg:body.tare_weight_kg})});
  });
  mode='fixture';await page.evaluate(()=>{cpTsd.task={...cpTsd.task,status:'IN_PROGRESS',picked_qty:0};cpTsdRender();});
  const save=panel.getByRole('button',{name:'Сохранить вес тары',exact:true});await save.waitFor();await page.waitForFunction(()=>!document.querySelector('#cpManualTare button').disabled);
  await panel.locator('[data-field=scan]').fill(native.current_carrier);await panel.locator('[data-field=weight]').fill('0.1');await panel.locator('[data-field=reference]').fill('UI_FIXTURE_ONLY');await save.click();
  await panel.getByRole('button',{name:'Повторить сохранённый вес',exact:true}).waitFor();assert.equal(attempt,1);
  await page.reload();await login();await panel.getByRole('button',{name:'Повторить сохранённый вес',exact:true}).waitFor({timeout:30000});await panel.getByRole('button',{name:'Повторить сохранённый вес',exact:true}).click();await page.waitForFunction(()=>!window.wmsCaseManualTare.hasPending());assert.equal(attempt,2);
  report.checks.push({width,test:'fixture503/reload/exact original manual command; no native write'});
  mode='native';await page.evaluate(async()=>{cpTsd.task=await cpTsdFetch('/api/case-pick/tasks/1163');cpTsdRender();});await panel.getByRole('status').filter({hasText:'0.1 кг'}).waitFor();
  mode='denied';await page.evaluate(()=>cpTsdRender());await panel.getByRole('status').filter({hasText:'FORBIDDEN'}).waitFor();assert(await save.isDisabled());assert.equal(await panel.locator('[data-field=weight]').inputValue(),'');assert(!(await panel.innerText()).includes('0.1 кг'));assert.equal(await page.locator('#cpCaseLabelTare').innerText(),'');
  report.checks.push({width,test:'403 clears measured tare and disables new input'});await ctx.close();
 }
 assert.equal(report.errors.length,0,JSON.stringify(report.errors));assert.equal(report.writes.length,0,JSON.stringify(report.writes));report.status='PASS';
})().catch(e=>{report.status='FAIL';report.error=String(e);process.exitCode=1;}).finally(async()=>{fs.writeFileSync(out+'/manual-tare-ui.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser?.close();});
