import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8088/wms-admin/resource-workload.html');await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>window.wmsAdminAuth?.state.user);
 await page.route('**/api/admin/auth/me',r=>r.abort());await page.reload();await page.locator('#adminRetrySession').waitFor();
 if(!await page.evaluate(()=>Boolean(sessionStorage.getItem('wmsAdminAuth'))&&!window.wmsAdminAuth.state.user&&document.body.classList.contains('auth-pending')))throw Error('Network error lost session or granted access');
 await page.unroute('**/api/admin/auth/me');await page.locator('#adminRetrySession').click();await page.waitForFunction(()=>window.wmsAdminAuth?.state.user);
 await page.route('**/api/admin/auth/me',r=>r.fulfill({status:503,contentType:'application/json',body:'{}'}));await page.reload();await page.locator('#adminRetrySession').waitFor();
 if(!await page.evaluate(()=>Boolean(sessionStorage.getItem('wmsAdminAuth'))&&!window.wmsAdminAuth.state.user))throw Error('503 lost session');
 await page.unroute('**/api/admin/auth/me');await page.route('**/api/admin/auth/me',r=>r.fulfill({status:401,contentType:'application/json',body:'{}'}));await page.locator('#adminRetrySession').click();
 await page.waitForFunction(()=>!sessionStorage.getItem('wmsAdminAuth'));if(await page.evaluate(()=>Boolean(window.wmsAdminAuth.state.user)))throw Error('401 allowed');
 if(errors.length)throw Error(JSON.stringify(errors));fs.writeFileSync('tmp/result1389.json',JSON.stringify({abortRetained:true,recoveredWithRealApi:true,unavailableRetained:true,unauthorizedCleared:true,errors},null,2));console.log('PASS: transient errors preserve session without granting access; real recovery; 401 clears session');
}finally{await browser.close();}