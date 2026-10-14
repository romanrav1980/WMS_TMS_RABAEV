import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
const b=await chromium.launch({headless:true});
try{
 const page=await b.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)errors.push(r.status()+' '+r.url());});
 await page.goto('http://127.0.0.1:8088/wms-admin/customer-orders.html?order_id=2135#preparedLayoutPanel');
 await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 await page.waitForFunction(()=>orderState.selectedId===2135);
 await page.locator('#plRead').click();await page.waitForFunction(()=>document.querySelector('#plCurrentRows').children.length||document.querySelector('#plStatus').textContent.includes('Error'));
 console.log(JSON.stringify({errors,state:await page.evaluate(()=>({selected:orderState.selectedId,status:document.querySelector('#plStatus').textContent,sap:document.querySelector('#sapPreparationStatus').textContent,rows:document.querySelector('#plCurrentRows').textContent,options:document.querySelector('#plRow').textContent}))}));
}finally{await b.close();}
