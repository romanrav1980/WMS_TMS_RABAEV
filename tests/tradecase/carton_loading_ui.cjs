const fs=require('fs'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-26/T08/carton-scale/physical';
const state=JSON.parse(fs.readFileSync(out+'/state.json','utf8'));
const pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const phase=process.env.CARTON_UI_PHASE||'LOADED660',members=Number(process.env.CARTON_UI_MEMBERS||660),loaded=process.env.CARTON_UI_LOADED==='live'?null:Number(process.env.CARTON_UI_LOADED||660);
assert(/^[A-Z0-9_-]+$/.test(phase));
const report={checks:[],writes:[],errors:[],denial:'MODELLED_403; real positive GETs'};let browser;
(async()=>{
 browser=await chromium.launch();
 for(const width of[1440,390]){
  const context=await browser.newContext({viewport:{width,height:width===390?844:1000}}),page=await context.newPage();let deny=false;
  page.on('pageerror',error=>report.errors.push(String(error)));
  await page.route('**/api/**',route=>{
   const request=route.request();
   if(!['GET','OPTIONS'].includes(request.method())&&!request.url().includes('/auth/')){report.writes.push(request.url());return route.abort();}
   if(deny&&request.url().includes('/api/transport/loading/')&&request.url().endsWith('/status'))return route.fulfill({status:403,contentType:'application/json',body:JSON.stringify({detail:{code:'LOADING_CURRENT_WARE_REQUIRED'}})});
   return route.continue();
  });
  const start=Date.now();
  await page.goto('http://127.0.0.1:8088/wms-admin/transport-loading.html?trip_id='+state.transport.transport_task_id);
  await page.waitForFunction(()=>window.wmsAdminAuth);
  await page.waitForFunction(()=>window.wmsAdminAuth.state.user||!window.wmsAdminAuth.state.basic);
  if(!await page.evaluate(()=>Boolean(window.wmsAdminAuth.state.user))){await page.fill('#loginUser','admin');await page.fill('#loginPassword',pass);await page.click('#adminLoginForm button[type=submit]');}
  await page.waitForFunction(count=>document.querySelectorAll('#tripRows tr').length===count,members,{timeout:30000});
  const usefulScreenMs=Date.now()-start;
  const summary=await page.locator('#tripSummary').innerText();
  const observedLoaded=Number(summary.match(/физических мест: (\d+);/)?.[1]);
  assert(Number.isInteger(observedLoaded)&&observedLoaded>=0&&observedLoaded<=members);
  if(loaded!==null)assert.equal(observedLoaded,loaded);
  assert.equal(await page.locator('#tripRows tr').count(),members);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Document overflow');
  const missing=await page.locator('main button:visible').evaluateAll(nodes=>nodes.filter(n=>!n.title.trim()).map(n=>({id:n.id,text:n.textContent})));
  assert.deepStrictEqual(missing,[],'Every visible action needs an explanatory tooltip');
  await page.screenshot({path:out+'/loading-'+phase+'-'+width+'.png',fullPage:false});
  await page.locator('#tripRows tr').last().scrollIntoViewIfNeeded();
  assert(await page.locator('#tripRows tr').last().isVisible());
  const help=page.locator('a[href^="/help/"]').first();assert(await help.count());
  const href=await help.getAttribute('href');const response=await page.request.get('http://127.0.0.1:8088'+href.split('#')[0]);assert(response.ok());
  deny=true;await page.click('#tripLoad');await page.waitForFunction(()=>document.querySelectorAll('#tripRows tr').length===0);
  assert(!await page.locator('#tripSummary').innerText().then(s=>s.includes(state.transport.vehicle_number)));
  deny=false;await page.click('#tripLoad');await page.waitForFunction(count=>document.querySelectorAll('#tripRows tr').length===count,members);
  report.checks.push({width,members,loaded:observedLoaded,usefulScreenMs,tooltips:true,help:href,denialClears:true});
  await context.close();
 }
 assert.deepStrictEqual(report.writes,[]);assert.deepStrictEqual(report.errors,[]);report.status='PASS';
})().catch(error=>{report.status='FAIL';report.error=String(error);process.exitCode=1;}).finally(async()=>{fs.writeFileSync(out+'/loading-ui-'+phase+'.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser?.close();});
