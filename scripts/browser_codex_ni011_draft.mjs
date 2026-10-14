import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const out='reports/retailcase/2026-10-13/codex/NI011-draft/';fs.mkdirSync(out,{recursive:true});const source=JSON.parse(fs.readFileSync('tmp/context1294.json','utf8'));
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],posts=[],checks=[];page.on('pageerror',e=>errors.push(e.message));
 let changedPolicy=false,openFixture=false;
 await page.route('**/api/finished-goods/skus/*/receiving-policy',async route=>{const response=await route.fetch(),data=await response.json();if(changedPolicy)data.profiles[0].profile_version='TEST_CHANGED_VERSION';await route.fulfill({response,json:data});});
 await page.route('**/api/integrations/sap/supply-orders/'+source.supply.order_id,async route=>{const response=await route.fetch(),data=await response.json();if(openFixture){data.receipt_allowed=true;data.lines[0].remaining_qty='20';}await route.fulfill({response,json:data});});
 await page.route('**/api/receiving/supply-orders/*/pallets',async route=>{if(route.request().method()!=='POST')throw Error('Unexpected receipt request');posts.push(route.request().postDataJSON());await route.abort('failed');});
 const url='http://127.0.0.1:8088/wms-admin/receiving.html?warehouse_id='+source.warehouse+'&supply_order_id='+source.supply.order_id;
 await page.goto(url);await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>document.querySelector('#receiptProfile').options.length===2&&document.querySelector('#receiptFormDraft').hidden===false);
 const formKey=await page.evaluate(()=>Object.keys(localStorage).find(k=>k.startsWith('["retailcase.receipt.form"'))||null);if(formKey)throw Error('Unexpected prior draft');
 await page.locator('#receiptSscc').fill('LOCAL.DRAFT.PALLET');await page.locator('#receiptQuantity').fill('2.125');await page.locator('#receiptBatch').fill('LOCAL.BATCH');await page.locator('#receiptExpiry').fill('2027-01-01');await page.locator('#receiptWeight').fill('1.234');
 for(const profile of ['0','1']){await page.locator('#receiptUnit').fill('1');await page.locator('#receiptUnitQuantity').fill('0.25');await page.locator('#receiptProfile').selectOption(profile);await page.locator('#receiptMarkCode').fill('LOCAL:'+profile+'\u001dSCAN');await page.locator('#receiptAddCode').click();}
 const key=await page.evaluate(()=>Object.keys(localStorage).find(k=>k.startsWith('["retailcase.receipt.form"')));
 await page.reload();await page.locator('#receiptFormDraft button').first().waitFor({state:'visible'});await page.waitForFunction(()=>!document.querySelector('#receiptFormDraft button').disabled);
 if(await page.locator('#receiptCodes li').count())throw Error('Auto-restored scans');await page.locator('#receiptFormDraft button').first().click();
 if(await page.locator('#receiptQuantity').inputValue()!=='2.125'||await page.locator('#receiptSscc').inputValue()!=='LOCAL.DRAFT.PALLET'||await page.locator('#receiptCodes li').count()!==2||!(await page.locator('#receiptCodes').textContent()).includes('\u001d'))throw Error('Restore lost exact data');
 if(!await page.locator('#receiptConfirmLabel').isDisabled()||await page.locator('#receiptPrintedScan').inputValue())throw Error('Printer fact restored');checks.push('real source/profile GET; explicit restore preserves pallet/decimal quantity/batch/unit QR and GS; no printer confirmation');
 changedPolicy=true;await page.reload();await page.waitForFunction(()=>document.querySelector('#receiptFormDraft p').textContent.includes('изменились'));
 if(!await page.locator('#receiptFormDraft button').first().isDisabled())throw Error('Changed policy restored');checks.push('changed profile version blocks old form');
 await page.locator('#receiptFormDraft button').nth(1).click();changedPolicy=false;openFixture=true;await page.reload();await page.waitForFunction(()=>document.querySelector('#receiptProfile').options.length===2&&!document.querySelector('#receiptConfirm').disabled);
 await page.locator('#receiptSscc').fill('LOCAL.PENDING.PALLET');await page.locator('#receiptQuantity').fill('1');await page.locator('#receiptBatch').fill('LOCAL.BATCH');await page.locator('#receiptExpiry').fill('2027-01-01');
 await page.locator('#receiptConfirm').click();await page.waitForFunction(()=>document.querySelector('#receiptPendingSelect').options.length===1);
 const storage=await page.evaluate(()=>({forms:Object.keys(localStorage).filter(k=>k.startsWith('["retailcase.receipt.form"')&&!k.includes(':archived:')),pending:Object.keys(localStorage).filter(k=>k.startsWith('retailcase.receipt.pending:'))}));
 if(storage.forms.length||storage.pending.length!==1||posts.length!==1)throw Error('Draft duplicated command');checks.push('modeled unknown POST: form retired only after existing durable intent; pending remains sole journal');
 await page.reload();await page.waitForFunction(()=>document.querySelector('#receiptFormDraft p').textContent.includes('Приоритет'));
 if(!await page.locator('#receiptFormDraft button').first().isDisabled())throw Error('Pending restored');checks.push('unknown outcome blocks restoring form after reload');
 await page.locator('#receiptFormDraft').screenshot({path:out+'pending-priority.png'});
 await page.evaluate(keys=>keys.forEach(k=>localStorage.removeItem(k)),storage.pending);await page.evaluate(key=>localStorage.setItem(key,'{broken'),key);await page.reload();await page.waitForFunction(()=>document.querySelector('#receiptFormDraft p').textContent.includes('повреждён'));
 if(!await page.locator('#receiptFormDraft button').first().isDisabled())throw Error('Damaged restored');checks.push('damaged form visible and retained');
 if(errors.length)throw Error(JSON.stringify(errors));fs.writeFileSync(out+'browser.json',JSON.stringify({checks,errors,modeled_receipt_posts:posts.length,real_receipt_posts:0,synthetic_open_source_and_policy_change:true},null,2));console.log(JSON.stringify({checks,errors}));
}finally{await browser.close();}