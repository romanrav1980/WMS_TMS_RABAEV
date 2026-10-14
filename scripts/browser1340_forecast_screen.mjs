import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 let visit=0;const open=async()=>{
  await page.goto('http://127.0.0.1:8088/wms-admin/warehouse-forecast.html');
  if(visit++===0)await page.locator('#adminLoginForm button[type=submit]').click();
  await page.waitForFunction(()=>window.wmsAdminAuth?.state.user);
  await page.locator('#wfWare').fill('9807');await page.locator('#wfHistory').fill('1');await page.locator('#wfHorizon').fill('1');await page.locator('#wfMinimum').fill('1');
  await page.locator('#wfScope').selectOption('FULLPAL_DISPATCH');await page.locator('#wfCurrent').check();
 };
 await open();await page.locator('#wfRead').click();await page.locator('#wfResult').waitFor({state:'visible'});

 await page.locator('#wfLabourResult details').first().evaluate(el=>el.open=true);
 await page.locator('.wf-resources').screenshot({path:'reports/nicora/2026-10-13/screenshots/87-ni081-forecast-hours.png'});
 console.log(JSON.stringify({text:await page.locator('#wfLabourResult').innerText(),errors}));
}finally{await browser.close();}
