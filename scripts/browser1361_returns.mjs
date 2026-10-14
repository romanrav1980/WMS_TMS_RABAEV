import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}}),errors=[],writes=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.method()==='POST'&&/store-return/.test(r.url()))writes.push(r.url());});
 await page.goto('http://127.0.0.1:8088/wms-admin/store-returns.html');
 await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>window.wmsAdminAuth?.state.user);
 await page.locator('#returnSource').fill('STORE383.RECEIPT:c09bc5c0');await page.locator('#returnLoad').click();await page.locator('.return-progress-card').nth(1).waitFor();
 const completed=await page.locator('#returnHistory').innerText();
 await page.locator('#returnHistory').screenshot({path:'reports/nicora/2026-10-13/screenshots/92-ni062-return-route.png'});
 await page.getByRole('link',{name:'Возврат поставщику',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('#srRows')?.textContent.includes('EXRET'));
 const warehouse=await page.locator('#srWare').inputValue();
 await page.goto('http://127.0.0.1:8088/wms-admin/store-returns.html');await page.waitForFunction(()=>window.wmsAdminAuth?.state.user);
 await page.locator('#returnSource').fill('STORE642.RECEIPT:dc1889623c');await page.locator('#returnLoad').click();await page.locator('.return-progress-card').waitFor();
 const reuse=await page.locator('#returnHistory').innerText();
 await page.locator('#returnHistory').screenshot({path:'reports/nicora/2026-10-13/screenshots/93-ni062-marked-reuse-route.png'});
 await page.locator('#returnSource').fill('STORE.RECEIPT:da46b595-e71c-477b-b0ae-1f3292fdc0c1');
 if(await page.locator('.return-progress-card').count())throw Error('Stale return route');
 await page.locator('#returnLoad').click();await page.getByText('Согласованных возвратов этой приёмки пока нет.',{exact:true}).waitFor();
 const result={completed,reuse,warehouse,errors,writes};fs.writeFileSync('tmp/result1361.json',JSON.stringify(result,null,2));
 if(errors.length||writes.length||warehouse!=='38542432')throw Error('Unexpected side effects');console.log(JSON.stringify({warehouse,errors,writes}));
}finally{await browser.close();}
