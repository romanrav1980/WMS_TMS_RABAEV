import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1080}});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('response',r=>{if(r.status()>=400)errors.push(r.status()+':'+r.url())});
 await page.goto('http://127.0.0.1:3000/?page=fleet',{waitUntil:'networkidle',timeout:30000});
 console.log(JSON.stringify({url:page.url(),errors,rows:await page.locator('tr').count(),body:(await page.locator('body').innerText()).slice(0,1300)}));
}finally{await browser.close();}
