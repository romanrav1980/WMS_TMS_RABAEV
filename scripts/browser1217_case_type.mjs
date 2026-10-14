import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const ctx=JSON.parse(fs.readFileSync('tmp/context1214.json','utf8'));
if(ctx.state!=='TYPED_EMPTY')throw Error('Retained case changed; do not repeat UI write');
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1000,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 let saved;
 page.on('request',r=>{if(r.method()==='POST'&&r.url().endsWith('/'+ctx.task+'/pallet-type'))saved=JSON.parse(r.postData());});
 await page.goto('http://127.0.0.1:8088/wms-admin/case-pick-tsd.html?case_task_id='+ctx.task,{waitUntil:'domcontentloaded'});
 await page.locator('#adminLoginForm button[type=submit]').click();
 await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 await page.locator('#cpTsdRefresh').click();
 await page.locator('#cpTypeActual').filter({hasText:'версия 1'}).waitFor();
 await page.locator('#cpTypeSelect').selectOption('1');
 await page.locator('#cpTypeReason').fill('DEV1217: actual empty assembly type confirmed in terminal UI');
 await page.locator('#cpTsdScanContainer').fill('CASE:'+ctx.task);
 await page.locator('#cpTypeSave').click();
 await page.locator('#cpTypeActual').filter({hasText:'версия 2'}).waitFor();
 if(!saved)throw Error('No real POST observed');
 const replay=await page.evaluate(async({task,body})=>{
  const r=await fetch(window.wmsAdminAuth.state.apiBase+'/api/case-pick/tasks/'+task+'/pallet-type',
   {method:'POST',headers:{...window.wmsAdminAuth.headers(),'Content-Type':'application/json'},body:JSON.stringify(body)});
  const data=await r.json();if(!r.ok)throw Error(JSON.stringify(data));return data;
 },{task:ctx.task,body:saved});
 if(replay.operation_id!==saved.operation_id||replay.version!==2||replay.pallet_type_id!==1)throw Error('Wrong replay');
 if(errors.length)throw Error(errors.join(';'));
 await page.locator('#cpTypePanel').scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/nicora/2026-10-13/screenshots/56-case-pallet-type-desktop.png'});
 await page.setViewportSize({width:390,height:844});
 await page.locator('#cpTypePanel').scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/nicora/2026-10-13/screenshots/57-case-pallet-type-mobile.png'});
 ctx.state='UI_TYPED_EMPTY';ctx.ui_request=saved;ctx.ui_receipt=replay;
 fs.writeFileSync('tmp/context1214.json',JSON.stringify(ctx,null,2));
 console.log('PASS1217 real terminal TYPE POST and exact replay/task'+ctx.task+'/version2/typeEU/no page errors/screens56-57');
}finally{await browser.close();}
