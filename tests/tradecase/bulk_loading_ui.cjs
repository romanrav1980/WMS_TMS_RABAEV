const fs=require('fs'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-22/T07',proof=JSON.parse(fs.readFileSync(out+'/bulk-small-loading.json','utf8'));
const pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1],report={checks:[],errors:[],writes:[]};let browser;
(async()=>{
 browser=await chromium.launch();
 for(const width of [1440,390]){
  const ctx=await browser.newContext({viewport:{width,height:width===390?844:1000}}),page=await ctx.newPage();let attempt=0,original,mode='ready';
  page.on('pageerror',e=>report.errors.push(String(e)));
  await page.route('**/api/**',route=>{const r=route.request();if(!['GET','OPTIONS'].includes(r.method())&&!r.url().includes('/auth/')){report.writes.push(r.url());return route.abort();}return route.continue();});
  await page.route('**/api/transport/loading/bulk-box-preview?*',route=>route.fulfill({status:mode==='denied'?403:200,contentType:'application/json',body:JSON.stringify(mode==='denied'?{detail:{code:'FORBIDDEN'}}:proof.preview)}));
  await page.route('**/api/transport/loading/confirm-bulk-box',route=>{
   const body=route.request().postDataJSON();attempt++;if(!original)original=body;else assert.deepStrictEqual(body,original);
   assert.equal(body.source_kind,'SINGLE');assert.equal(body.identifier,'BS22.ST.1163');assert.equal(body.scan_container,proof.preview.snapshot.nodes[0].sscc);assert.equal(body.expected_composition_signature,proof.preview.composition_signature);assert.equal(body.measurements.gross_weight_kg,'2.1');
   return route.fulfill({status:attempt===1?503:200,contentType:'application/json',body:JSON.stringify(attempt===1?{detail:{code:'RESULT_UNCERTAIN',outcome_confirmed:false}}:{...proof.results.load,operation_id:body.operation_id})});
  });
  const login=async()=>{await page.waitForFunction(()=>window.wmsAdminAuth);await page.waitForFunction(()=>window.wmsAdminAuth.state.user||!window.wmsAdminAuth.state.basic);if(!await page.evaluate(()=>Boolean(window.wmsAdminAuth.state.user))){await page.fill('#loginUser','admin');await page.fill('#loginPassword',pass);await page.click('#adminLoginForm button[type=submit]');}await page.waitForFunction(()=>window.wmsAdminAuth.state.user?.username==='admin');};
  const start=Date.now();await page.goto('http://127.0.0.1:8088/wms-admin/transport-loading.html?trip_id=33664');await login();await page.locator('#tripSummary').filter({hasText:'B22V1161'}).waitFor({timeout:30000});
  await page.selectOption('#loadMode','BULK');assert(await page.locator('#loadShipment').isHidden());assert(await page.locator('#loadOriginalOperation').isHidden());
  await page.fill('#loadIdentifier',proof.preview.snapshot.nodes[0].sscc);await page.click('#loadComposition');await page.locator('#loadCompositionSummary').filter({hasText:'Версия 4'}).waitFor();
  assert((await page.locator('#loadBoxRows').innerText()).includes('итогового весового контроля'));assert.equal(await page.locator('#loadBoxRows input').count(),0);assert(await page.locator('a[href="/help/manual-weight.html#bulk"]').count());
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'bulk overflow '+width);
  await page.locator('.loading-manual-measure').screenshot({path:out+'/bulk-measures-'+width+'.png'});
  if(width===390){const rows=await page.locator('.loading-manual-measure>label').evaluateAll(nodes=>nodes.map(n=>({top:n.getBoundingClientRect().top,bottom:n.getBoundingClientRect().bottom})));assert.equal(rows.length,4);for(let i=1;i<rows.length;i++)assert(rows[i].top>=rows[i-1].bottom,'measurement labels overlap');}
  await page.screenshot({path:out+'/bulk-mode-'+width+'.png',fullPage:true});report.checks.push({width,test:'real trip and captured pre-load carton preview; server QC mass; mode navigation/help/geometry',usefulScreenMs:Date.now()-start});
  const values={loadScan:proof.preview.snapshot.nodes[0].sscc,loadCell:proof.preview.snapshot.cell,loadVehicle:'B22V1161',loadDock:'B22D1161',loadGross:'2.1',loadWidth:'0.4',loadDepth:'0.5',loadHeight:'0.5'};for(const[id,value]of Object.entries(values))await page.fill('#'+id,value);
  await page.click('#loadConfirm');await page.locator('#loadStatus').filter({hasText:'исходный идентификатор'}).waitFor();assert.equal(attempt,1);
  await page.reload();await login();await page.locator('#loadRetry').waitFor({timeout:30000});await page.click('#loadRetry');await page.locator('#loadStatus').filter({hasText:'Подтверждено.'}).waitFor();assert.equal(attempt,2);report.checks.push({width,test:'fixture503/reload/exact original bulk command and receipt; no native POST'});
  await page.selectOption('#loadMode','BULK');await page.fill('#loadIdentifier',proof.preview.snapshot.nodes[0].sscc);await page.click('#loadComposition');await page.locator('#loadCompositionSummary').filter({hasText:'Версия 4'}).waitFor();mode='denied';await page.click('#loadComposition');await page.locator('#loadStatus').filter({hasText:'FORBIDDEN'}).waitFor();assert.equal(await page.locator('#loadCompositionSummary').innerText(),'');assert.equal(await page.locator('#loadBoxRows fieldset').count(),0);
  report.checks.push({width,test:'403 clears composition and manual box rows'});await ctx.close();
 }
 assert.equal(report.errors.length,0,JSON.stringify(report.errors));assert.equal(report.writes.length,0,JSON.stringify(report.writes));report.status='PASS';
})().catch(e=>{report.status='FAIL';report.error=String(e);process.exitCode=1;}).finally(async()=>{fs.writeFileSync(out+'/bulk-loading-ui.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser?.close();});
