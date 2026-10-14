import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),writes=[];
 page.on('request',r=>{if(r.method()==='POST'&&r.url().includes('/api/warehouse-hus'))writes.push(r.postDataJSON());});
 await page.goto('http://127.0.0.1:8088/wms-admin/warehouse-hus.html?identifier=HU1069%3A4bb85f1f15');
 await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>window.wmsAdminAuth?.state.user);
 await page.locator('.hu-tree-select').nth(2).waitFor();await page.locator('#huMove').click();
 await page.getByText('Отсканируйте внешнее грузовое место перед операцией.',{exact:true}).waitFor();
 if(writes.length)throw Error('Search identifier used as physical scan');
 await page.locator('#huContainerScan').fill('WRONG.SCAN.1368');await page.locator('#huFrom').fill('QW4bb85f1f15');await page.locator('#huTo').fill('QW4bb85f1f15');
 const response=page.waitForResponse(r=>r.url().endsWith('/api/warehouse-hus/move')&&r.request().method()==='POST');
 await page.locator('#huMove').click();const r=await response,result=await r.json();
 fs.writeFileSync('tmp/result1368.json',JSON.stringify({status:r.status(),result,writes},null,2));
 if(r.status()!==409||writes.length!==1||writes[0].scan_container!=='WRONG.SCAN.1368')throw Error('Unexpected scan result');
 await page.locator('#huContainerScan').fill('');await page.locator('#huLoad').click();await page.locator('.hu-tree-select').nth(2).waitFor();
 await page.locator('#huComposition').screenshot({path:'reports/nicora/2026-10-13/screenshots/96-ni041-explicit-scan.png'});
 console.log(JSON.stringify({status:r.status(),result}));
}finally{await browser.close();}
