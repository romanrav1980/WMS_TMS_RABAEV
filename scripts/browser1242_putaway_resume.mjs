import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const path='tmp/context1238.json',ctx=JSON.parse(fs.readFileSync(path,'utf8'));
if(ctx.stage!=='PUTAWAY_STARTED')throw Error('Resume explicitly from retained context');
const receipts=[ctx.receipts[0].body];
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}});let logged=false;
 ctx.putaway=ctx.putaway||[];ctx.stage='PUTAWAY_STARTED';fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 for(const r of receipts){
  await page.goto('http://127.0.0.1:8088/wms-admin/warehouse-tasks.html?task_id='+r.task_id,{waitUntil:'domcontentloaded'});
  if(!logged){await page.locator('#adminLoginForm button[type=submit]').click();logged=true;}
  await page.waitForFunction(id=>warehouseTaskState.selectedTask?.task_id===id,r.task_id);
  for(const action of ['assign','start']){
   const expected=page.waitForResponse(res=>res.request().method()==='POST'&&res.url().endsWith('/'+r.task_id+'/'+action));
   await page.locator(action==='assign'?'#warehouseTaskAssign':'#warehouseTaskStart').click();
   const response=await expected;const body=await response.json();
   ctx.putaway.push({task:r.task_id,action,status:response.status(),body});fs.writeFileSync(path,JSON.stringify(ctx,null,2));
   if(!response.ok())throw Error(JSON.stringify(body));
   await page.waitForFunction(({id,status})=>warehouseTaskState.selectedTask?.task_id===id&&warehouseTaskState.selectedTask?.status===status,{id:r.task_id,status:action==='assign'?'ASSIGNED':'IN_PROGRESS'});
  }
  await page.locator('#warehouseTaskScanPallet').fill(r.pallet_identifier);
  await page.locator('#warehouseTaskScanFrom').fill(r.receive_cell);
  await page.locator('#warehouseTaskScanTo').fill(r.putaway_cell);
  const expected=page.waitForResponse(res=>res.request().method()==='POST'&&res.url().endsWith('/'+r.task_id+'/complete'));
  await page.locator('#warehouseTaskComplete').click();
  const response=await expected;const body=await response.json();
  ctx.putaway.push({task:r.task_id,action:'complete',status:response.status(),body});fs.writeFileSync(path,JSON.stringify(ctx,null,2));
  if(!response.ok())throw Error(JSON.stringify(body));
  await page.waitForFunction(id=>warehouseTaskState.selectedTask?.task_id===id&&warehouseTaskState.selectedTask?.status==='DONE',r.task_id);
 }
 ctx.stage='PUTAWAY_DONE';fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 await page.locator('#warehouseTaskDetail').scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/nicora/2026-10-13/screenshots/66-b01-putaway.png'});
 console.log(JSON.stringify({stage:ctx.stage,actions:ctx.putaway}));
}finally{await browser.close();}
