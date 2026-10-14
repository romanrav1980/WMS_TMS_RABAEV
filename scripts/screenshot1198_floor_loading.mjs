import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const d=JSON.parse(fs.readFileSync('tmp/context1194.json','utf8'));
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1080}});
 await page.goto('http://127.0.0.1:8088/wms-admin/transport-loading.html',{waitUntil:'domcontentloaded'});
 await page.locator('#adminLoginForm button[type=submit]').click();
 await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 await page.locator('#tripId').fill(String(d.trip_id));await page.locator('#tripLoad').click();
 await page.locator('#tripRows').getByText('Европоддон',{exact:true}).waitFor();
 await page.locator('#departTempProfile').filter({hasText:'Норматив тары на выезде подтверждён'}).waitFor();
 if(!await page.locator('#tripDepart').isDisabled())throw Error('Completed departure enabled');
 await page.locator('#tripSummary').scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/nicora/2026-10-13/screenshots/51-physical-top-tare-proof.png'});
 await page.setViewportSize({width:390,height:844});
 await page.locator('#departTempProfile').scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/nicora/2026-10-13/screenshots/52-physical-top-departure-mobile.png'});
 console.log('PASS1198 actual33637/typeEU/oneTOP/departure normative proof/read-only UI screenshots');
}finally{await browser.close();}
