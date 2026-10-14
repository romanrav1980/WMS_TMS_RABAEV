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
 const before=await page.locator('#wfLabourResult').innerText();
 await page.getByText('Настроить связь вида работы с участком',{exact:true}).click();
 await page.locator('#wfNormLoad').click();await page.locator('#wfNormSites').selectOption('OWN_B01_FULLPAL');
 await page.locator('#wfNormReason').fill('Own B01 dev explicit full-pallet workload site');
 let submitted=null,committed=null;
 await page.route('**/api/resources/workload/forecast-scopes',async route=>{
  submitted=route.request().postDataJSON();const response=await route.fetch();committed={status:response.status(),body:await response.json()};
  fs.writeFileSync('tmp/committed1334.json',JSON.stringify({submitted,committed},null,2));
  await route.abort('failed');
 });
 await page.locator('#wfNormSave').click();
 await page.waitForFunction(()=>document.querySelector('#wfNormMessage').textContent.includes('Повторите'));
 if(committed?.status!==200)throw Error(JSON.stringify(committed));
 await page.unroute('**/api/resources/workload/forecast-scopes');await open();
 await page.getByText('Настроить связь вида работы с участком',{exact:true}).click();
 const repeat=page.waitForResponse(r=>r.url().endsWith('/workload/forecast-scopes')&&r.request().method()==='POST');
 await page.locator('#wfNormRetry').click();const replay=await repeat;
 if(JSON.stringify(replay.request().postDataJSON())!==JSON.stringify(submitted))throw Error('Changed retry');
 const replayBody=await replay.json();if(JSON.stringify(replayBody)!==JSON.stringify(committed.body))throw Error('Changed result');
 await page.waitForFunction(()=>document.querySelector('#wfNormMessage').textContent.includes('Связь сохранена'));
 const view=page.waitForResponse(r=>r.url().endsWith('/9807/view'));await page.locator('#wfRead').click();const response=await view,data=await response.json();
 if(!response.ok()||data.labour_estimate?.status!=='COMPLETE_ESTIMATE')throw Error(JSON.stringify(data));
 await page.locator('#wfLabourResult').getByText(/Расчётные трудозатраты/).waitFor();
 await page.locator('#wfLabourResult').screenshot({path:'reports/retailcase/2026-10-13/screenshots/87-ni081-forecast-hours.png'});
 fs.writeFileSync('tmp/result1334.json',JSON.stringify({before,submitted,committed,replay:replayBody,forecast:data,errors},null,2));
 console.log(JSON.stringify({mapping:replayBody,labour:data.labour_estimate,errors}));
}finally{await browser.close();}
