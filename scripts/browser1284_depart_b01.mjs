import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const path='tmp/context1238.json',ctx=JSON.parse(fs.readFileSync(path,'utf8'));
if(ctx.stage!=='B01_LOADED')throw Error('Retained loaded stage required');
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1080}});
 await page.goto('http://127.0.0.1:8088/wms-admin/transport-loading.html?trip_id=33571');
 await page.locator('#adminLoginForm button[type=submit]').click();
 await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 await page.waitForFunction(()=>!document.querySelector('#tripDepart').disabled);
 const pending=page.waitForResponse(r=>r.url().endsWith('/33571/depart')&&r.request().method()==='POST');
 await page.locator('#tripDepart').click();const r=await pending;
 ctx.departure={status:r.status(),request:r.request().postDataJSON(),body:await r.json()};
 fs.writeFileSync(path,JSON.stringify(ctx,null,2));console.log(JSON.stringify(ctx.departure));
 if(!r.ok())throw Error('Departure rejected, saved operation retained');
 await page.waitForFunction(()=>!window.wmsPhysicalLoadState.isBusy());
 ctx.stage='B01_DEPARTED';fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 await page.locator('#tripSummary').scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/nicora/2026-10-13/screenshots/78-b01-departed.png'});
}finally{await browser.close();}
