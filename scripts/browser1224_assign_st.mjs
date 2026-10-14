import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const ctx=JSON.parse(fs.readFileSync('tmp/context1224.json','utf8'));
if(ctx.state!=='UNASSIGNED')throw Error('Retained assignment changed; no fixture repeat');
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));let posted;
 page.on('request',r=>{if(r.method()==='POST'&&r.url().endsWith('/tasks/'+ctx.trip+'/sts'))posted=JSON.parse(r.postData());});
 await page.goto('http://127.0.0.1:8088/wms-admin/customer-orders.html?order_id=2135#sapAssignment',{waitUntil:'domcontentloaded'});
 await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 await page.locator('#sapPreparationStatus').filter({hasText:'SAP_2135'}).waitFor();
 await page.locator('#sapTripChoose').click();
 await page.locator('#tpRows').getByRole('button',{name:'Выбрать рейс '+ctx.trip,exact:true}).click();
 await page.locator('#sapTripReview').click();await page.locator('#sapTripReviewMessage').filter({hasText:'Вместимость проверена'}).waitFor();
 await page.locator('#sapAssignSt').click();await page.locator('#sapPreparationStatus').filter({hasText:'добавлена в рейс '+ctx.trip}).waitFor();
 if(!posted)throw Error('Existing assignment POST absent');
 ctx.state='ASSIGNED_HTTP';ctx.body=posted;fs.writeFileSync('tmp/context1224.json',JSON.stringify(ctx,null,2));
 const repeat=await page.evaluate(async({trip,body})=>{
  const r=await fetch(window.wmsAdminAuth.state.apiBase+'/api/admin/transport/tasks/'+trip+'/sts',
   {method:'POST',headers:{...window.wmsAdminAuth.headers(),'Content-Type':'application/json'},body:JSON.stringify(body)});
  const value=await r.json();if(!r.ok)throw Error(JSON.stringify(value));return value;
 },{trip:ctx.trip,body:posted});
 if(errors.length)throw Error(errors.join(';'));
 ctx.state='ASSIGNED_REPEATED';ctx.repeat=repeat;fs.writeFileSync('tmp/context1224.json',JSON.stringify(ctx,null,2));
 await page.locator('#sapAssignment').scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/nicora/2026-10-13/screenshots/61-auto-st-assigned-existing-trip.png'});
 console.log('PASS1224 original UI/API assigned SAP_2135→33571 and repeated original request; native counts/stock verify next');
}finally{await browser.close();}
