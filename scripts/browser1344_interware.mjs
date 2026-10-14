import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}}),errors=[],writes=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.method()==='POST'&&r.url().includes('/api/inventory/interwarehouse'))writes.push(r.url());});
 await page.goto('http://127.0.0.1:8088/wms-admin/interwarehouse.html');
 await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>window.wmsAdminAuth?.state.user);
 await page.locator('#iwWare').fill('59619048');await page.locator('#iwHistory').check();
 await page.locator('#iwLoad').click();await page.locator('.iw-flow-card').first().waitFor();
 await page.locator('.iw-flow-card').first().click();
 const single=await page.locator('#iwFlowDetail').innerText();
 await page.locator('.iw-board').screenshot({path:'reports/nicora/2026-10-13/screenshots/88-b04-interwarehouse-route.png'});
 await page.getByRole('button',{name:'История / расхождения',exact:true}).click();
 if(!await page.locator('#iwDecisionHistory').isVisible())throw Error('Existing form not opened');
 await page.locator('#iwWare').fill('56524567');
 if(await page.locator('.iw-flow-card').count())throw Error('Stale warehouse cards');
 await page.locator('#iwLoad').click();await page.locator('#iwGroupLinks a').first().waitFor();
 await page.locator('#iwGroupLinks a').first().click();
 await page.waitForFunction(()=>document.querySelector('#ggState')?.textContent?.length>0);
 const group=await page.locator('#ggState').innerText(),lots=await page.locator('#ggLots').innerText();
 await page.locator('main > section').first().screenshot({path:'reports/nicora/2026-10-13/screenshots/89-b04-group-link.png'});
 fs.writeFileSync('tmp/result1344.json',JSON.stringify({single,group,lots,errors,writes},null,2));
 console.log(JSON.stringify({single,group,errors,writes}));if(errors.length||writes.length)throw Error('Unexpected error or write');
}finally{await browser.close();}
