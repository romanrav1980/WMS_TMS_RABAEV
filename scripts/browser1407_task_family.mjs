import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1100}}),writes=[],errors=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.method()==='POST'&&r.url().includes('/api/'))writes.push(r.url());});
 const wait=page.waitForResponse(r=>r.url().endsWith('/warehouse-tasks/634/progress'));
 await page.goto('http://127.0.0.1:8088/wms-admin/warehouse-tasks.html?task_id=634#warehouseTaskDetail');await page.locator('#adminLoginForm button[type=submit]').click();
 const r=await wait,data=await r.json();if(r.status()!==200||data.confirmed_quantity!=='3'||data.remaining_quantity!=='0'||data.tasks.length!==2)throw Error('Unexpected actual chain '+JSON.stringify(data));
 await page.locator('#warehouseTaskFamily .wt-family-step').last().waitFor();
 if(await page.locator('#warehouseTaskFamily .wt-family-step').count()!==data.tasks.length)throw Error('Lost family row');
 await page.locator('#warehouseTaskFamily').screenshot({path:'reports/retailcase/2026-10-13/screenshots/105-ni032-task-family.png'});
 const parent=page.locator('#warehouseTaskFamily a').filter({hasText:/^#633$/});const parentRead=page.waitForResponse(r=>r.url().endsWith('/warehouse-tasks/633/progress'));await parent.click();if((await parentRead).status()!==200)throw Error('Parent link failed');
 await page.setViewportSize({width:390,height:844});await page.locator('#warehouseTaskFamily').evaluate(n=>n.scrollIntoView({block:'start'}));await page.locator('#warehouseTaskFamily').screenshot({path:'reports/retailcase/2026-10-13/screenshots/106-ni032-task-family-mobile.png'});
 const box=await page.locator('#warehouseTaskFamily').boundingBox();if(!box||box.width>390)throw Error('Family panel too wide');
 await page.goto('http://127.0.0.1:8088/wms-admin/warehouse-tasks.html?task_id=564#warehouseTaskDetail');await page.locator('#warehouseTaskFamily').waitFor();
 const next=page.locator('#warehouseTaskFamily a').filter({hasText:'Открыть следующее задание #564'});if(await next.count()!==1)throw Error('Active next step missing');
 if(writes.length||errors.length)throw Error(JSON.stringify({writes,errors}));fs.writeFileSync('tmp/result1407.json',JSON.stringify({family:data,parentRead:200,activeNext:564,writes,errors},null,2));console.log(JSON.stringify({root:data.root_task_id,confirmed:data.confirmed_quantity,remaining:data.remaining_quantity,steps:data.tasks.length,activeNext:564,writes,errors}));
}finally{await browser.close();}