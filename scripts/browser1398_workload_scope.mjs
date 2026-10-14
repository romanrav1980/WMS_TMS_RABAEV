import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),writes=[],errors=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.method()==='POST'&&r.url().includes('/api/'))writes.push(r.url());});
 await page.goto('http://127.0.0.1:8088/wms-admin/resource-workload.html');await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>window.wmsAdminAuth?.state.user);
 await page.locator('#rwWare').fill('6667491');await page.locator('#rwSite').fill('QA134');
 await page.locator('#rwViewStart').fill('2026-10-01T00:00');await page.locator('#rwViewFinish').fill('2026-11-01T00:00');
 const wait=page.waitForResponse(r=>r.url().includes('/workload/warehouses/6667491?'));await page.locator('#rwRefresh').click();const response=await wait,data=await response.json();
 if(response.status()!==200||data.selection.site_code!=='QA134'||data.planned_attendance.length!==1)throw Error('Unexpected scope '+JSON.stringify(data));
 await page.waitForFunction(()=>document.getElementById('rwAttendance').textContent.includes('QA134'));
 await page.locator('#rwAttendance').locator('xpath=ancestor::section').screenshot({path:'reports/retailcase/2026-10-13/screenshots/102-ni081-scoped-attendance.png'});
 await page.locator('#rwSite').fill('NO_SUCH_1398');const emptyWait=page.waitForResponse(r=>r.url().includes('site_code=NO_SUCH_1398'));await page.locator('#rwRefresh').click();const empty=await(await emptyWait).json();if(empty.norms.length||empty.planned_attendance.length)throw Error('Scope leak');
 if(writes.length||errors.length)throw Error(JSON.stringify({writes,errors}));fs.writeFileSync('tmp/result1398.json',JSON.stringify({status:response.status(),selection:data.selection,attendance:data.planned_attendance.map(r=>r.plan_operation_id),empty:true,writes,errors},null,2));console.log(JSON.stringify({status:response.status(),rows:data.planned_attendance.length,empty:true,writes,errors}));
}finally{await browser.close();}