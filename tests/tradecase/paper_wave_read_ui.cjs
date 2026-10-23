// Actual read-only task navigation; the one pending-record recovery case is a browser fixture.
const fs=require('fs'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-23/T11/';
const state=JSON.parse(fs.readFileSync(out+'paper-wave-state.json','utf8'));
const pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const auth='Basic '+Buffer.from('admin:'+pass).toString('base64');
const result={checks:[],posts:0,queueReads:0,errors:[],fixtures:['pending full-pallet browser record; never sent']};
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  for(const width of [390,1440]){
   const ctx=await browser.newContext({viewport:{width,height:900}}),p=await ctx.newPage();
   await ctx.addInitScript(auth=>sessionStorage.setItem('wmsAdminAuth',JSON.stringify({apiBase:'http://127.0.0.1:8088',basic:auth})),auth);
   p.on('pageerror',e=>result.errors.push(String(e)));
   await ctx.route('**/api/**',r=>{if(r.request().method()==='POST'){result.posts++;return r.abort();}if(/\/api\/warehouse-tasks\?/.test(r.request().url()))result.queueReads++;return r.continue();});
   async function open(id){const response=await ctx.request.get('http://127.0.0.1:8088/api/warehouse-tasks/'+id+'/paper',{headers:{Authorization:auth}});if(response.status()!==200)throw Error(await response.text());const paper=await response.json();await p.goto('http://127.0.0.1:8088/wms-admin/warehouse-tasks.html?task_id='+id+'&paper_reference='+encodeURIComponent(paper.reference));await p.waitForFunction(id=>warehouseTaskState.selectedTask?.task_id===id,id);}
   await open(state.task);assert(await p.locator('#fullpalShipment').isHidden(),'Replenishment must not ask for shipment binding');
   assert(await p.locator('.warehouse-task-list-panel').isHidden());assert(await p.locator('#warehouseTaskComplete').isDisabled());
   await p.screenshot({path:out+'paper-wave-compact-'+width+'.png',fullPage:true});
   await open(1221);assert(await p.locator('#fullpalShipment').isVisible(),'Actual completed full-pallet picking move retains binding');
   await open(state.task);
   await p.evaluate(()=>{const key='wms-fullpal-binding:'+wmsAdminAuth.state.apiBase.replace(/\/$/,'')+':'+wmsAdminAuth.state.user.username;window.qaPendingKey=key;localStorage.setItem(key,JSON.stringify({task:1221,body:{operation_id:'FULLPAL.BIND:read-only-recovery-fixture',shipment_identifier:'QA_PENDING_NO_POST',scanned_pallet:'QA_PENDING_NO_POST',expected_stock_version:0}}));window.dispatchEvent(new StorageEvent('storage',{key}));});
   assert(await p.locator('#fullpalShipment').isVisible(),'Unknown saved binding must stay accessible on a different task');
   assert.equal(await p.locator('#fullpalShipment [data-bind]').innerText(),'Повторить сохранённую связь');
   await p.evaluate(()=>{localStorage.removeItem(window.qaPendingKey);window.dispatchEvent(new StorageEvent('storage',{key:window.qaPendingKey}));});
   assert(await p.locator('#fullpalShipment').isHidden());
   const overflow=await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);assert(overflow<=1);result.checks.push({width,replenishmentBindingHidden:true,realFullPickingShown:true,pendingFixtureRetained:true,overflow});await ctx.close();
  }
  assert.equal(result.posts,0);assert.equal(result.queueReads,0);assert.deepStrictEqual(result.errors,[]);result.status='PASS';console.log(JSON.stringify(result));
 }finally{await browser.close();fs.writeFileSync(out+'paper-wave-read-ui.json',JSON.stringify(result,null,2));}
})().catch(e=>{console.error(e);process.exitCode=1});
