const fs=require('fs'),assert=require('assert');
const{chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-26/T08';
const s=JSON.parse(fs.readFileSync(out+'/topup-physical-660.json','utf8'));
const pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const report={checks:[],writes:[],errors:[],provider:'Real reads; all loading POST responses intercepted'};let browser;
(async()=>{
 browser=await chromium.launch();
 for(const width of[1440,390]){
  const ctx=await browser.newContext({viewport:{width,height:width===390?844:1000}}),page=await ctx.newPage();let posts=0;
  page.on('pageerror',e=>report.errors.push(String(e)));
  await page.route('**/api/**',route=>{const request=route.request();if(!['GET','OPTIONS'].includes(request.method())&&!request.url().includes('/auth/')){report.writes.push(request.url());return route.abort();}return route.continue();});
  await page.route('**/api/transport/loading/confirm-single',route=>{posts++;return route.fulfill({status:409,contentType:'application/json',body:JSON.stringify({detail:{code:'STOCK_RULE_REJECTED',message:'ORA-20886: LOAD_PLACE_EXCEEDS_VEHICLE_DIMENSIONS',operation_id:route.request().postDataJSON().operation_id,outcome_confirmed:true}})});});
  await page.goto('http://127.0.0.1:8088/wms-admin/transport-loading.html?trip_id='+s.transport.transport_task_id);
  await page.waitForFunction(()=>window.wmsAdminAuth);
  await page.waitForFunction(()=>window.wmsAdminAuth.state.user||!window.wmsAdminAuth.state.basic);
  if(!await page.evaluate(()=>Boolean(window.wmsAdminAuth.state.user))){await page.fill('#loginUser','admin');await page.fill('#loginPassword',pass);await page.click('#adminLoginForm button[type=submit]');}
  await page.locator('#tripSummary').filter({hasText:s.transport.vehicle_number}).waitFor({timeout:30000});
  const ship=s.shipments[Object.keys(s.shipments).sort()[0]];
  await page.selectOption('#loadMode','SINGLE');await page.fill('#loadShipment',ship.shipment_identifier);await page.click('#loadComposition');
  await page.waitForFunction(()=>document.getElementById('loadCompositionSummary').textContent.includes('Версия'));
  const values={loadScan:ship.pallet,loadCell:ship.cell,loadVehicle:s.transport.vehicle_number,loadDock:s.transport.dock,loadGross:'200',loadWidth:'1.2',loadDepth:'0.8',loadHeight:'2.5'};
  for(const[id,value]of Object.entries(values))await page.fill('#'+id,value);
  await page.click('#loadConfirm');await page.locator('#loadStatus').filter({hasText:'Грузовое место не помещается в кузов'}).waitFor();
  assert.equal(posts,1);assert(!String(await page.locator('#loadStatus').innerText()).includes('LOAD_PLACE_'));
  assert(await page.locator('#loadRestart').isVisible());
  const retained=await page.evaluate(()=>Object.entries(localStorage).filter(([key])=>key.startsWith('wms-physical-load:')).map(([,value])=>JSON.parse(value)));
  assert.equal(retained.length,1);assert.equal(retained[0].confirmed_rejection,true);assert.equal(retained[0].body.measurements.height_m,'2.5');
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'horizontal overflow '+width);
  assert(await page.locator('#loadActionStatus').isVisible());assert((await page.locator('.loading-trip-table').boundingBox()).height<=353);await page.locator('#loadActionStatus').scrollIntoViewIfNeeded();await page.screenshot({path:out+'/loading-dimensions-'+width+'.png',fullPage:false});
  const help=await page.request.get('http://127.0.0.1:8088/help/manual-weight.html');assert(help.ok());assert((await help.text()).includes('id="vehicle-dimensions"'));
  report.checks.push({width,confirmedRefusal:true,originalIntentRetained:true,help:true});await ctx.close();
 }
 assert.equal(report.writes.length,0);assert.equal(report.errors.length,0);report.status='PASS';
})().catch(e=>{report.status='FAIL';report.error=String(e);process.exitCode=1;}).finally(async()=>{fs.writeFileSync(out+'/loading-dimensions-ui.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser?.close();});
