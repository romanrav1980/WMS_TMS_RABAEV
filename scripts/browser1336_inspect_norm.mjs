import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 const open=async()=>{
  await page.goto('http://127.0.0.1:8088/wms-admin/warehouse-forecast.html');
  await page.locator('#adminLoginForm button[type=submit]').click();
  await page.waitForFunction(()=>window.wmsAdminAuth?.state.user);
  await page.locator('#wfWare').fill('9807');await page.locator('#wfHistory').fill('1');await page.locator('#wfHorizon').fill('1');await page.locator('#wfMinimum').fill('1');
  await page.locator('#wfScope').selectOption('FULLPAL_DISPATCH');await page.locator('#wfCurrent').check();
 };
 await open();await page.locator('#wfRead').click();await page.locator('#wfResult').waitFor({state:'visible'});
 const before=await page.locator('#wfLabourResult').innerText();if(!before.includes('Вид работы не связан'))throw Error(before);
 await page.getByText('Настроить связь вида работы с участком',{exact:true}).click();

 const response=page.waitForResponse(r=>r.url().includes('/api/resources/workload/warehouses/'));
 await page.locator('#wfNormLoad').click();const r=await response;console.log(JSON.stringify({status:r.status(),body:await r.json()}));
 await page.waitForFunction(()=>!document.querySelector('#wfNormLoad').disabled);
 console.log(JSON.stringify({message:await page.locator('#wfNormMessage').innerText(),options:await page.locator('#wfNormSites').innerHTML(),errors}));
}finally{await browser.close();}
