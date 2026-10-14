import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const path='tmp/context1238.json',ctx=JSON.parse(fs.readFileSync(path,'utf8'));
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage();
 await page.goto('http://127.0.0.1:8088/wms-admin/transport-loading.html?trip_id=33571');
 await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 ctx.loading_read=await page.evaluate(async()=>{
 const results=[];for(const path of ['/api/transport/loading/33571/status','/api/transport/loading/single-preview?shipment_identifier=OP_SAP_2135_1']){
 const r=await fetch(window.wmsAdminAuth.state.apiBase+path,{headers:window.wmsAdminAuth.headers()});results.push({path,status:r.status,body:await r.json()});}return results;});
 fs.writeFileSync(path,JSON.stringify(ctx,null,2));console.log(JSON.stringify(ctx.loading_read));
}finally{await browser.close();}
