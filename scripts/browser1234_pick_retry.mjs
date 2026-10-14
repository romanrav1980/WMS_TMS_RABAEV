import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
if(fs.existsSync('tmp/browser1234.json'))throw Error('Retained case; do not rerun');
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8088/wms-admin/customer-orders.html?order_id=2135#sapAssignment',{waitUntil:'domcontentloaded'});
 await page.locator('#adminLoginForm button[type=submit]').click();
 await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 await page.locator('#sapPreparationStatus').filter({hasText:'SAP_2135'}).waitFor();
 await page.locator('#orderPickRefresh').click();
 await page.locator('#orderPickRows').getByText('2187',{exact:true}).waitFor();
 fs.writeFileSync('tmp/browser1234.json',JSON.stringify({stage:'STARTED',order:2135,old_plan:2187}));
 await page.locator('#orderPickRows').getByRole('button',{name:'Отменить пустой план'}).click();
 await page.locator('#orderPickStatus').filter({hasText:'Пустой план отменён'}).waitFor();
 let original;
 await page.route('**/api/picking/plans',async route=>{
  if(route.request().method()!=='POST'){await route.continue();return;}
  const r=await route.fetch();original={status:r.status(),body:await r.json()};
  fs.writeFileSync('tmp/browser1234.json',JSON.stringify({stage:'COMMITTED_RESPONSE',original}));
  await route.abort('failed');
 });
 await page.locator('#orderPickCreate').click();
 await page.locator('#orderPickStatus').filter({hasText:'Создание сохранено'}).waitFor();
 if(original?.status!==200||!original.body.operation_id)throw Error('Original command failed: '+JSON.stringify(original));
 await page.unroute('**/api/picking/plans');
 const replayPromise=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/api/picking/plans'));
 await page.locator('#orderPickRetry').click();
 const replayResponse=await replayPromise;const replay=await replayResponse.json();
 await page.locator('#orderPickStatus').filter({hasText:'Сохранён план'}).waitFor();
 if(replayResponse.status()!==200||JSON.stringify(replay)!==JSON.stringify(original.body))throw Error('Replay mismatch');
 if(errors.length)throw Error(errors.join(';'));
 await page.locator('#orderPickStatus').scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/retailcase/2026-10-13/screenshots/64-pick-plan-retry.png'});
 const result={stage:'PASS',original,replay,message:await page.locator('#orderPickStatus').innerText()};
 fs.writeFileSync('tmp/browser1234.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));
}finally{await browser.close();}
