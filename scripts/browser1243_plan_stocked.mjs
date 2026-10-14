import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const path='tmp/context1238.json',ctx=JSON.parse(fs.readFileSync(path,'utf8'));
if(ctx.stage!=='PUTAWAY_DONE')throw Error('Use retained context, no repeated new plan');
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}});
 await page.goto('http://127.0.0.1:8088/wms-admin/customer-orders.html?order_id=2135#sapAssignment',{waitUntil:'domcontentloaded'});
 await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 await page.locator('#sapPreparationStatus').filter({hasText:'SAP_2135'}).waitFor();await page.locator('#orderPickRefresh').click();
 const row=page.locator('#orderPickRows tr').filter({has:page.getByText('2189',{exact:true})});
 await row.getByRole('button',{name:'Отменить пустой план'}).click();
 await page.locator('#orderPickStatus').filter({hasText:'Пустой план отменён'}).waitFor();
 ctx.stage='PICK_REPLAN_STARTED';fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 const expected=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/api/picking/plans'));
 await page.locator('#orderPickCreate').click();const response=await expected;const result=await response.json();
 ctx.plan={status:response.status(),result};fs.writeFileSync(path,JSON.stringify(ctx,null,2));if(!response.ok())throw Error(JSON.stringify(result));
 await page.locator('#orderPickStatus').filter({hasText:'Сохранён план'}).waitFor();
 const actual=await page.evaluate(async id=>orderRequest('/api/picking/plans/'+id),result.pick_plan_id);
 ctx.plan.detail=actual;ctx.stage='PICK_PLAN_OBSERVED';fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 await page.locator('#orderPickingPanel').scrollIntoViewIfNeeded();await page.screenshot({path:'reports/retailcase/2026-10-13/screenshots/67-b01-stocked-plan.png'});
 await page.setViewportSize({width:430,height:900});await page.locator('#orderPickingPanel').scrollIntoViewIfNeeded();await page.screenshot({path:'reports/retailcase/2026-10-13/screenshots/68-b01-stocked-plan-mobile.png'});
 console.log(JSON.stringify({stage:ctx.stage,plan:actual}));
}finally{await browser.close();}
