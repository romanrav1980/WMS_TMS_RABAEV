import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const b=await chromium.launch({headless:true});try{
 const p=await b.newPage({viewport:{width:1250,height:950}}),writes=[],errors=[];p.on('pageerror',e=>errors.push(e.message));p.on('request',r=>{if(r.method()==='POST'&&r.url().includes('/api/'))writes.push(r.url());});
 const actual=p.waitForResponse(r=>r.url().includes('/stock-conflicts?'));
 await p.goto('http://127.0.0.1:8088/wms-admin/day-reconciliation.html?warehouse_id=9807&stock_metric=stock_quantity_invariants#stockConflicts');await p.locator('#adminLoginForm button[type=submit]').click();const response=await actual;if(response.status()!==200)throw Error('Live registry unavailable');
 await p.locator('#stockConflicts [role=status]').filter({hasText:'Конец текущей выборки'}).waitFor();
 await p.route('**/stock-conflicts?*',r=>{const second=new URL(r.request().url()).searchParams.has('after');const count=second?2:50;return r.fulfill({status:200,contentType:'application/json',body:JSON.stringify({warehouse_id:9807,metric:'stock_quantity_invariants',rows:Array.from({length:count},(_,i)=>({uid_pallet:'SYNTHETIC:'+String((second?50:0)+i),cell:'TEST',base_uom:'EA',physical_quantity:'.3',hard_quantity:'.4'})),has_more:!second,next_cursor:second?null:'synthetic-page-two'})});});
 await p.locator('#stockConflicts [data-first]').click();await p.waitForFunction(()=>document.querySelectorAll('#stockConflicts tbody tr').length===50);
 await p.locator('#stockConflicts [data-next]').click();await p.waitForFunction(()=>document.querySelectorAll('#stockConflicts tbody tr').length===2);
 if(!await p.locator('#stockConflicts [data-next]').isDisabled())throw Error('End page still enabled');
 await p.locator('#stockConflicts').screenshot({path:'reports/nicora/2026-10-13/screenshots/110-ni072-stock-conflict-pages-synthetic.png'});
 await p.locator('#drWare').fill('6667491');if(await p.locator('#stockConflicts tbody tr').count())throw Error('Old warehouse rows retained');
 if(writes.length||errors.length)throw Error(JSON.stringify({writes,errors}));fs.writeFileSync('tmp/result1430.json',JSON.stringify({realRead:200,syntheticUiPages:[50,2],filterReset:true,writes,errors},null,2));console.log(JSON.stringify({realRead:200,syntheticUiPages:[50,2],writes,errors}));
}finally{await b.close();}
