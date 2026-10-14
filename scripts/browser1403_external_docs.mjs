import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),writes=[],errors=[],reads=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.method()==='POST'&&r.url().includes('/api/'))writes.push(r.url());if(r.url().includes('/api/admin/event-outbox'))reads.push(r.url());});
 await page.goto('http://127.0.0.1:8088/wms-admin/day-reconciliation.html?warehouse_id=38542432&day=2026-10-14');await page.locator('#adminLoginForm button[type=submit]').click();
 const link=page.locator('.dr-documents a[href*="external-outbox.html?event_id="]').first();await link.waitFor({state:'attached'});await link.locator('xpath=ancestor::details').evaluate(n=>n.open=true);
 await link.locator('xpath=ancestor::article').screenshot({path:'reports/retailcase/2026-10-13/screenshots/103-ni072-external-documents.png'});
 const href=await link.getAttribute('href'),id=new URL(href,'http://localhost').searchParams.get('event_id');const wait=page.waitForResponse(r=>r.url().endsWith('/api/admin/event-outbox/'+id));await link.click();const r=await wait;if(r.status()!==200)throw Error('Detail '+r.status());
 await page.waitForFunction(id=>document.getElementById('externalDetails').textContent.includes(id),id);
 await page.locator('#externalDetails').screenshot({path:'reports/retailcase/2026-10-13/screenshots/104-ni072-external-message.png'});
 if(reads.some(url=>url.includes('/api/admin/event-outbox?')))throw Error('Unnecessary queue list on deep link');
 if(writes.length||errors.length)throw Error(JSON.stringify({writes,errors}));fs.writeFileSync('tmp/result1403.json',JSON.stringify({id,status:r.status(),reads,writes,errors},null,2));console.log(JSON.stringify({id,status:r.status(),reads,writes,errors}));
}finally{await browser.close();}