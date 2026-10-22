const fs=require('fs'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-22/T07',proof=JSON.parse(fs.readFileSync(out+'/manual-tare-live.json','utf8'));
const pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1],report={checks:[],errors:[],writes:[]};let browser;
(async()=>{
 browser=await chromium.launch();
 for(const width of [1440,390]){
  const ctx=await browser.newContext({viewport:{width,height:width===390?844:1000}}),page=await ctx.newPage();let attempt=0,original,held,entered;
  const arrival=new Promise(resolve=>entered=resolve);page.on('pageerror',e=>report.errors.push(String(e)));
  await page.route('**/api/**',route=>{const r=route.request();if(!['GET','OPTIONS'].includes(r.method())&&!r.url().includes('/auth/')){report.writes.push(r.url());return route.abort();}return route.continue();});
  await page.route('**/api/case-pick/tasks/1164/return-carrier',async route=>{
   const body=route.request().postDataJSON();attempt++;if(!original)original=body;else assert.deepStrictEqual(body,original);
   if(attempt===4){entered();await new Promise(resolve=>held=resolve);}
   const status=attempt===1?503:attempt===3?403:200;
   const result=status===503?{detail:{code:'RESULT_UNCERTAIN',outcome_confirmed:false}}:status===403?{detail:{code:'OWNER_FORBIDDEN',outcome_confirmed:false}}:{...proof.cancelled,operation_id:attempt===2?'OTHER_OPERATION':body.operation_id};
   return route.fulfill({status,contentType:'application/json',body:JSON.stringify(result)});
  });
  const login=async()=>{await page.waitForFunction(()=>window.wmsAdminAuth);await page.waitForFunction(()=>window.wmsAdminAuth.state.user||!window.wmsAdminAuth.state.basic);if(!await page.evaluate(()=>Boolean(window.wmsAdminAuth.state.user))){await page.fill('#loginUser','admin');await page.fill('#loginPassword',pass);await page.click('#adminLoginForm button[type=submit]');}await page.waitForFunction(()=>window.wmsAdminAuth.state.user?.username==='admin');};
  await page.goto('http://127.0.0.1:8088/wms-admin/case-pick-tsd.html');await login();
  await page.evaluate(async()=>{const task=await cpTsdFetch('/api/case-pick/tasks/1164');cpTsd.task={...task,status:'IN_PROGRESS',picked_qty:0,physical_lots:[]};cpTsdRender();});
  await page.fill('#cpTsdScanContainer',proof.label.sscc);await page.fill('#cpTsdEmptyCancelReason','UI fixture: empty task only');await page.click('#cpTsdCancelEmpty');await page.locator('#cpTsdRetryReturn').waitFor();assert.equal(attempt,1);
  const journal=await page.evaluate(()=>{const key=JSON.stringify(['retailcase.caseCarrierReturn',cpTsdApiBase(),cpTsdUser()]);return{key,raw:localStorage.getItem(key)};});assert(journal.raw);
  await page.reload();await login();await page.evaluate(()=>cpTsdRender());await page.locator('#cpTsdRetryReturn').waitFor();await page.click('#cpTsdRetryReturn');await page.waitForFunction(()=>!window.cpTsdStockBusy);assert.equal(attempt,2);assert.equal(await page.evaluate(k=>localStorage.getItem(k),journal.key),journal.raw);
  report.checks.push({width,test:'fixture503/reload/exact request; unrelated receipt does not settle'});
  await page.click('#cpTsdRetryReturn');await page.waitForFunction(()=>!window.cpTsdStockBusy);assert.equal(attempt,3);assert.equal(await page.evaluate(k=>localStorage.getItem(k),journal.key),journal.raw);assert.equal(await page.evaluate(()=>cpTsd.task),null);
  report.checks.push({width,test:'403 keeps original return intent'});
  await page.click('#cpTsdRetryReturn');await arrival;await page.evaluate(()=>{window.wmsAdminAuth.state.user={username:'fixture-other',permissions:[]};});held();await page.waitForFunction(()=>!window.cpTsdStockBusy);assert.equal(await page.evaluate(k=>localStorage.getItem(k),journal.key),journal.raw);
  await page.evaluate(()=>{window.wmsAdminAuth.state.user={username:'admin',permissions:['*']};cpTsdRender();});await page.locator('#cpTsdRetryReturn').waitFor();await page.click('#cpTsdRetryReturn');await page.waitForFunction(k=>localStorage.getItem(k)===null,journal.key);assert.equal(attempt,5);
  report.checks.push({width,test:'late receipt after fixture identity switch preserves original; original user exact retry settles'});
  assert(await page.locator('a[href="/help/manual-weight.html#empty-cancel"]').count());assert(await page.locator('#cpTsdCancelEmpty').getAttribute('title'));assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await ctx.close();
 }
 assert.equal(report.errors.length,0,JSON.stringify(report.errors));assert.equal(report.writes.length,0,JSON.stringify(report.writes));report.status='PASS';
})().catch(e=>{report.status='FAIL';report.error=String(e);process.exitCode=1;}).finally(async()=>{fs.writeFileSync(out+'/case-return-ui.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser?.close();});
