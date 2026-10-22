const fs=require('fs'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-22/T07',report={checks:[],errors:[],blockedWrites:[]};
const password=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
(async()=>{
 const browser=await chromium.launch();
 try{
  for(const width of [1440,390]){
   const ctx=await browser.newContext({viewport:{width,height:width===390?844:1000}}),page=await ctx.newPage();let denied=0;
   page.on('pageerror',e=>report.errors.push(String(e)));
   await page.route('**/api/**',r=>{
    if(!['GET','OPTIONS'].includes(r.request().method())&&!r.request().url().includes('/auth/')){report.blockedWrites.push(r.request().url());return r.abort();}
    return r.continue();
   });
   await page.route('**/api/receiving/st-deferrals/waiting-tasks?*',r=>denied?r.fulfill({status:denied,contentType:'application/json',body:JSON.stringify({detail:{code:'FORBIDDEN'}})}):r.continue());
   const began=Date.now();await page.goto('http://127.0.0.1:8088/wms-admin/day-reconciliation.html#stTransfer');
   await page.waitForFunction(()=>window.wmsAdminAuth);
   await page.waitForFunction(()=>window.wmsAdminAuth.state.user||!window.wmsAdminAuth.state.basic);
   if(!await page.evaluate(()=>Boolean(window.wmsAdminAuth.state.user))){await page.fill('#loginUser','admin');await page.fill('#loginPassword',password);await page.click('#adminLoginForm button[type=submit]');}
   await page.waitForFunction(()=>window.wmsAdminAuth.state.user?.username==='admin');
   await page.fill('#sdSt','N22B.220793322');await page.click('#sdRead');
   await page.waitForFunction(()=>document.querySelector('#sdMessage').textContent.includes('33666'));
   const contextMs=Date.now()-began;
   await page.fill('#swDecision','NB22.DEFER.B');const read=Date.now();await page.click('#swRead');
   await page.locator('#swRows tr').filter({hasText:'1224'}).waitFor();
   assert((await page.locator('#swRows').innerText()).includes('Выполнено'));
   report.checks.push({width,test:'Actual context and DONE task',entryToContextMs:contextMs,waitingMs:Date.now()-read});
   for(const id of ['sdRead','sdSave','sdRetry','sdHistory','sdHistoryNext','swRead','swPlan','swRetry','swNext'])assert((await page.locator('#'+id).getAttribute('title')).length>15);
   const help=page.locator('#waitingArea a[href="/help/manual-weight.html#remaining"]');assert(await help.count()===1);
   const response=await ctx.request.get('http://127.0.0.1:8088/help/manual-weight.html');assert(response.ok());assert((await response.text()).includes('id="remaining"'));
   await page.locator('#waitingArea').scrollIntoViewIfNeeded();await page.screenshot({path:out+`/remainder-${width}.png`});
   const dimensions=await page.evaluate(()=>({body:document.documentElement.scrollWidth,viewport:innerWidth}));assert(dimensions.body<=dimensions.viewport+1,JSON.stringify(dimensions));
   report.checks.push({width,test:'Button explanations, served help and page width'});
   const saved=await page.evaluate(()=>{
    const state=window.wmsAdminAuth.state,key='wms-st-waiting-tasks:'+JSON.stringify([state.apiBase,state.user.username]);
    const raw=JSON.stringify({operation_id:'UI_PENDING_NOT_POSTED',decision_operation_id:'NB22.DEFER.B'});localStorage.setItem(key,raw);return {key,raw};
   });
   for(const status of [401,403,404]){
    denied=status;await page.click('#swRead');await page.waitForFunction(()=>document.querySelector('#swRows').children.length===0);
    assert(await page.locator('#swPlan').isDisabled());assert.equal(await page.evaluate(key=>localStorage.getItem(key),saved.key),saved.raw);
    report.checks.push({width,test:`${status} clears stale rows and retains original pending request`});
    denied=0;await page.click('#swRead');await page.locator('#swRows tr').filter({hasText:'1224'}).waitFor();
   }
   await ctx.close();
  }
  assert.deepStrictEqual(report.blockedWrites,[]);assert.deepStrictEqual(report.errors,[]);report.status='PASS';
 }finally{await browser.close();fs.writeFileSync(out+'/remainder-ui.json',JSON.stringify(report,null,2));}
 console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exit(1);});
