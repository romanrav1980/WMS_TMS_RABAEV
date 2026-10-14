import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const path='tmp/context1238.json',ctx=JSON.parse(fs.readFileSync(path,'utf8'));
if(!['WAVE_LAUNCH_STARTED','IDENTITY_REPLAN_STARTED'].includes(ctx.stage))throw Error('Unexpected retained stage');
ctx.identity_fix??={old_plan:ctx.plan,old_wave:ctx.wave_id,old_launch:ctx.launch,cancel_operation:'WAVE.CANCEL.IDENTITY:'+crypto.randomUUID(),actions:[]};
ctx.stage='IDENTITY_REPLAN_STARTED';fs.writeFileSync(path,JSON.stringify(ctx,null,2));
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}});
 await page.goto('http://127.0.0.1:8088/wms-admin/customer-orders.html?order_id=2135#sapAssignment',{waitUntil:'domcontentloaded'});
 await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 await page.locator('#sapPreparationStatus').filter({hasText:'SAP_2135'}).waitFor();
 for(const [kind,url,body]of [
 ['cancel_wave','/api/picking/waves/'+ctx.identity_fix.old_wave+'/cancel',{operation_id:ctx.identity_fix.cancel_operation,reason:'Replan exact canonical article after planner correction'}],
 ['cancel_plan','/api/picking/plans/'+ctx.identity_fix.old_plan.result.pick_plan_id+'/cancel',{}]]){
  if(ctx.identity_fix.actions.some(a=>a.kind===kind))continue;
  const result=await page.evaluate(async({url,body})=>orderRequest(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),{url,body});
  ctx.identity_fix.actions.push({kind,result});fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 }
 await page.locator('#orderPickRefresh').click();
 const expected=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/api/picking/plans'));
 await page.locator('#orderPickCreate').click();const response=await expected;const result=await response.json();
 ctx.plan={status:response.status(),result};fs.writeFileSync(path,JSON.stringify(ctx,null,2));if(!response.ok())throw Error(JSON.stringify(result));
 await page.locator('#orderPickStatus').filter({hasText:'Сохранён план'}).waitFor();
 ctx.plan.detail=await page.evaluate(id=>orderRequest('/api/picking/plans/'+id),result.pick_plan_id);
 ctx.stage='PICK_PLAN_OBSERVED';fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 await page.setViewportSize({width:430,height:900});await page.locator('#orderPickingPanel').scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/nicora/2026-10-13/screenshots/71-b01-canonical-plan-mobile.png'});
 console.log(JSON.stringify({stage:ctx.stage,plan:ctx.plan.detail}));
}finally{await browser.close();}
