import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const path='tmp/context1238.json',ctx=JSON.parse(fs.readFileSync(path,'utf8'));
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}});
 await page.goto('http://127.0.0.1:8088/wms-admin/warehouse-tasks.html?qc_shipment=OP_SAP_2135_1#outgoingQuality');
 await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 ctx.quality_read=await page.evaluate(async()=>{const results=[];for(const id of ['OP_SAP_2135_1','OP_SAP_2135_2']){
 const r=await fetch(window.wmsAdminAuth.state.apiBase+'/api/outgoing-quality/'+id,{headers:window.wmsAdminAuth.headers()});results.push({id,status:r.status,body:await r.json()});}return results;});
 fs.writeFileSync(path,JSON.stringify(ctx,null,2));console.log(JSON.stringify(ctx.quality_read));
}finally{await browser.close();}

