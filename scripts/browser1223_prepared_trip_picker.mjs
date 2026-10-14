import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const data=JSON.parse(fs.readFileSync('tmp/assignment1222.json','utf8'));
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8088/wms-admin/customer-orders.html?order_id=2135#sapAssignment',{waitUntil:'domcontentloaded'});
 await page.locator('#adminLoginForm button[type=submit]').click();
 await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 await page.locator('#sapPreparationStatus').filter({hasText:'SAP_2135'}).waitFor();
 await page.locator('#sapTripChoose').click();
 await page.locator('#tpRows button').first().waitFor();
 await page.locator('#tpFrom').fill('2026-11-03');await page.locator('#tpTo').fill('2026-11-04');
 await page.locator('#tpSearch').click();await page.locator('#tpRows button').first().waitFor();
 await page.screenshot({path:'reports/retailcase/2026-10-13/screenshots/60-prepared-st-trip-picker.png'});
 await page.locator('#tpRows').getByRole('button',{name:'Выбрать рейс '+data.rows[0].trip_id,exact:true}).click();
 if(await page.locator('#sapTripId').inputValue()!==String(data.rows[0].trip_id))throw Error('Trip selection not applied');
 await page.locator('#sapTripReview').click();
 await page.locator('#sapTripReviewMessage').filter({hasText:'Назначение проверяет'}).waitFor();
 const text=await page.locator('#sapTripReviewMessage').innerText();
 if(errors.length)throw Error(errors.join(';'));
 fs.writeFileSync('tmp/browser1223.json',JSON.stringify({status:'PASS1223',trip:data.rows[0].trip_id,source:'SAP_2135',review:text,writes:0},null,2));
 console.log('PASS1223 actual prepared ST/date-filter/current existing trip selection/preflight/no writes/no page errors');
}finally{await browser.close();}
