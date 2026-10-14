import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const out='reports/nicora/2026-10-13/codex/NI011/';fs.mkdirSync(out,{recursive:true});const context=JSON.parse(fs.readFileSync('tmp/context1294.json','utf8'));
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),writes=[],errors=[],checks=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.method()!=='GET'&&r.url().includes('/api/'))writes.push(r.url());});
 await page.goto('http://127.0.0.1:8088/wms-admin/receiving.html?warehouse_id='+context.warehouse+'&supply_order_id='+context.supply.order_id);
 await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>document.querySelector('#receiptProfile').options.length===2);
 const quantity=await page.locator('#receiptQuantity').inputValue();
 async function scan(unit,profile,code,amount){await page.locator('#receiptUnit').fill(unit);await page.locator('#receiptUnitQuantity').fill(amount);await page.locator('#receiptProfile').selectOption(String(profile));await page.locator('#receiptMarkCode').fill(code);await page.locator('#receiptAddCode').click();}
 await scan('1',0,'WRONG:<img src=x onerror=alert(1)>','0.25');await scan('1',1,'EGAIS:KEEP','0.25');await scan('2',0,'CRPT:KEEP','0.75');await scan('2',1,'EGAIS:KEEP2','0.75');
 if(await page.locator('#receiptCodes img').count())throw Error('HTML interpreted');
 await page.locator('#receiptCodes li').first().locator('button').click();
 if(await page.locator('#receiptCodes li').count()!==3||await page.locator('#receiptUnit').inputValue()!=='1'||await page.locator('#receiptUnitQuantity').inputValue()!=='0.25'||await page.locator('#receiptProfile').inputValue()!=='0')throw Error('Per-profile correction failed');checks.push('one bad profile removed; other unit/profile codes and unit quantity retained');
 await page.locator('#receiptMarkCode').fill('CRPT:CORRECTED');await page.locator('#receiptAddCode').click();
 if(await page.locator('#receiptCodes li').count()!==4)throw Error('Correction lost scans');
 const unit2=page.locator('#receiptCodes li').filter({hasText:'Единица 2'});await unit2.first().locator('button').click();await unit2.first().locator('button').click();
 if(!(await page.locator('#receiptCodeCount').textContent()).includes('Единиц со сканированиями: 1'))throw Error('Empty unit not removed');checks.push('last profile removal removes only its physical unit');
 if(await page.locator('#receiptQuantity').inputValue()!==quantity)throw Error('Pallet quantity changed');checks.push('pallet quantity untouched; textContent protects raw QR');
 await page.evaluate(()=>{window.originalPending=window.wmsReceiptIntent.pending;window.wmsReceiptIntent.pending=()=>[{body:{operation_id:'fixture',sscc:'PENDING:TEST'}}];document.getElementById('receiptSscc').value='PENDING:TEST';});
 const before=await page.locator('#receiptCodes').textContent();await page.locator('#receiptCodes li button').first().click();await page.locator('#receiptClearCodes').click();await page.locator('#receiptMarkCode').fill('MUST:NOT:ADD');await page.locator('#receiptAddCode').click();
 if(await page.locator('#receiptCodes').textContent()!==before)throw Error('Pending modified');checks.push('pending immutable: remove/all-clear/add blocked');await page.evaluate(()=>{wmsReceiptIntent.pending=window.originalPending;});
 await page.locator('#receiptMarking').screenshot({path:out+'receipt-scan-correction.png'});
 if(writes.length||errors.length)throw Error(JSON.stringify({writes,errors}));fs.writeFileSync(out+'browser.json',JSON.stringify({real_get_source:context.supply.order_id,local_codes_synthetic:true,pending_check_simulated:true,checks,writes,errors},null,2));console.log(JSON.stringify({checks,writes,errors}));
}finally{await browser.close();}