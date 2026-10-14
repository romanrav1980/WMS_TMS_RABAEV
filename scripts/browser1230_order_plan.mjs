import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
if(fs.existsSync('tmp/browser1230.json'))throw Error('Retained plan case; do not repeat create');
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));let answer;
 page.on('response',async r=>{if(r.request().method()==='POST'&&r.url().endsWith('/api/picking/plans'))answer={status:r.status(),body:await r.json()};});
 await page.goto('http://127.0.0.1:8088/wms-admin/customer-orders.html?order_id=2135#sapAssignment',{waitUntil:'domcontentloaded'});
 await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 await page.locator('#sapPreparationStatus').filter({hasText:'SAP_2135'}).waitFor();
 await page.locator('#orderPickRefresh').click();
 await page.locator('#orderPickStatus').filter({hasText:'Планов нет'}).waitFor();
 await page.locator('#orderPickCreate').click();
 await page.waitForFunction(()=>document.querySelector('#orderPickStatus').textContent.includes('Сохранён план')||document.querySelector('#orderPickStatus').textContent.includes('Создание сохранено'));
 await page.waitForTimeout(200);
 if(!answer)throw Error('Existing picking API was not called');
 if(errors.length)throw Error(errors.join(';'));
 const text=await page.locator('#orderPickStatus').innerText();
 if(answer.status>=500)throw Error('Unclassified server error: '+JSON.stringify(answer));
 await page.locator('#orderPickStatus').scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/nicora/2026-10-13/screenshots/63-order-picking-workspace.png'});
 fs.writeFileSync('tmp/browser1230.json',JSON.stringify({status:'OBSERVED1230',answer,text,writes:1},null,2));
 console.log(JSON.stringify({status:'OBSERVED1230',answer,message:text}));
}finally{await browser.close();}
