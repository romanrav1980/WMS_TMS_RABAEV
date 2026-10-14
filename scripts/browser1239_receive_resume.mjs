import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const path='tmp/context1238.json',ctx=JSON.parse(fs.readFileSync(path,'utf8'));
if(ctx.stage!=='STORAGE_READY')throw Error('Resume retained context explicitly; no automatic new receipts');
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8088/wms-admin/receiving.html?supply_order_id='+ctx.supply.order_id+'&line_number=1',{waitUntil:'domcontentloaded'});
 await page.locator('#adminLoginForm button[type=submit]').click();
 await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 await page.waitForFunction(()=>!document.querySelector('#receiptConfirm').disabled);
 ctx.stage='RECEIVING';ctx.receipts=[];fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 for(let i=0;i<2;i++){
  if(i>0){await page.locator('#receiptLines tr[data-line-number="2"] button').click();await page.waitForFunction(()=>!document.querySelector('#receiptConfirm').disabled);}
  await page.locator('#receiptSscc').fill('B01.1238:'+ctx.tag+':'+(i+1));
  await page.locator('#receiptQuantity').fill('18');
  await page.locator('#receiptBarcode').fill(ctx.barcodes[i]);
  await page.locator('#receiptBatch').fill('B01.1238:'+ctx.tag);
  await page.locator('#receiptExpiry').fill('2030-01-01');
  await page.locator('#receiptWeight').fill('12');
  await page.locator('#receiptHeight').fill('1');
  await page.locator('#receiptHeightM').fill('1');
  await page.locator('#receiptVolume').fill('0.05');
  const responsePromise=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/pallets'));
  await page.locator('#receiptConfirm').click();
  const response=await responsePromise;const body=await response.json();
  ctx.receipts.push({line:i+1,status:response.status(),body});fs.writeFileSync(path,JSON.stringify(ctx,null,2));
  if(response.status()!==201)throw Error('Receipt not confirmed: '+JSON.stringify(body));
  await page.locator('#receiptMessage').filter({hasText:'принята'}).waitFor();
 }
 if(errors.length)throw Error(errors.join(';'));
 ctx.stage='RECEIVED';fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 await page.locator('#receiptMessage').scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/retailcase/2026-10-13/screenshots/65-b01-sap-received.png'});
 console.log(JSON.stringify({stage:ctx.stage,receipts:ctx.receipts}));
}finally{await browser.close();}
