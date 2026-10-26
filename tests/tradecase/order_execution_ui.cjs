const fs=require('fs'),assert=require('assert');
const{chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-26/T08/partial-80';
const state=JSON.parse(fs.readFileSync(out+'/state.json','utf8'));
const label=state.phase==='CLOSED'?'closed':state.phase==='REMAINDER_LOADED'?'remainder-loaded':'partial';
const expected=label==='closed'?[80,80,80,80,0]:label==='remainder-loaded'?[80,80,80,60,0]:[80,80,60,60,20];
const pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[\x60,)\s]/)[1];
const report={checks:[],writes:[],errors:[]};let browser;
(async()=>{
 browser=await chromium.launch();
 for(const width of[1440,390]){
  const ctx=await browser.newContext({viewport:{width,height:width===390?844:1000}}),page=await ctx.newPage();let denied=0;
  page.on('pageerror',e=>report.errors.push(String(e)));
  await page.route('**/api/**',route=>{
   const req=route.request();
   if(!['GET','OPTIONS'].includes(req.method())&&!req.url().includes('/auth/')){report.writes.push(req.url());return route.abort();}
   if(denied&&req.url().includes('/documents/ORDER/O80'))return route.fulfill({status:denied,contentType:'application/json',body:JSON.stringify({detail:{code:'TRADECASE_ACCESS_DENIED'}})});
   return route.continue();
  });
  const start=Date.now();await page.goto('http://127.0.0.1:3000/?'+new URLSearchParams({page:'tradecase',tc_wh:String(state.fixture.warehouse_id),tc_tab:'ORDER',tc_open:'O80'}));
  if(await page.locator('input[type=password]').count()){await page.fill('input[autocomplete=username]','admin');await page.fill('input[type=password]',pass);await page.click('button[type=submit]');}
  const card=page.locator('.tc-order-execution');await card.locator('strong').first().waitFor({timeout:30000});
  assert.deepStrictEqual(await card.locator('strong').allTextContents(),expected.map(n=>n+' кор.'));
  report.checks.push({width,usefulScreenMs:Date.now()-start,boxes:expected});
  await card.scrollIntoViewIfNeeded();assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  for(const strong of await card.locator('strong').all()){const box=await strong.boundingBox();assert(box.x>=0&&box.x+box.width<=width,'Quantity outside viewport');}
  await page.screenshot({path:out+'/order-execution-'+label+'-'+width+'.png',fullPage:false});
  assert.equal(await card.locator('a[href="/help/tradecase-documents.html#order"]').count(),1);
  const help=await page.request.get('http://127.0.0.1:3000/help/tradecase-documents.html');assert(help.ok());assert((await help.text()).includes('осталось на складе 20'));
  for(const status of[403,404]){
   denied=status;await page.getByRole('button',{name:'Обновить',exact:true}).click();await page.locator('section.tc-card [role=alert]').waitFor();assert.equal(await card.count(),0);
   denied=0;await page.getByRole('button',{name:'Обновить',exact:true}).click();await card.locator('strong').first().waitFor();
   assert.deepStrictEqual(await card.locator('strong').allTextContents(),expected.map(n=>n+' кор.'));
   report.checks.push({width,denial:status,cleared:true,recovered:true});
  }
  await ctx.close();
 }
 assert.equal(report.writes.length,0);assert.equal(report.errors.length,0);report.status='PASS';
})().catch(e=>{report.status='FAIL';report.error=String(e);process.exitCode=1;}).finally(async()=>{fs.writeFileSync(out+'/order-execution-'+label+'-ui.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser?.close();});
