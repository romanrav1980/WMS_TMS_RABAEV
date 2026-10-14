import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const path='tmp/context1238.json',ctx=JSON.parse(fs.readFileSync(path,'utf8'));
if(ctx.stage!=='STAGING_DONE')throw Error('Retained stage required');
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8088/wms-admin/customer-orders.html?order_id=2135#preparedLayoutPanel',{waitUntil:'domcontentloaded'});
 await page.locator('#adminLoginForm button[type=submit]').click();
 await page.waitForFunction(()=>orderState.selectedId===2135);
 await page.locator('#plRead').click();await page.locator('#plRow option').filter({hasText:'QAUTOc0c2a00c0bB · 6'}).waitFor({state:'attached'});
 await page.locator('#plRow').selectOption('16727991');await page.locator('#plTarget').selectOption('641508');
 await page.locator('#plReason').fill('Согласование подготовленной укладки с фактически отобранными целыми паллетами A18 и B18');
 await page.locator('#plPreview').click();await page.locator('#plComparison').waitFor({state:'visible'});
 await page.locator('#plComparison').scrollIntoViewIfNeeded();await page.screenshot({path:'reports/retailcase/2026-10-13/screenshots/74-b01-layout-preview.png'});
 ctx.stage='LAYOUT_MOVE_STARTED';fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 const expected=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/prepared-layout/move-row'));
 await page.locator('#plMove').click();const response=await expected;const body=await response.json();
 ctx.layout_move={status:response.status(),body,request:response.request().postDataJSON()};
 ctx.layout_pending=await page.evaluate(()=>Object.fromEntries(Object.keys(localStorage).filter(k=>k.startsWith('retailcase.preparedLayout:')).map(k=>[k,localStorage.getItem(k)])));
 fs.writeFileSync(path,JSON.stringify(ctx,null,2));if(!response.ok())throw Error(JSON.stringify(body));
 await page.locator('#plStatus').filter({hasText:'Укладка изменена'}).waitFor();
 ctx.layout_replay=await page.evaluate(body=>orderRequest('/api/customer-orders/2135/prepared-layout/move-row',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),ctx.layout_move.request);
 if(ctx.layout_replay.operation_id!==body.operation_id)throw Error('Wrong replay');
 ctx.stage='LAYOUT_RECONCILED';fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 await page.locator('#preparedLayoutPanel').scrollIntoViewIfNeeded();await page.screenshot({path:'reports/retailcase/2026-10-13/screenshots/75-b01-layout-confirmed.png'});
 console.log(JSON.stringify({stage:ctx.stage,result:body,replay_operation:ctx.layout_replay.operation_id,errors}));
 if(errors.length)throw Error(errors.join(';'));
}finally{await browser.close();}

