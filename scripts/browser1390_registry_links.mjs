import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage(),writes=[],results=[];page.on('request',r=>{if(r.method()==='POST'&&r.url().includes('/api/'))writes.push(r.url());});
 await page.goto('http://127.0.0.1:8088/wms-admin/day-reconciliation.html');await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>window.wmsAdminAuth?.state.user);
 for(const [screen,input,match]of [['interwarehouse','iwWare','/interwarehouse/warehouses/9807'],['supplier-handover','shWare','/supplier-handover/warehouses/9807'],['logistics-costs','lcWare','/logistics-costs/']]){
  const href=await page.evaluate(screen=>window.dayReconLinks.build({kind:'registry',href:screen+'.html'},{warehouse_id:9807,business_date:'2026-10-14'}).href,screen).catch(()=>screen+'.html?warehouse_id=9807');
  const responses=[];const listener=r=>{if(r.url().includes(match))responses.push({status:r.status(),url:r.url()});};page.on('response',listener);
  await page.goto('http://127.0.0.1:8088/wms-admin/'+href);await page.waitForFunction(id=>document.getElementById(id)?.value==='9807',input);
  await page.waitForLoadState('networkidle');page.off('response',listener);if(!responses.length||responses.some(r=>r.status!==200))throw Error(JSON.stringify({screen,responses}));results.push({screen,responses});
 }
 if(writes.length)throw Error('Unexpected mutation');fs.writeFileSync('tmp/result1390.json',JSON.stringify({results,writes},null,2));console.log(JSON.stringify({results,writes}));
}finally{await browser.close();}