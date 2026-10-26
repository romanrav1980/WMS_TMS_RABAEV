const fs=require('fs'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-26/T08/carton-scale/physical';
const state=JSON.parse(fs.readFileSync(out+'/state.json','utf8'));
const pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const report={checks:[],errors:[],writes:[]};let browser;
(async()=>{
 browser=await chromium.launch();
 for(const width of[1440,390]){
  const ctx=await browser.newContext({viewport:{width,height:width===390?844:1000}}),page=await ctx.newPage();
  page.on('pageerror',e=>report.errors.push(String(e)));
  await page.route('**/api/**',route=>{
   const r=route.request();if(!['GET','OPTIONS'].includes(r.method())&&!r.url().includes('/auth/')){report.writes.push(r.url());return route.abort();}return route.continue();
  });
  await page.goto('http://127.0.0.1:8088/wms-admin/case-pick-management.html');
  await page.waitForFunction(()=>window.wmsAdminAuth);
  if(!await page.evaluate(()=>Boolean(window.wmsAdminAuth.state.user))){await page.fill('#loginUser','admin');await page.fill('#loginPassword',pass);await page.click('#adminLoginForm button[type=submit]');}
  const panel=page.locator('.case-panel').filter({has:page.getByRole('heading',{name:'Типы тары и финальное взвешивание',exact:true})});
  await panel.waitFor();await panel.locator('select[aria-label="Тип тары"] option[value="'+state.box_type+'"]').waitFor({state:'attached'});
  await panel.locator('select[aria-label="Тип тары"]').selectOption(String(state.box_type));
  const option=panel.locator('option[value="BOX"]');assert.equal(await option.innerText(),'Короб');assert.equal(await panel.locator('select').nth(1).inputValue(),'BOX');
  for(const button of await panel.locator('button').all()){assert((await button.getAttribute('title'))?.trim());assert((await button.boundingBox()).height>=44);}
  const help=panel.locator('a[href="/help/manual-weight.html#enter"]');assert.equal(await help.count(),1);
  assert((await ctx.request.get('http://127.0.0.1:8088/help/manual-weight.html')).ok());
  await panel.scrollIntoViewIfNeeded();await page.screenshot({path:out+'/box-type-'+width+'.png'});report.checks.push({width,class:'BOX',type:state.box_type});
  if(width===1440){const response=await ctx.request.post('http://127.0.0.1:8088/api/case-pick/pallet-types',{headers:{Authorization:'Basic '+Buffer.from('admin:'+pass).toString('base64')},data:{pallet_type_code:'REJECT_ONLY',pallet_type_name:'Invalid class must not reach Oracle',load_unit_class:'NOT_A_CLASS'}});assert.equal(response.status(),422);report.invalidClassStatus=422;}
  await ctx.close();
 }
 assert.deepStrictEqual(report.errors,[]);assert.deepStrictEqual(report.writes,[]);report.status='PASS';
})().catch(error=>{report.status='FAIL';report.error=String(error);process.exitCode=1;}).finally(async()=>{fs.writeFileSync(out+'/box-type-ui.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser?.close();});
