import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const path='tmp/context1238.json',ctx=JSON.parse(fs.readFileSync(path,'utf8'));
if(ctx.stage!=='B01_DEPARTED')throw Error('Retained departed stage required');
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1080}});
 await page.goto('http://127.0.0.1:8088/wms-admin/wave-replenishment.html?wave_id=559#waveExecution');
 await page.locator('#adminLoginForm button[type=submit]').click();
 await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 ctx.wave_execution=await page.evaluate(async()=>{const r=await fetch(window.wmsAdminAuth.state.apiBase+'/api/picking/waves/559/execution',{headers:window.wmsAdminAuth.headers()});return {status:r.status,body:await r.json()};});
 fs.writeFileSync(path,JSON.stringify(ctx,null,2));console.log(JSON.stringify(ctx.wave_execution));
 if(ctx.wave_execution.body.ready&&!ctx.wave_execution.body.completed){
  await page.waitForFunction(()=>!document.querySelector('#waveExecution [data-release]').disabled);
  const pending=page.waitForResponse(r=>r.url().endsWith('/559/finish-execution')&&r.request().method()==='POST');
  await page.locator('#waveExecution [data-release]').click();const r=await pending;
  ctx.wave_finish={status:r.status(),request:r.request().postDataJSON(),body:await r.json()};
  fs.writeFileSync(path,JSON.stringify(ctx,null,2));console.log(JSON.stringify(ctx.wave_finish));if(!r.ok())throw Error('Finish rejected');
  await page.waitForFunction(()=>document.querySelector('#waveExecution [role=status]').textContent.includes('Решение завершения сохранено'));
 }
 ctx.execution_read=await page.evaluate(async()=>{const r=await fetch(window.wmsAdminAuth.state.apiBase+'/api/customer-orders/2135/execution',{headers:window.wmsAdminAuth.headers()});return {status:r.status,body:await r.json()};});
 fs.writeFileSync(path,JSON.stringify(ctx,null,2));console.log(JSON.stringify(ctx.execution_read));
 await page.locator('#waveExecution').scrollIntoViewIfNeeded();await page.screenshot({path:'reports/nicora/2026-10-13/screenshots/79-b01-wave-finished.png'});
}finally{await browser.close();}
