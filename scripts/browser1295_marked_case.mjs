import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const path='tmp/context1294.json',ctx=JSON.parse(fs.readFileSync(path));
if(ctx.stage!=='READY_FOR_UI')throw Error('Resume saved state, do not rerun');
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:430,height:932}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8088/wms-admin/case-pick-tsd.html?case_task_id='+ctx.case);
 await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 await page.waitForFunction(()=>document.querySelectorAll('#cpTsdMarking textarea').length===2);
 await page.locator('#cpTsdScanCell').fill(ctx.cell);await page.locator('#cpTsdScanContainer').fill(ctx.carrier);
 await page.locator('#cpTsdScanProduct').fill(ctx.gtin);await page.locator('#cpTsdFactQty').fill('5');
 const url='/api/case-pick/tasks/'+ctx.case+'/lines/'+ctx.line+'/confirm';let posts=0;
 page.on('request',r=>{if(r.url().endsWith(url)&&r.method()==='POST')posts++;});
 await page.locator('#cpTsdMarking textarea[data-system=CRPT]').fill(ctx.scans.filter(x=>x.system_code==='CRPT').map(x=>x.code).join('\n'));
 await page.locator('#cpTsdConfirm').click();await page.waitForFunction(()=>document.querySelector('#cpTsdState').textContent.includes('ALCOHOL'));
 if(posts!==0)throw Error('Missing profile submitted');
 await page.locator('#cpTsdMarking textarea[data-system=EGAIS]').fill(ctx.scans.filter(x=>x.system_code==='EGAIS').map(x=>x.code).join('\n'));
 await page.locator('#cpTsdMarking').screenshot({path:'reports/retailcase/2026-10-13/screenshots/82-b02-multiple-profiles.png'});
 let original;
 await page.route('**'+url,async route=>{
  original=route.request().postDataJSON();
  const r=await route.fetch();ctx.first_pick={status:r.status(),request:original,body:await r.json()};
  fs.writeFileSync(path,JSON.stringify(ctx,null,2));
  if(!r.ok()){await route.fulfill({response:r});return;}
  ctx.stage='PICK_COMMITTED_RESPONSE_LOST';fs.writeFileSync(path,JSON.stringify(ctx,null,2));
  await route.abort('failed');
 },{times:1});
 await page.locator('#cpTsdConfirm').click();
 await page.waitForFunction(()=>document.querySelector('#cpTsdState').textContent.includes('Исход не подтверждён'));
 await page.reload();await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 await page.locator('#cpTsdRetryPosting').waitFor({state:'visible'});
 const response=page.waitForResponse(r=>r.url().endsWith(url)&&r.request().method()==='POST');
 await page.locator('#cpTsdRetryPosting').click();const r=await response;const body=await r.json();
 ctx.replay={status:r.status(),body,same_request:JSON.stringify(r.request().postDataJSON())===JSON.stringify(original)};
 fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 if(!r.ok()||!ctx.replay.same_request||body.operation_id!==original.operation_id)throw Error('Replay did not match');
 await page.waitForFunction(()=>document.querySelector('#cpTsdState').textContent.includes('Отбор проведён'));
 ctx.stage='B02_MARKED_PICKED';ctx.ui_errors=errors;fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 await page.locator('.tsd-task-card').first().screenshot({path:'reports/retailcase/2026-10-13/screenshots/83-b02-picked.png'});
 console.log(JSON.stringify({stage:ctx.stage,case:ctx.case,operation:body.operation_id,profiles:2,codes:original.unit_scans.length,quantity:original.fact_qty,missing_profile_posted:false,replay_same:ctx.replay.same_request,errors}));
}finally{await browser.close();}
