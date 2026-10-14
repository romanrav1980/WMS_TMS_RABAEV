import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:600,height:950}}),writes=[],errors=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.method()==='POST'&&r.url().includes('/api/'))writes.push(r.url());});
 await page.goto('http://127.0.0.1:8088/wms-admin/case-pick-tsd.html?case_task_id=1134');await page.locator('#adminLoginForm button[type=submit]').click();await page.locator('.cp-next-step').waitFor();
 await page.getByRole('link',{name:'Перейти к связи со СТ',exact:true}).click();
 if(await page.locator('#cpTsdShipmentIdentifier').inputValue())throw Error('Auto physical identifier');
 await page.locator('.cp-next-step').screenshot({path:'reports/retailcase/2026-10-13/screenshots/100-ni051-case-next-step.png'});
 await page.goto('http://127.0.0.1:8088/wms-admin/case-pick-tsd.html?case_task_id=1131');await page.locator('.cp-next-step').waitFor();
 const control=page.getByRole('link',{name:'Открыть контроль',exact:true}),href=await control.getAttribute('href');
 if(!href.includes('qc_shipment=')||!href.endsWith('#outgoingQuality'))throw Error('Wrong control link');
 if(errors.length||writes.length)throw Error(JSON.stringify({errors,writes}));
 fs.writeFileSync('tmp/result1387.json',JSON.stringify({href,errors,writes},null,2));console.log(JSON.stringify({href,errors,writes}));
}finally{await browser.close();}