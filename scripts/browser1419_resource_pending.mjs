import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const b=await chromium.launch({headless:true});
try{
 const p=await b.newPage({viewport:{width:1250,height:1000}}),errors=[],bodies=[];
 p.on('pageerror',e=>errors.push(e.message));
 await p.goto('http://127.0.0.1:8088/wms-admin/resource-workload.html');await p.locator('#adminLoginForm button[type=submit]').click();await p.waitForFunction(()=>window.wmsAdminAuth?.state.user);
 await p.locator('#rwWare').fill('6667491');await p.locator('#rwSite').fill('QA134');
 await p.locator('#rwViewStart').fill('2026-10-15T10:00');await p.locator('#rwViewFinish').fill('2026-10-15T12:00');
 await p.route('**/api/resources/workload/warehouses/6667491/preview',r=>r.fulfill({status:200,contentType:'application/json',body:JSON.stringify({current_presence_count:0,intervals:[],work_outside_view:[],unscheduled_work:[],work:[],recommendations:{status:'CAPACITY_ACTIONS',capacity_actions:[{from_utc:'2026-10-15T10:00:00Z',to_utc:'2026-10-15T12:00:00Z',additional_planned_person_hours:'2',additional_full_interval_people:1}],wave_duration_scenarios:[]}})}));
 await p.locator('#rwPreview').click();const apply=p.getByRole('button',{name:'Подставить интервал в план выхода',exact:true});await apply.waitFor();await apply.click();
 if(!(await p.locator('#rwStart').inputValue()).startsWith('2026-10-15T'))throw Error('Interval not filled');
 await p.locator('#rwResult').screenshot({path:'reports/retailcase/2026-10-13/screenshots/109-ni081-capacity-action.png'});
 const storeKey=await p.evaluate(()=>{const key='wmsWorkloadPending:'+window.wmsAdminAuth.state.apiBase.replace(/\/$/,'')+'|'+window.wmsAdminAuth.state.user.username;localStorage.setItem(key,JSON.stringify({path:'/api/resources/workload/norms',body:{operation_id:'WORKLOAD.UI:1419',warehouse_id:6667491}}));document.getElementById('rwWare').dispatchEvent(new Event('input'));return key;});
 let phase=0;
 await p.route('**/api/resources/workload/norms',r=>{bodies.push(r.request().postData());const request=JSON.parse(r.request().postData());phase++;return r.fulfill({status:phase===1?503:200,contentType:'application/json',body:JSON.stringify(phase===1?{detail:{code:'WORKLOAD_COMMAND_UNCONFIRMED',message:'TEST unknown response'}}:{operation_id:request.operation_id,warehouse_id:6667491,action:'NORM',stock_changed:false})});});
 await p.locator('#rwRetry').click();await p.locator('#rwMessage').filter({hasText:'Повторите исходное действие'}).waitFor();
 if(!await p.evaluate(k=>localStorage.getItem(k),storeKey))throw Error('Lost intent');
 await p.locator('#rwRetry').click();await p.locator('#rwMessage').filter({hasText:'Действие подтверждено'}).waitFor();
 if(bodies.length!==2||bodies[0]!==bodies[1]||await p.evaluate(k=>localStorage.getItem(k),storeKey))throw Error('Replay mismatch');
 const integrity=await p.evaluate(()=>{
  const key=()=> 'test.resource1419',s=window.wmsResourcePending.create(key,'wave','wtRetry',async()=>{});
  const body={operation_id:'WAVE.TIME.UI:1419',wave_id:395};
  s.save(body);const r=s.read();const rejected=s.confirms(body,{operation_id:'OTHER',wave_id:395,plan_status:'APPROVED',stock_changed:false});
  let conflict=false;localStorage.setItem(key(),'changed');try{s.settle(r);}catch{conflict=true;}
  const damaged=s.read().damaged;s.archiveDamaged(s.read());
  const old=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k===key())return;return old.call(this,k,v);};
  let blocked=false;try{s.save(body);}catch{blocked=true;}finally{Storage.prototype.setItem=old;}
  return {wrongIdentityRejected:!rejected,changedRecordPreserved:conflict,damaged,storageFailureBlocked:blocked};
 });
 if(Object.values(integrity).some(v=>v!==true)||errors.length)throw Error(JSON.stringify({integrity,errors}));
 fs.writeFileSync('tmp/result1419.json',JSON.stringify({recommendationSynthetic:true,sameBodyReplay:true,interceptedCommandPosts:bodies.length,oracleWrites:0,integrity,errors},null,2));console.log(JSON.stringify({sameBodyReplay:true,integrity,errors}));
}finally{await b.close();}
