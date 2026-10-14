import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const browser=await chromium.launch({headless:true});
try {
 const page=await browser.newPage({viewport:{width:1200,height:1000}}), errors=[], writes=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.method()==='POST'&&r.url().includes('/api/'))writes.push(r.url());});
 await page.goto('http://127.0.0.1:8088/wms-admin/warehouse-tasks.html?task_id=564#warehouseTaskDetail');
 await page.locator('#adminLoginForm button[type=submit]').click();
 await page.locator('#warehouseTaskDetailStatus').filter({hasText:'PLANNED'}).waitFor();
 if(!await page.locator('#warehouseTaskAssign').isEnabled())throw Error('Planned assignment blocked');
 await page.locator('#warehouseTaskDetail').screenshot({path:'reports/nicora/2026-10-13/screenshots/107-ni032-task-actions.png'});
 await page.locator('#warehouseTaskAssignee').fill('NO_MATCH_1411');
 // Only the POST reply is intercepted. No assignment or stock mutation reaches Oracle.
 await page.route('**/api/warehouse-tasks/564/assign',r=>r.fulfill({status:200,contentType:'application/json',body:'{}'}));
 const direct=page.waitForResponse(r=>r.url().endsWith('/warehouse-tasks/564')&&r.request().method()==='GET');
 await page.locator('#warehouseTaskAssign').click();
 if((await direct).status()!==200)throw Error('Pinned task not fetched');
 await page.locator('#warehouseTaskSelectionText').filter({hasText:'Выбрано задание 564'}).waitFor();
 const transitions=await page.evaluate(()=>{
  const result={};for(const status of ['PLANNED','ASSIGNED','IN_PROGRESS','DONE','CANCELLED']){
   window.warehouseTaskActions.render({task_id:564,status,assigned_to:'fixture'});
   result[status]=['warehouseTaskAssign','warehouseTaskStart','warehouseTaskComplete'].map(id=>!document.getElementById(id).disabled);
  }return result;
 });
 if(JSON.stringify(transitions)!==JSON.stringify({PLANNED:[true,true,true],ASSIGNED:[true,true,true],IN_PROGRESS:[false,false,true],DONE:[false,false,false],CANCELLED:[false,false,false]}))throw Error(JSON.stringify(transitions));
 if(errors.length)throw Error(JSON.stringify(errors));
 fs.writeFileSync('tmp/result1411.json',JSON.stringify({realTask:564,pinnedAfterInterceptedPost:true,transitions,interceptedPosts:writes,oracleMutations:0,errors},null,2));
 console.log(JSON.stringify({realTask:564,pinned:true,transitionStates:Object.keys(transitions),interceptedPosts:writes.length,oracleMutations:0,errors}));
} finally {await browser.close();}
