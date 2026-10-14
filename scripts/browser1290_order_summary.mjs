import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const browser=await chromium.launch({headless:true});
try{const page=await browser.newPage({viewport:{width:1440,height:1080}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:8088/wms-admin/customer-orders.html?order_id=2135#orderExecution');
await page.locator('#adminLoginForm button[type=submit]').click();
await page.waitForFunction(()=>window.orderState?.selectedId===2135||typeof orderState!=='undefined'&&orderState.selectedId===2135);
await page.waitForFunction(()=>document.querySelector('#orderDeliveryRows').children.length===2);
await page.locator('#orderExecutionPanel').scrollIntoViewIfNeeded();
await page.screenshot({path:'reports/retailcase/2026-10-13/screenshots/80-b01-order-summary.png'});
console.log(JSON.stringify({execution:await page.locator('#orderExecutionStatus').innerText(),delivery:await page.locator('#orderDeliveryStatus').innerText(),errors}));
await page.locator('#plRead').click();
await page.waitForFunction(()=>document.querySelector('#plCurrentRows').children.length===2);
await page.locator('#preparedLayoutPanel').scrollIntoViewIfNeeded();await page.screenshot({path:'reports/retailcase/2026-10-13/screenshots/81-b01-prepared-layout-current.png'});
}finally{await browser.close();}
