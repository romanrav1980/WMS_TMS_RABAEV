import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const path='tmp/context1238.json',ctx=JSON.parse(fs.readFileSync(path,'utf8'));
if(ctx.stage!=='FULLPAL_BOUND')throw Error('Retained stage required');
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1080}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8088/wms-admin/transport-loading.html?trip_id=33571');
 await page.locator('#adminLoginForm button[type=submit]').click();
 await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 await page.locator('#tripSummary').getByText('QC241ede877f6d1',{exact:false}).waitFor();
 ctx.loading_ui??=[];
 async function clickCommand(id,url){
  const pending=page.waitForResponse(r=>r.url().endsWith(url)&&r.request().method()==='POST');
  await page.locator(id).click();const r=await pending;
  const result={url,status:r.status(),request:r.request().postDataJSON(),body:await r.json()};
  ctx.loading_ui.push(result);fs.writeFileSync(path,JSON.stringify(ctx,null,2));console.log(JSON.stringify(result));
  if(!r.ok())throw Error('Command rejected; saved request remains in context');
  await page.waitForFunction(()=>!window.wmsPhysicalLoadState.isBusy());
 }
 for(let i=1;i<=2;i++){
  const st='OP_SAP_2135_'+i,pal='B01.1238:c0c2a00c0b:'+i;
  if(ctx.loading_ui.some(x=>x.url.endsWith('confirm-single')&&x.request.identifier===st&&x.status<300))continue;
  await page.locator('#loadMode').selectOption('SINGLE');
  await page.locator('#loadShipment').fill(st);
  await page.locator('#loadComposition').click();
  await page.locator('#palletFloorPanel').waitFor({state:'visible'});
  await page.locator('#loadScan').fill(pal);await page.locator('#loadCell').fill('B38c0c2a00cE');
  if(!ctx.loading_ui.some(x=>x.url.endsWith('pallet-floor-types')&&x.request.identifier===pal&&x.status<300)){
   await page.locator('#palletFloorSelect').selectOption('1');
   await page.locator('#palletFloorReference').fill('OWN.DEV.B01.1283:'+i);
   await clickCommand('#palletFloorConfirm','/api/inventory/pallet-floor-types');
   await page.locator('#loadComposition').click();await page.locator('#palletFloorPanel').waitFor({state:'visible'});
  }
  await page.locator('#loadVehicle').fill('QC241ede877f6d1');await page.locator('#loadDock').fill(ctx.loading_dock);
  for(const [id,value]of Object.entries({loadGross:'12',loadWidth:'0.8',loadDepth:'1.2',loadHeight:'1'}))await page.locator('#'+id).fill(value);
  await clickCommand('#loadConfirm','/api/transport/loading/confirm-single');
 }
 ctx.stage='B01_LOADED';fs.writeFileSync(path,JSON.stringify(ctx,null,2));
 await page.locator('#tripSummary').scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/nicora/2026-10-13/screenshots/77-b01-loaded.png'});
 console.log(JSON.stringify({stage:ctx.stage,errors}));
}finally{await browser.close();}
