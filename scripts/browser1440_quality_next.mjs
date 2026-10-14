import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const b=await chromium.launch({headless:true});
try {
 const p=await b.newPage({viewport:{width:1300,height:1000}}),errors=[],writes=[];
 p.on('pageerror',e=>errors.push(e.message));p.on('request',r=>{if(r.method()==='POST'&&r.url().includes('/api/'))writes.push(r.url());});
 const live=p.waitForResponse(r=>r.url().includes('/api/outgoing-quality/CASE%3A1131')&&!r.url().includes('final-captures'));
 await p.goto('http://127.0.0.1:8088/wms-admin/warehouse-tasks.html?qc_shipment=CASE%3A1131#outgoingQuality');
 await p.locator('#adminLoginForm button[type=submit]').click();const response=await live;const data=await response.json();
 if(response.status()!==200||!data.transport_assignment)throw Error(JSON.stringify({status:response.status(),data}));
 // Native QC source is retained. States below model navigation only; no goods commands.
 await p.evaluate(data=>window.wmsQualityNext.render(document.querySelector('#outgoingQuality'),{...data,ready:true,transport_assignment:{state:'ASSIGNED',transport_task_id:33571}},false),data);
 const link=p.getByRole('link',{name:'Открыть погрузку рейса 33571'});await link.waitFor();
 await p.locator('#outgoingQuality').screenshot({path:'reports/nicora/2026-10-13/screenshots/112-ni051-quality-next-synthetic.png'});
 const next=p.waitForResponse(r=>r.url().endsWith('/33571/status'));await link.click();if((await next).status()!==200)throw Error('Trip link failed');
 await p.goBack();
 await p.evaluate(data=>window.wmsQualityNext.render(document.querySelector('#outgoingQuality'),{...data,ready:false,required:true},false),data);
 if(await p.getByRole('link',{name:'Открыть погрузку рейса 33571'}).count())throw Error('Pending QC exposes approved link');
 await p.evaluate(data=>window.wmsQualityNext.render(document.querySelector('#outgoingQuality'),{...data,ready:true,transport_assignment:{state:'UNASSIGNED'}},false),data);
 await p.locator('#outgoingQuality .qc-actions span').filter({hasText:'ещё не назначен рейс'}).waitFor();
 if(errors.length||writes.length)throw Error(JSON.stringify({errors,writes}));
 const result={liveQc:200,assignment:data.transport_assignment,nativeTripRead:200,modeledNavigationStates:true,writes,errors};fs.writeFileSync('tmp/result1440.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));
}finally{await b.close();}
