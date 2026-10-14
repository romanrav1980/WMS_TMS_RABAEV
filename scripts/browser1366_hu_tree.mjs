import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}}),errors=[],writes=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.method()==='POST'&&r.url().includes('/api/warehouse-hus'))writes.push(r.url());});
 await page.goto('http://127.0.0.1:8088/wms-admin/warehouse-hus.html?identifier=HU1069%3A4bb85f1f15');
 await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>window.wmsAdminAuth?.state.user);
 await page.locator('.hu-tree-select').nth(2).waitFor();await page.locator('.hu-tree-select').nth(1).click();
 const live=await page.locator('.hu-tree-workspace').innerText();await page.locator('.hu-tree-workspace').screenshot({path:'reports/retailcase/2026-10-13/screenshots/94-ni041-hu-tree.png'});
 await page.getByRole('link',{name:'Открыть состав этого вложения',exact:true}).click();await page.locator('.hu-tree-ancestors').waitFor();
 const child=await page.locator('.hu-tree-ancestors').innerText();
 await page.locator('#huIdentifier').fill('SMALL514.HU:af32399b');
 if(await page.locator('.hu-tree-select').count())throw Error('Stale tree after identifier changed');
 if(!await page.locator('#huMove').isDisabled())throw Error('Movement enabled without current read');
 await page.locator('#huLoad').click();await page.getByText('Исторический состав на момент отгрузки. Операции изменения недоступны.',{exact:true}).waitFor();
 if(!await page.locator('#huMove').isDisabled()||!await page.locator('#huUnpack').isDisabled())throw Error('Historical mutations enabled');
 await page.locator('.hu-tree-workspace').screenshot({path:'reports/retailcase/2026-10-13/screenshots/95-ni041-historical-tree.png'});
 fs.writeFileSync('tmp/result1366.json',JSON.stringify({live,child,errors,writes},null,2));
 console.log(JSON.stringify({child,errors,writes}));if(errors.length||writes.length)throw Error('Browser error or write');
}finally{await browser.close();}
