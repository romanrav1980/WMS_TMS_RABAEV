import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}}),writes=[],errors=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.method()==='POST'&&r.url().includes('/api/')&&!r.url().endsWith('/preview'))writes.push(r.url());});
 await page.goto('http://127.0.0.1:8088/wms-admin/resource-workload.html');await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>window.wmsAdminAuth?.state.user);
 await page.locator('#rwWare').fill('6667491');await page.locator('#rwSite').fill('QA134');
 for(const id of ['rwViewStart','rwWaveStart'])await page.locator('#'+id).fill('2026-10-14T16:00');
 for(const id of ['rwViewFinish','rwWaveFinish'])await page.locator('#'+id).fill('2026-10-14T18:00');
 await page.locator('#rwWave').fill('395');await page.locator('#rwAddWindow').click();
 const wait=page.waitForResponse(r=>r.url().endsWith('/warehouses/6667491/preview'));await page.locator('#rwPreview').click();const r=await wait,data=await r.json();
 await page.locator('.rw-interval').first().waitFor();
 if(r.status()!==200||data.stock_changed||data.plan_applied)throw Error('Unexpected preview');
 const count=await page.locator('.rw-deficit').count();if(!count)throw Error('No actual deficit displayed');
 await page.getByLabel('Интервалы нагрузки').selectOption('deficit');
 await page.locator('.rw-overview').screenshot({path:'reports/nicora/2026-10-13/screenshots/98-ni081-workload-intervals.png'});
 await page.getByRole('button',{name:'Подставить интервал в план выхода',exact:true}).first().click();
 if(!await page.locator('#rwStart').inputValue())throw Error('Existing recommendation did not fill form');
 await page.setViewportSize({width:390,height:844});if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Mobile horizontal overflow');await page.locator('.rw-overview').screenshot({path:'reports/nicora/2026-10-13/screenshots/99-ni081-workload-mobile.png'});
 await page.locator('#rwViewFinish').fill('2026-10-14T19:00');if(await page.locator('.rw-overview').count())throw Error('Old result not cleared');
 if(writes.length||errors.length)throw Error(JSON.stringify({writes,errors}));
 fs.writeFileSync('tmp/result1385.json',JSON.stringify({data,count,writes,errors},null,2));console.log(JSON.stringify({status:r.status(),count,writes,errors}));
}finally{await browser.close();}