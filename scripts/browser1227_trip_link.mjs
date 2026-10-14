import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8088/wms-admin/customer-orders.html?order_id=2135#sapAssignment',{waitUntil:'domcontentloaded'});
 await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 await page.locator('#orderFulfillmentRows a').getByText('Рейс №33571',{exact:false}).first().waitFor();
 await page.locator('#orderFulfillmentRows a[href="transport-loading.html?trip_id=33571"]').first().click();
 await page.waitForURL('**/transport-loading.html?trip_id=33571');
 await page.locator('#tripSummary').filter({hasText:'ожидают погрузки'}).waitFor();
 if(await page.locator('#tripId').inputValue()!=='33571')throw Error('Trip deep link lost');
 if(!await page.locator('#tripDepart').isDisabled())throw Error('Unloaded trip departure enabled');
 if(errors.length)throw Error(errors.join(';'));
 await page.screenshot({path:'reports/nicora/2026-10-13/screenshots/62-order-to-current-loading.png'});
 console.log('PASS1227 current order→actual assigned trip→loading; pending facts visible/departure disabled/no writes');
}finally{await browser.close();}
