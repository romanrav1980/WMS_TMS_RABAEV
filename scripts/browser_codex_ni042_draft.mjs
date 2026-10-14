import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const out='reports/nicora/2026-10-13/codex/NI042/';fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1100}}),writes=[],errors=[],checks=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.method()!=='GET'&&r.url().includes('/api/'))writes.push(r.url());});
 await page.goto('http://127.0.0.1:8088/wms-admin/case-pick-tsd.html?case_task_id=1134');await page.locator('#adminLoginForm button[type=submit]').click();
 await page.locator('#cpTsdMarking textarea').first().waitFor();await page.locator('#cpTsdInputDraft').waitFor({state:'visible'});
 const draftKey=await page.evaluate(()=>JSON.stringify(['nicora.caseInputDraft',cpTsdApiBase(),cpTsdUser(),cpTsd.task.case_pick_task_id,cpTsdCurrentLine().case_pick_line_id]));
 await page.locator('#cpTsdScanCell').fill('LOCAL:SCANNED');await page.locator('#cpTsdFactQty').fill('5.000000001');await page.locator('#cpTsdMarking textarea').first().fill('LOCAL:QR\u001d123');
 await page.reload();await page.locator('#cpTsdMarking textarea').first().waitFor();await page.locator('#cpTsdInputDraft button').first().waitFor();
 if(await page.locator('#cpTsdScanCell').inputValue())throw Error('Auto-restored physical scan');await page.locator('#cpTsdInputDraft button').first().click();
 if(await page.locator('#cpTsdScanCell').inputValue()!=='LOCAL:SCANNED'||await page.locator('#cpTsdFactQty').inputValue()!=='5.000000001'||await page.locator('#cpTsdMarking textarea').first().inputValue()!=='LOCAL:QR\u001d123')throw Error('Input not preserved exactly');checks.push('real CASE1134 GET; explicit reload restoration preserves exact quantity and GS separator');
 await page.evaluate(key=>{const record=JSON.parse(localStorage.getItem(key));record.signature+='changed';localStorage.setItem(key,JSON.stringify(record));cpTsdRender();},draftKey);await page.waitForFunction(()=>document.querySelector('#cpTsdInputDraft p').textContent.includes('изменились'));
 if(!await page.locator('#cpTsdInputDraft button').first().isDisabled())throw Error('Changed context restored');checks.push('changed snapshot blocks restoration');
 await page.locator('#cpTsdInputDraft button').nth(1).click();await page.locator('#cpTsdScanCell').fill('NEW:LOCAL');
 const before=await page.evaluate(key=>localStorage.getItem(key),draftKey);
 await page.evaluate(()=>{const key=JSON.stringify(['nicora.casePickIntent',cpTsdApiBase(),cpTsdUser()]);localStorage.setItem(key,'{"fixture":true}');});
 await page.locator('#cpTsdScanCell').fill('PENDING:BLOCKED');if(await page.evaluate(key=>localStorage.getItem(key),draftKey)!==before)throw Error('Pending overwritten');
 await page.evaluate(()=>localStorage.removeItem(JSON.stringify(['nicora.casePickIntent',cpTsdApiBase(),cpTsdUser()])));checks.push('pending command blocks draft writes');
 await page.evaluate(key=>{const record=JSON.parse(localStorage.getItem(key));window.oldTicket={key,revision:record.revision};record.revision='another-tab';localStorage.setItem(key,JSON.stringify(record));cpCaseDraft.settle(window.oldTicket);},draftKey);
 if(!await page.evaluate(key=>localStorage.getItem(key),draftKey))throw Error('New revision removed');checks.push('successful old receipt cannot delete newer tab draft');
 await page.evaluate(key=>{localStorage.setItem(key,'{broken');cpTsdRender();},draftKey);await page.waitForFunction(()=>document.querySelector('#cpTsdInputDraft p').textContent.includes('повреждён'));
 if(!await page.locator('#cpTsdInputDraft button').first().isDisabled())throw Error('Corrupt restored');checks.push('damaged record visible and retained');
 await page.locator('#cpTsdInputDraft button').nth(1).click();await page.locator('#cpTsdScanCell').fill('RESTORED:DEMO');
 await page.locator('#cpTsdInputDraft').screenshot({path:out+'case-input-draft.png'});
 if(writes.length||errors.length)throw Error(JSON.stringify({writes,errors}));fs.writeFileSync(out+'browser.json',JSON.stringify({checks,writes,errors,local_form_only:true},null,2));console.log(JSON.stringify({checks,writes,errors}));
}finally{await browser.close();}