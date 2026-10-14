import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const path='tmp/context1238.json',ctx=JSON.parse(fs.readFileSync(path,'utf8'));
if(ctx.stage!=='PICK_PLAN_OBSERVED'||ctx.plan.detail.status!=='PLANNED_FULL')throw Error('Retained flow is not ready');
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8088/wms-admin/customer-orders.html?order_id=2135#sapAssignment',{waitUntil:'domcontentloaded'});
 await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 await page.locator('#sapPreparationStatus').filter({hasText:'SAP_2135'}).waitFor();await page.locator('#orderPickRefresh').click();
 await page.locator('#opWavePlan').selectOption(String(ctx.plan.result.pick_plan_id));
 await page.locator('#opWaveName').fill('B01 заказ2135 — штатное исполнение');
 ctx.stage='WAVE_PLANNING_STARTED';ctx.wave_actions=[];fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 for(const [button,suffix]of [['opWaveCreate','/api/picking/waves'],['opWaveAdd','/plans'],['opWaveCalculate','/calculate']]){
  const expected=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith(suffix));
  await page.locator('#'+button).click();const response=await expected;const text=await response.text();let body;try{body=JSON.parse(text);}catch{body={message:text};}
  ctx.wave_actions.push({button,status:response.status(),body});
  ctx.wave_pending=await page.evaluate(()=>Object.fromEntries(Object.keys(localStorage).filter(k=>k.startsWith('retailcase.orderWave:')).map(k=>[k,localStorage.getItem(k)])));
  fs.writeFileSync(path,JSON.stringify(ctx,null,2));if(!response.ok())throw Error(JSON.stringify(body));
  if(button==='opWaveCreate'){ctx.wave_id=body.pick_wave_id;fs.writeFileSync(path,JSON.stringify(ctx,null,2));await page.locator('#opWaveStatus').filter({hasText:'Волна создана'}).waitFor();}
  if(button==='opWaveAdd')await page.locator('#opWaveStatus').filter({hasText:'План включён'}).waitFor();
  if(button==='opWaveCalculate')await page.locator('#opWaveStatus').filter({hasText:'Расчёт волны сохранён'}).waitFor();
 }
 if(errors.length)throw Error(errors.join(';'));
 ctx.stage='WAVE_PREVIEW';ctx.wave_detail=await page.evaluate(id=>orderRequest('/api/picking/waves/'+id),ctx.wave_id);
 ctx.wave_readiness=await page.evaluate(id=>orderRequest('/api/picking/waves/'+id+'/readiness'),ctx.wave_id);
 fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 await page.locator('#orderWavePlanning').scrollIntoViewIfNeeded();await page.screenshot({path:'reports/retailcase/2026-10-13/screenshots/69-b01-wave-planning.png'});
 console.log(JSON.stringify({stage:ctx.stage,wave:ctx.wave_id,readiness:ctx.wave_readiness}));
}finally{await browser.close();}
