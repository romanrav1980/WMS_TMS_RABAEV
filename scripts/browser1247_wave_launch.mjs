import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const path='tmp/context1238.json',ctx=JSON.parse(fs.readFileSync(path,'utf8'));
if(ctx.stage!=='WAVE_PREVIEW')throw Error('Resume retained launch explicitly');
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}});
 await page.goto('http://127.0.0.1:8088/wms-admin/customer-orders.html?order_id=2135#sapAssignment',{waitUntil:'domcontentloaded'});
 await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 await page.locator('#sapPreparationStatus').filter({hasText:'SAP_2135'}).waitFor();await page.locator('#orderPickRefresh').click();
 await page.locator('#opWaveRead').click();await page.locator('#opWaveSelect').selectOption(String(ctx.wave_id));await page.waitForFunction(()=>!document.querySelector('#opWaveLaunch').disabled);
 ctx.stage='WAVE_LAUNCH_STARTED';fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 const expected=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/'+ctx.wave_id+'/launch'));
 await page.locator('#opWaveLaunch').click();const response=await expected;const text=await response.text();let body;try{body=JSON.parse(text);}catch{body={message:text};}
 ctx.launch={status:response.status(),body};ctx.wave_pending=await page.evaluate(()=>Object.fromEntries(Object.keys(localStorage).filter(k=>k.startsWith('nicora.orderWave:')).map(k=>[k,localStorage.getItem(k)])));fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 if(!response.ok())throw Error(JSON.stringify(body));
 await page.locator('#opWaveStatus').filter({hasText:'Волна запущена'}).waitFor();
 ctx.stage='WAVE_LAUNCHED';ctx.wave_tasks=await page.evaluate(id=>orderRequest('/api/picking/waves/'+id+'/tasks'),ctx.wave_id);
 ctx.execution=await page.evaluate(id=>orderRequest('/api/picking/waves/'+id+'/execution'),ctx.wave_id);
 fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 await page.locator('#orderWavePlanning').scrollIntoViewIfNeeded();await page.screenshot({path:'reports/nicora/2026-10-13/screenshots/70-b01-wave-launched.png'});
 console.log(JSON.stringify({stage:ctx.stage,wave:ctx.wave_id,tasks:ctx.wave_tasks,execution:ctx.execution}));
}finally{await browser.close();}
