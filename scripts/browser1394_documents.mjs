import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),writes=[],errors=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.method()==='POST'&&r.url().includes('/api/'))writes.push(r.url());});
 const response=page.waitForResponse(r=>r.url().includes('/day-reconciliation/warehouses/1?'));
 await page.goto('http://127.0.0.1:8088/wms-admin/day-reconciliation.html?warehouse_id=1&day=2026-10-14');await page.locator('#adminLoginForm button[type=submit]').click();
 const r=await response,data=await r.json();if(!data.current_backlog_documents)throw Error('New API not loaded');
 const a=page.locator('.dr-documents a').filter({hasText:/^564$/});await a.waitFor({state:'attached'});
 await a.locator('xpath=ancestor::details').evaluate(n=>n.open=true);
 await a.locator('xpath=ancestor::article').screenshot({path:'reports/nicora/2026-10-13/screenshots/101-ni072-backlog-documents.png'});
 const href=await a.getAttribute('href');if(href!=='warehouse-tasks.html?task_id=564')throw Error(href);
 await page.goto('http://127.0.0.1:8088/wms-admin/day-reconciliation.html?warehouse_id=38542432&day=2026-10-14');
 const doc=page.locator('.dr-documents a').filter({hasText:/^STORE383.RECEIPT:c09bc5c0$/});await doc.waitFor({state:'attached'});await doc.locator('xpath=ancestor::details').evaluate(n=>n.open=true);
 const caseRead=page.waitForResponse(r=>r.url().includes('/api/delivery/case-work/STORE383.RECEIPT'));
 await doc.click();const cr=await caseRead;if(cr.status()!==200)throw Error('Dossier read '+cr.status());
 if(await page.locator('#caseId').inputValue()!=='STORE383.RECEIPT:c09bc5c0')throw Error('Case context lost');
 if(writes.length||errors.length)throw Error(JSON.stringify({writes,errors}));
 fs.writeFileSync('tmp/result1394.json',JSON.stringify({task: data.current_backlog_documents.open_warehouse_tasks,href,caseStatus:cr.status(),writes,errors},null,2));console.log(JSON.stringify({status:r.status(),caseStatus:cr.status(),writes,errors}));
}finally{await browser.close();}