const fs=require('fs'),assert=require('assert');
const{chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-26/T02/shipment-events';
const state=JSON.parse(fs.readFileSync(out+'/state.json','utf8'));
const proof=JSON.parse(fs.readFileSync(out+'/final.json','utf8'));
const pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[\x60,)\s]/)[1];
const report={checks:[],writes:[],errors:[],modelledDeliveryFailure:true};let browser;
(async()=>{
 browser=await chromium.launch();
 for(const width of[1440,390])for(const[trip,quantity,events]of[['T60','600',proof.first],['T20','200',proof.second]]){
  const ctx=await browser.newContext({viewport:{width,height:width===390?844:1000}}),page=await ctx.newPage();let mode='REAL';
  ctx.on('page',p=>p.on('pageerror',e=>report.errors.push(String(e))));
  await ctx.route('**/api/**',async route=>{
   const req=route.request();
   if(!['GET','OPTIONS'].includes(req.method())&&!req.url().includes('/auth/')){report.writes.push(req.url());return route.abort();}
   if(req.url().includes('/trips/'+trip+'/execution')){
    if(mode==='DENIED')return route.fulfill({status:403,contentType:'application/json',body:JSON.stringify({detail:{code:'TRADECASE_ACCESS_DENIED'}})});
    if(mode==='ERROR'){
     const response=await route.fetch(),body=await response.json();body.shipment_messages[0].delivery_status='ERROR';return route.fulfill({response,json:body});
    }
   }
   return route.continue();
  });
  const start=Date.now();await page.goto('http://127.0.0.1:3000/?'+new URLSearchParams({page:'tradecase',tc_wh:String(state.fixture.warehouse_id),tc_tab:'TRIP',tc_open:trip}));
  await page.waitForSelector('input[type=password], section.tc-card');
  if(await page.locator('input[type=password]').count()){await page.fill('input[autocomplete=username]','admin');await page.fill('input[type=password]',pass);await page.click('button[type=submit]');}
  const panel=page.locator('.tc-shipment-messages');await panel.locator('tbody tr').first().waitFor({timeout:30000});
  assert.equal(await panel.locator('tbody tr').count(),2);
  assert.deepStrictEqual(await panel.locator('tbody tr td:nth-child(2)').allTextContents(),[quantity,quantity]);
  assert((await panel.innerText()).includes('SAP')&&(await panel.innerText()).includes('СКМ'));
  const ids=new Set(events.map(e=>e.id)),links=panel.locator('[data-help-id="tradecase.shipment.queue"]');
  for(const link of await links.all()){const href=await link.getAttribute('href');assert(ids.has(Number(new URL(href,'http://127.0.0.1:3000').searchParams.get('event_id'))));assert(await link.getAttribute('title'));}
  await panel.scrollIntoViewIfNeeded();assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  for(const cell of await panel.locator('tbody tr').first().locator('td').all()){const box=await cell.boundingBox();assert(box.x>=0&&box.x+box.width<=width,'Shipment state must fit the phone viewport');}
  await page.screenshot({path:out+'/shipment-'+trip+'-'+width+'.png',fullPage:false});
  report.checks.push({width,trip,quantity,usefulScreenMs:Date.now()-start});
  mode='ERROR';await page.getByRole('button',{name:'Обновить',exact:true}).click();await panel.locator('tbody tr').filter({hasText:'Ошибка передачи'}).waitFor();
  assert.equal(await panel.locator('tbody tr').filter({hasText:'В очереди'}).count(),1);
  mode='DENIED';await page.getByRole('button',{name:'Обновить',exact:true}).click();await panel.waitFor({state:'detached'});assert.equal(await panel.count(),0);
  mode='REAL';await page.getByRole('button',{name:'Обновить',exact:true}).click();await panel.locator('tbody tr').first().waitFor();assert.equal(await panel.locator('tbody tr').filter({hasText:'В очереди'}).count(),2);
  const help=await page.request.get('http://127.0.0.1:3000/help/tradecase-documents.html');assert(help.ok());assert((await help.text()).includes('id="shipment"'));
  const popupPromise=page.waitForEvent('popup');await links.first().click();const popup=await popupPromise;
  await popup.waitForFunction(()=>window.wmsAdminAuth);await popup.waitForFunction(()=>window.wmsAdminAuth.state.user||!window.wmsAdminAuth.state.basic);
  if(!await popup.evaluate(()=>Boolean(window.wmsAdminAuth.state.user))){await popup.fill('#loginUser','admin');await popup.fill('#loginPassword',pass);await popup.click('#adminLoginForm button[type=submit]');}
  await popup.locator('#externalDetails').filter({hasText:'TRADECASE_SHIPMENT_'}).waitFor({timeout:30000});
  const selected=Number(new URL(popup.url()).searchParams.get('event_id'));assert(ids.has(selected));
  const detail=await popup.locator('#externalDetails').innerText();assert(detail.includes(String(selected)));assert(detail.includes('TRADECASE_BUS'));
  for(const id of['externalRefresh','externalDryRun','externalRetry','adapterRefresh'])assert(await popup.locator('#'+id).getAttribute('title'));
  assert.equal(await popup.locator('#externalSystem option[value=TRADECASE_BUS]').count(),1);
  report.checks.push({width,trip,selectedQueueMessage:selected,globalRefresh:true,deniedClears:true,errorIsSeparate:true});
  await popup.close();await ctx.close();
 }
 assert.equal(report.writes.length,0);assert.equal(report.errors.length,0);report.status='PASS';
})().catch(e=>{report.status='FAIL';report.error=String(e);process.exitCode=1;}).finally(async()=>{fs.writeFileSync(out+'/delivery-ui.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser?.close();});
