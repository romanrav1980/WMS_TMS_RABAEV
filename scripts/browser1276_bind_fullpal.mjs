import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const path='tmp/context1238.json',ctx=JSON.parse(fs.readFileSync(path,'utf8'));
if(ctx.stage!=='LAYOUT_RECONCILED')throw Error('Retained layout must be reconciled');
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}});let logged=false;const errors=[];page.on('pageerror',e=>errors.push(e.message));
 ctx.stage='FULLPAL_BIND_STARTED';ctx.fullpal_bind=[];fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 for(let i=0;i<ctx.staging_tasks.length;i++){
  const task=ctx.staging_tasks[i],st='OP_SAP_2135_'+(i+1);
  await page.goto('http://127.0.0.1:8088/wms-admin/warehouse-tasks.html?task_id='+task.warehouse_task_id+'#fullpalShipment',{waitUntil:'domcontentloaded'});
  if(!logged){await page.locator('#adminLoginForm button[type=submit]').click();logged=true;}
  await page.waitForFunction(id=>warehouseTaskState.selectedTask?.task_id===id,task.warehouse_task_id);
  const panel=page.locator('#fullpalShipment');
  await panel.locator('[data-task]').fill(String(task.warehouse_task_id));await panel.locator('[data-preview]').click();
  await panel.locator('[data-fact]').filter({hasText:task.pallet_uid}).waitFor();
  await panel.locator('[data-pallet]').fill(task.pallet_uid);await panel.locator('[data-shipment]').fill(st);
  const expected=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/full-pallet-shipment'));
  await panel.locator('[data-bind]').click();const response=await expected;const body=await response.json();
  ctx.fullpal_bind.push({task_id:task.warehouse_task_id,shipment:st,status:response.status(),body,request:response.request().postDataJSON()});
  fs.writeFileSync(path,JSON.stringify(ctx,null,2));if(!response.ok())throw Error(JSON.stringify(body));
  await panel.locator('[role=status]').filter({hasText:'связана с местом СТ'}).waitFor();
 }
 ctx.stage='FULLPAL_BOUND';fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 await page.locator('#fullpalShipment').scrollIntoViewIfNeeded();await page.screenshot({path:'reports/nicora/2026-10-13/screenshots/76-b01-fullpal-bound.png'});
 console.log(JSON.stringify({stage:ctx.stage,bindings:ctx.fullpal_bind,errors}));
 if(errors.length)throw Error(errors.join(';'));
}finally{await browser.close();}
