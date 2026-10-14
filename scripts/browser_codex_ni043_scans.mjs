import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const out='reports/nicora/2026-10-13/codex/NI043/';fs.mkdirSync(out,{recursive:true});
const source=fs.readFileSync('wiki-raw/wms_admin_ui_reference/warehouse-task-scans.js','utf8'),sig='A'.repeat(64),checks=[];
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1200,height:650}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/ni043-harness',r=>r.fulfill({contentType:'text/html',body:'<main></main><script>var warehouseTaskState={selectedTask:{task_id:1}};window.wmsAdminAuth={state:{apiBase:location.origin,user:{username:"actorA"}},headers:()=>({}),hasPermission:()=>true};</script>'}));
 let saved=null,delay=null,lose=false,mismatch=false,posts=[];
 await page.route('**/api/warehouse-tasks/*/scan-*',async route=>{
  const request=route.request(),id=Number(request.url().match(/tasks\/(\d+)/)[1]);
  if(delay&&request.url().endsWith(delay.suffix)){const wait=delay;delay=null;wait.started();await wait.promise;}
  if(request.method()==='POST'){
   const body=request.postDataJSON();posts.push(body);saved={draft_id:body.draft_id,task_id:id,actor:'actorA',request:body,profile_signature:sig,stock_version:1};
   if(lose){lose=false;await route.abort('failed');return;}
   await route.fulfill({json:{draft_id:mismatch?'WRONG':body.draft_id,idempotent:posts.length>1}});return;
  }
  await route.fulfill({json:request.url().endsWith('/scan-context')?{task_id:id,profiles:[{system_code:'CRPT',profile_code:'TOBACCO',profile_version:1,scan_mode:'UNIT'}],profile_signature:sig,stock_version:1,marking_required:1}:saved});
 });
 await page.goto('http://127.0.0.1:8088/ni043-harness');await page.addScriptTag({content:source});
 const click=async action=>{await page.locator('[data-action="'+action+'"]').click();};
 const idle=()=>page.waitForFunction(()=>!document.querySelector('[data-action="load"]').disabled);
 const switchTask=id=>page.evaluate(id=>{warehouseTaskState.selectedTask={task_id:id};window.dispatchEvent(new Event('warehouse-task-selected'));},id);
 const setDelay=suffix=>{let release,started;const promise=new Promise(r=>release=r),signal=new Promise(r=>started=r);delay={suffix,promise,started};return{release,signal};};
 const late=setDelay('/scan-context');await click('load');await late.signal;await switchTask(2);late.release();await page.waitForTimeout(100);
 if(await page.locator('select option').count())throw Error('Stale context visible');checks.push('late GET ignored after task change');
 await switchTask(1);await click('load');await idle();await page.locator('input').fill('UNIQUE:1');await click('add');await idle();lose=true;await click('save');await idle();
 const first=posts[0];if(!first||await page.evaluate(()=>warehouseTaskScans.draftId(1))!==null)throw Error('Lost response marked saved');
 await click('retry');await idle();if(posts[1].draft_id!==first.draft_id||await page.evaluate(()=>warehouseTaskScans.draftId(1))!==first.draft_id)throw Error('Retry identity');checks.push('lost POST response retained exact ID; retry reconciled current GET');
 await page.evaluate(()=>{wmsAdminAuth.state.user={username:'actorB'};window.dispatchEvent(new Event('wms-admin-auth-ready'));});
 if(await page.evaluate(()=>warehouseTaskScans.draftId(1))!==null)throw Error('Actor leaked');checks.push('same task different actor has no draft');
 await page.evaluate(()=>{wmsAdminAuth.state.user={username:'actorA'};window.dispatchEvent(new Event('wms-admin-auth-ready'));});await click('load');await idle();
 const postsBefore=posts.length;await click('retry');await idle();if(posts.length!==postsBefore)throw Error('Empty retry sent');checks.push('empty retry sends no request');
 await page.locator('input').fill('UNIQUE:2');await click('add');await idle();mismatch=true;await click('save');await idle();if(await page.evaluate(()=>warehouseTaskScans.draftId(1))!==null)throw Error('Wrong response ID saved');
 if(!await page.evaluate(()=>localStorage.getItem('wms.task.scans:'+location.origin+':actorA:1')))throw Error('Wrong response lost intent');checks.push('wrong response ID keeps pending and blocks confirmed draft');
 mismatch=false;await click('retry');await idle();
 await page.locator('input').fill('UNIQUE:3');await click('add');await idle();const lateSave=setDelay('/scan-draft');await click('save');await lateSave.signal;
 await page.evaluate(()=>{wmsAdminAuth.state.user={username:'actorB'};window.dispatchEvent(new Event('wms-admin-auth-ready'));});lateSave.release();await page.waitForTimeout(100);
 if(await page.evaluate(()=>warehouseTaskScans.draftId(1))!==null)throw Error('Stale save actor leak');checks.push('late save after actor change ignored; old pending retained');
 await page.evaluate(()=>{const title=document.createElement('h1');title.textContent='NI04.3: проверка смены пользователя — ответы API моделируются';document.body.prepend(title);});
 await page.screenshot({path:out+'scan-scope-synthetic.png'});if(errors.length)throw Error(JSON.stringify(errors));fs.writeFileSync(out+'browser.json',JSON.stringify({synthetic_api:true,checks,post_count:posts.length,errors},null,2));console.log(JSON.stringify({checks,errors}));
}finally{await browser.close();}