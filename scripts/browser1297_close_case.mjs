import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const path='tmp/context1294.json',ctx=JSON.parse(fs.readFileSync(path));if(ctx.stage!=='B02_MARKED_PICKED')throw Error('Retained picked state required');
const browser=await chromium.launch({headless:true});try{
 const page=await browser.newPage({viewport:{width:430,height:932}});
 await page.goto('http://127.0.0.1:8088/wms-admin/case-pick-tsd.html?case_task_id='+ctx.case);await page.locator('#adminLoginForm button[type=submit]').click();
 await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user)&&!document.querySelector('#cpTsdClose').disabled);
 const pending=page.waitForResponse(r=>r.url().endsWith('/'+ctx.case+'/close-pallet')&&r.request().method()==='POST');
 await page.locator('#cpTsdClose').click();const r=await pending;ctx.close={status:r.status(),request:r.request().postDataJSON(),body:await r.json()};fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 if(!r.ok())throw Error('Close rejected');await page.waitForFunction(()=>document.querySelector('#cpTsdState').textContent.includes('Сборка закрыта'));
 ctx.stage='B02_WAIT_CONTROL';fs.writeFileSync(path,JSON.stringify(ctx,null,2));console.log(JSON.stringify(ctx.close));
 await page.locator('.tsd-task-card').first().screenshot({path:'reports/nicora/2026-10-13/screenshots/84-b02-case-closed.png'});
 await page.goto('http://127.0.0.1:8088/wms-admin/case-pick-tsd.html?case_task_id=1064');
 await page.waitForFunction(()=>document.querySelector('#cpTsdMethod').textContent.includes('Товар на развес'));
 if(!await page.locator('#cpTsdFactQty').isDisabled())throw Error('Loose weight manual quantity enabled');
 console.log('PASS real retained loose-weight policy: manual quantity disabled; no mutation on CASE1064');
}finally{await browser.close();}
