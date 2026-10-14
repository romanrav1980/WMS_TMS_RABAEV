import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const d=JSON.parse(fs.readFileSync('tmp/context1214.json','utf8'));
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1000,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8088/wms-admin/case-pick-tsd.html?case_task_id='+d.task,{waitUntil:'domcontentloaded'});
 await page.locator('#adminLoginForm button[type=submit]').click();
 await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));await page.locator('#cpTsdRefresh').click();
 await page.locator('#cpTypeActual').filter({hasText:'версия 2'}).waitFor();
 if(await page.locator('#cpTypeRestart').isVisible()||await page.locator('#cpTypeRetry').isVisible())throw Error('False recovery buttons');
 if(errors.length)throw Error(errors.join(';'));
 await page.locator('#cpTypePanel').scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/retailcase/2026-10-13/screenshots/58-case-type-styled-desktop.png'});
 await page.setViewportSize({width:390,height:844});await page.locator('#cpTypePanel').scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/retailcase/2026-10-13/screenshots/59-case-type-styled-mobile.png'});
 console.log('PASS1219 real current CASE/type/read-only/styled desktop+mobile/hidden recovery controls');
}finally{await browser.close();}
