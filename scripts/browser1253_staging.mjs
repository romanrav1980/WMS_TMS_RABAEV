import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const path='tmp/context1238.json',ctx=JSON.parse(fs.readFileSync(path,'utf8'));
if(!['WAVE_LAUNCHED','STAGING_RELEASE_STARTED'].includes(ctx.stage))throw Error('Retained flow required');
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}});
 await page.goto('http://127.0.0.1:8088/wms-admin/wave-replenishment.html?wave_id='+ctx.wave_id,{waitUntil:'domcontentloaded'});
 await page.locator('#adminLoginForm button[type=submit]').click();
 await page.waitForFunction(id=>waveReplenishmentState.selectedWave?.pick_wave_id===id,ctx.wave_id);
 await page.locator('#waveStagingToCell').fill(ctx.staging_cell);
 ctx.stage='STAGING_RELEASE_STARTED';fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 const expected=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/staging/release'));
 await page.locator('#waveStagingRelease').click();const response=await expected;const body=await response.json();
 ctx.staging_release={status:response.status(),body};fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 if(!response.ok())throw Error(JSON.stringify(body));
 await page.locator('#waveReplenishmentDetailStatus').filter({hasText:'В грузовую зону выпущено'}).waitFor();
 ctx.staging_tasks=await page.evaluate(id=>waveRepFetch('/api/picking/waves/'+id+'/tasks?limit=500'),ctx.wave_id);
 ctx.stage='STAGING_RELEASED';fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 await page.locator('#waveStagingTaskRows').scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/nicora/2026-10-13/screenshots/72-b01-staging-issued.png'});
 console.log(JSON.stringify({stage:ctx.stage,tasks:ctx.staging_tasks}));
}finally{await browser.close();}
