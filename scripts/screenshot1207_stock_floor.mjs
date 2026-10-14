import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const d=JSON.parse(fs.readFileSync('tmp/context1206.json','utf8'));
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1080}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8088/wms-admin/transport-loading.html',{waitUntil:'domcontentloaded'});
 await page.locator('#adminLoginForm button[type=submit]').click();
 await page.waitForFunction(()=>Boolean(window.wmsAdminAuth?.state.user));
 await page.locator('#tripId').fill(String(d.trip_id));await page.locator('#tripLoad').click();
 await page.locator('#tripRows').getByText('Европоддон',{exact:true}).waitFor();
 const saved=await page.evaluate(async uid=>{
  const r=await fetch(window.wmsAdminAuth.state.apiBase.replace(/\/$/,'')+'/api/inventory/pallet-floor-types?identifier='+encodeURIComponent(uid),{headers:window.wmsAdminAuth.headers()});
  if(!r.ok)throw Error('Type read HTTP '+r.status);return r.json();
 },d.lot);
 if(saved.version!==1||saved.pallet_type_id!==1)throw Error('Wrong retained type');
 if(errors.length)throw Error(errors.join(';'));
 await page.locator('#tripSummary').scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/retailcase/2026-10-13/screenshots/55-stock-pallet-loading.png'});
 console.log('PASS1207 live API read/current trip/type proof/UI no page errors; no writes');
}finally{await browser.close();}
