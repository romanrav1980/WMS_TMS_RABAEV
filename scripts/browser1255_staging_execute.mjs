import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const path='tmp/context1238.json',ctx=JSON.parse(fs.readFileSync(path,'utf8'));
if(ctx.stage!=='STAGING_RELEASED')throw Error('Resume explicitly');
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}});
 await page.goto('http://127.0.0.1:8088/wms-admin/wave-replenishment.html?wave_id='+ctx.wave_id,{waitUntil:'domcontentloaded'});
 await page.locator('#adminLoginForm button[type=submit]').click();
 await page.waitForFunction(id=>waveReplenishmentState.selectedWave?.pick_wave_id===id,ctx.wave_id);
 ctx.staging_checks=await page.evaluate(async({wave,cell,other})=>{
   const url='/api/picking/waves/'+wave+'/staging/release';
   const call=async target=>{try{return {ok:true,body:await waveRepFetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({to_cell:target})})};}catch(e){return {ok:false,error:e.message};}};
   return {replays:await Promise.all([call(cell),call(cell)]),conflict:await call(other)};
 },{wave:ctx.wave_id,cell:ctx.staging_cell,other:ctx.storage_cells[0]});
 fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 if(!ctx.staging_checks.replays.some(r=>r.ok&&r.body.released_count===0)||ctx.staging_checks.conflict.ok)throw Error('Repeat/target conflict failed');
 const panel=page.getByRole('heading',{name:'Допуск отбора',exact:true}).locator('../..');
 await panel.locator('[data-load]').click();
 await page.waitForFunction(()=>[...document.querySelectorAll('section')].find(p=>p.querySelector('h2')?.textContent==='Допуск отбора')?.querySelector('[data-release]')?.disabled===false);
 const expected=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/release-picking'));
 await panel.locator('[data-release]').click();const response=await expected;const body=await response.json();
 ctx.pick_release={status:response.status(),body};fs.writeFileSync(path,JSON.stringify(ctx,null,2));if(!response.ok())throw Error(JSON.stringify(body));
 ctx.stage='PICK_RELEASED';fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 console.log(JSON.stringify({stage:ctx.stage,checks:ctx.staging_checks,release:body}));
}finally{await browser.close();}

