import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const d=JSON.parse(fs.readFileSync('tmp/context1168.json','utf8'));
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1080}});
 await page.goto('http://127.0.0.1:8088/wms-admin/transport-loading.html',{waitUntil:'domcontentloaded',timeout:30000});
 await page.locator('#adminLoginForm button[type=submit]').click();
 await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user),{timeout:20000});
 await page.locator('#tripId').fill(String(d.trip_id));
 await page.locator('#tripLoad').click();
 await page.locator('#departTempProfile').filter({hasText:'Сохранён факт температуры выезда 3.75'}).waitFor({timeout:20000});
 if(!await page.locator('#tripRows').getByText('3.125 °C · вручную',{exact:true}).count())throw Error('Original loading confirmation not rendered');
 if(!await page.locator('#tripDepart').isDisabled())throw Error('Already departed trip offered another departure');
 await page.locator('#departTempProfile').scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/retailcase/2026-10-13/screenshots/47-loading-departure-temperature.png'});
 await page.setViewportSize({width:390,height:844});
 await page.locator('#departTempProfile').scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/retailcase/2026-10-13/screenshots/48-departure-temperature-mobile.png'});
 console.log('PASS1177 actual read-only original33636: load3.125/depart3.75/profile1, departed button disabled; desktop/mobile screenshots');
}finally{await browser.close();}
