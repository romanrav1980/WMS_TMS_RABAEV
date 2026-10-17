// Production-bundle rendered recovery checks. EVERY request is fulfilled locally.
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{createHash}=require('node:crypto');
const root=path.resolve(__dirname,'../..'),dist=path.join(root,'terminal/wms_terminal_web/dist');
const out=path.join(root,'reports/retailcase/2026-10-15/resource-intent-ui');
const origin='http://127.0.0.1:8088',KEY='wms.case-work.journal.v1';
const digest=s=>createHash('sha256').update(s).digest('hex').toUpperCase();
const canonical=x=>JSON.stringify(Object.fromEntries(Object.keys(x).sort().map(k=>[k,x[k]])));
const body={operation_id:'UI.ORIGINAL:1',action:'START',expected_assignment_version:2,resource_session_id:3,resource_id:4,equipment_id:null,reason:'explicit original start reason'};
const wire=canonical(body),intent={server:origin,actor:'worker',task_id:7,url:'/api/case-pick/tasks/7/resource-commands',wire,request_sha256:digest(wire),body,created_at:'2026-10-15T18:00:00Z'};
function abandoned(control){return{operation_id:control.operation_id,status:'ABANDONED',domain:'CASE',task_id:7,actor:'worker',action:'START',target:'worker',original_operation_id:body.operation_id,original_wire:wire,original_request_sha256:digest(wire),control_request_sha256:digest(canonical(control)),original_expected_assignment_version:2,assignment_version_at_abandon:2,outcome_confirmed:true,stock_posted:false};}
function context(started=false){return{task_id:7,warehouse_id:1,status:started?'IN_PROGRESS':'ASSIGNED',assignment_version:started?3:2,content_version:1,assigned_to:'worker',resource_id:4,resource_session_id:3,equipment_id:null,started_at_instant:started?'2026-10-15T18:00:00Z':null,started_shift_time_zone:null,current_actor:'worker'};}
function originalAck(){const {current_actor,...state}=context(true);return{...state,operation_id:body.operation_id,action:'START',actor:'worker',outcome:'APPLIED',request_sha256:digest(wire),outcome_confirmed:true,may_create_corrected_operation:false,error_code:null,changed:true,stock_posted:false};}
function rejectedAck(){const {current_actor,...state}=context(false);return{...originalAck(),...state,outcome:'REJECTED',may_create_corrected_operation:true,error_code:'CASE_SESSION_UNAVAILABLE',changed:false};}
async function setup(browser,mode='lost',width=390){
 const ctx=await browser.newContext({viewport:{width,height:844},serviceWorkers:'block'}),page=await ctx.newPage();
 const state={mode,posts:[],originalPosts:0,ack:null,started:false,revoked:false,errors:[],unexpected:[]};
 await ctx.addInitScript(({key,intent,quota})=>{
  if(!localStorage.getItem('TEST.seeded')){localStorage.setItem(key,JSON.stringify({schema:1,pending:intent,last:null}));localStorage.setItem('TEST.seeded','1');}
  if(quota){const original=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k.startsWith('wms.metadata-intent-control.v1:'))throw new DOMException('quota','QuotaExceededError');return original.call(this,k,v);};}
 },{key:KEY,intent,quota:mode==='quota'});
 await ctx.route('**/*',async route=>{
  const req=route.request(),url=new URL(req.url()),p=url.pathname;
  if(!p.startsWith('/api/')){
   let file=path.join(dist,p.endsWith('/')?p+'index.html':p);if(!file.startsWith(dist)||!fs.existsSync(file)){state.unexpected.push(p);return route.fulfill({status:404,body:'missing'});}
   return route.fulfill({status:200,body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml'})[path.extname(file)]||'application/octet-stream'});
  }
  if(state.revoked && p.startsWith('/api/resources/metadata-intents')) return route.fulfill({status:403,json:{detail:"current access revoked"}});
  let data,status=200;
  if(p==='/api/terminal/auth/me'){const actor=Buffer.from(req.headers().authorization.slice(6),'base64').toString().split(':')[0];data={username:actor,display_name:actor,user_group:'TEST',permissions:['case_pick_execute']};}
  else if(p==='/api/resources/picker-time/me/current')data={operator_id:'worker',stream_version:0,shift_state:'OFF',work_state:'IDLE',warehouse_id:null,resource_session_id:null,resource_id:null,source_kind:null,source_id:null,shift_started_at:null,work_started_at:null,pause_started_at:null,last_event_at:null,work_coverage_certified:false,source_mode:'MANUAL_CONFIRMED'};
  else if(p.endsWith('/resource-context'))data=context(state.started);
  else if(p.endsWith('/resource-sessions'))data={task_id:7,warehouse_id:1,current_actor:'worker',action:'START',items:[{resource_session_id:3,resource_id:4,equipment_id:null,resource_code:'RESOURCE-4',ready:true,reason:null}],command_revalidates:true};
  else if(p==='/api/resources/metadata-intents/abandonments'&&req.method()==='POST'){
   state.posts.push(req.postData());const control=JSON.parse(req.postData());state.ack=abandoned(control);
   if(mode==='lost'&&state.posts.length===1)return route.abort('failed');
   if(mode.startsWith('recorded')){state.started=mode==='recorded';status=409;data={detail:{code:'RESOURCE_INTENT_RECORDED_READ_REQUIRED'}};}
   else if(mode==='mismatch')data={...state.ack,actor:'another'};
   else data=state.ack;
  }
  else if(p.startsWith('/api/resources/metadata-intents/abandonments/')){if(state.ack&&!mode.startsWith('recorded')){data=state.ack;}else{status=404;data={detail:'not found'};}}
  else if(p==='/api/resources/metadata-intents/resolution'){
   if(mode.startsWith('recorded')&&state.posts.length)data={status:'RECORDED',domain:'CASE',task_id:7,actor:'worker',original_operation_id:body.operation_id,original_request_sha256:digest(wire),original_receipt:mode==='recorded-rejected'?rejectedAck():originalAck(),abandonment:null};
   else if(mode==='remote')data={status:'ABANDONED',domain:'CASE',task_id:7,actor:'worker',original_operation_id:body.operation_id,original_request_sha256:digest(wire),original_receipt:null,abandonment:abandoned({operation_id:'REMOTE.CONTROL:1',domain:'CASE',task_id:7,reason:'other device same operator',original_wire:wire})};
   else{status=404;data={detail:'unknown'};}
  }
  else if(p.startsWith('/api/case-pick/resource-commands/')){status=404;data={detail:'not found'};}
  else if(p.endsWith('/resource-commands')&&req.method()==='POST'){state.originalPosts++;status=500;data={detail:'ORIGINAL MUST NOT BE SENT'};}
  else if(p.startsWith('/api/help/articles/'))data={article_id:p.split('/').pop(),title:'Восстановление запроса',body:'ABANDONED прекращает запрос, не задание.',related:[],revision:1};
  else{state.unexpected.push(p);status=404;data={detail:'unexpected mocked API'};}
  return route.fulfill({status,json:data});
 });
 page.on('pageerror',e=>state.errors.push(String(e)));
 async function login(target=page,actor='worker'){
  await target.locator('[data-help-id="assembly.login.username"]').fill(actor);await target.locator('[data-help-id="assembly.login.password"]').fill('TEST');await target.locator('[data-help-id="assembly.login.submit"]').click();
  await target.getByRole('heading',{name:'\u0417\u0430\u043f\u0440\u043e\u0441 \u0441\u043e\u0445\u0440\u0430\u043d\u0451\u043d',exact:true}).waitFor();await target.waitForFunction(()=>!document.querySelector('[data-help-id="case-work.refresh"]')?.disabled);
 }
 await page.goto(origin+'/case-work/?task_id=7');await login(page,mode==='foreign'?'other':'worker');
 return{ctx,page,state,login};
}
async function openRecovery(page){await page.locator('[data-help-id="metadata-intent.recovery.open"]').click();}
async function sendAbandon(page){await openRecovery(page);await page.locator('[data-help-id="metadata-intent.reason"]').fill('explicit reason to stop pending start');await page.locator('[data-help-id="metadata-intent.confirm"]').check();await page.locator('[data-help-id="metadata-intent.abandon.submit"]').click();}
async function stored(page){return page.evaluate(key=>JSON.parse(localStorage.getItem(key)),KEY);}
async function idle(page){await page.waitForFunction(()=>!document.querySelector('[data-help-id="case-work.refresh"]')?.disabled);}
async function lostRecovery(browser,checks){
 const {ctx,page,state,login}=await setup(browser,'lost',360);await sendAbandon(page);await idle(page);
 assert.equal(state.posts.length,1);assert.equal((await stored(page)).pending.wire,wire);assert.equal(await page.locator('[data-help-id="case-work.receipt.retry"]').isDisabled(),true);
 await page.screenshot({path:path.join(out,'control-pending-360.png'),fullPage:true});
 await page.reload();await login();await openRecovery(page);assert.equal(await page.locator('[data-help-id="case-work.receipt.retry"]').isDisabled(),true);
 await page.locator('[data-help-id="metadata-intent.abandon.submit"]').click();await page.getByRole('heading',{name:'Исходный запрос прекращён',exact:true}).waitFor();
 assert.equal(state.posts.length,2);assert.equal(state.posts[0],state.posts[1]);assert.equal((await stored(page)).pending,null);assert.equal((await stored(page)).abandoned.proof.original_wire,wire);assert.equal(state.originalPosts,0);
 assert.equal(await page.getByText('Само задание не отменено',{exact:false}).count(),1);assert.deepEqual(state.errors,[]);assert.deepEqual(state.unexpected,[]);
 checks.push('lost_response_reload_exact_control_retry_original_blocked_ABANDONED_not_task_cancelled');await ctx.close();
}
async function lostReadAndTabs(browser,checks){
 const {ctx,page,state,login}=await setup(browser,'lost',390);
 const second=await ctx.newPage();await second.goto(origin+'/case-work/?task_id=7');await login(second);
 await sendAbandon(page);await idle(page);await idle(second);
 assert.equal(await second.locator('[data-help-id="case-work.receipt.retry"]').isDisabled(),true);
 assert.equal(state.originalPosts,0);checks.push('shared_browser_journal_control_blocks_second_tab_original_retry');
 state.revoked=true;await page.locator('[data-help-id="metadata-intent.resolution.read"]').click();await idle(page);
 assert.ok((await stored(page)).pending);assert.equal(state.posts.length,1);checks.push('revoked_read_does_not_clear_unknown_control_or_original');
 state.revoked=false;await page.reload();await login();await page.locator('[data-help-id="case-work.receipt.read"]').click();
 await page.getByRole('heading',{name:'Исходный запрос прекращён',exact:true}).waitFor();assert.equal(state.posts.length,1);assert.equal((await stored(page)).pending,null);
 await page.screenshot({path:path.join(out,'abandoned-390.png'),fullPage:true});
 assert.deepEqual(state.errors,[]);checks.push('lost_response_reload_read_native_control_receipt_without_resend');await ctx.close();
}
async function simpleCases(browser,checks){
 for(const mode of ['unknown','mismatch','quota']){
  const {ctx,page,state}=await setup(browser,mode,390);
  if(mode==='unknown'){await page.locator('[data-help-id="case-work.receipt.read"]').click();await idle(page);assert.equal(state.posts.length,0);}
  else{await sendAbandon(page);await idle(page);assert.equal(state.posts.length,mode==='quota'?0:1);}
  assert.equal((await stored(page)).pending.wire,wire);assert.equal(state.originalPosts,0);assert.equal(await page.getByRole('heading',{name:'Исходный запрос прекращён',exact:true}).count(),0);
  assert.deepEqual(state.errors,[]);checks.push(mode+'_preserves_pending_no_original_or_fake_confirmation');await ctx.close();
 }
}
async function recordedRecovery(browser,checks){
 const {ctx,page,state}=await setup(browser,'recorded',1440);await sendAbandon(page);await idle(page);assert.ok((await stored(page)).pending);
 await page.locator('[data-help-id="metadata-intent.resolution.read"]').click();await page.getByRole('heading',{name:'Действие подтверждено',exact:true}).waitFor();
 assert.equal((await stored(page)).pending,null);assert.equal((await stored(page)).last.ack.operation_id,body.operation_id);assert.equal((await stored(page)).abandoned,undefined);assert.equal(state.originalPosts,0);
 await page.screenshot({path:path.join(out,'recorded-1440.png'),fullPage:true});assert.deepEqual(state.errors,[]);checks.push('RECORDED_winner_original_ack_not_ABANDONED');await ctx.close();
}
async function otherTerminalProofs(browser,checks){
 const rejected=await setup(browser,'recorded-rejected',390);await sendAbandon(rejected.page);await idle(rejected.page);await rejected.page.locator('[data-help-id="metadata-intent.resolution.read"]').click();
 await rejected.page.getByRole('heading',{name:'Сервер сохранил отказ',exact:true}).waitFor();assert.equal((await stored(rejected.page)).pending,null);assert.equal((await stored(rejected.page)).last.ack.outcome,'REJECTED');assert.equal((await stored(rejected.page)).abandoned,undefined);assert.equal(rejected.state.originalPosts,0);await rejected.ctx.close();checks.push('RECORDED_REJECTED_keeps_original_denial_not_fake_abandonment');
 const remote=await setup(browser,'remote',390);await remote.page.locator('[data-help-id="case-work.receipt.read"]').click();await remote.page.getByRole('heading',{name:'Исходный запрос прекращён',exact:true}).waitFor();assert.equal(remote.state.posts.length,0);assert.equal((await stored(remote.page)).abandoned.proof.operation_id,'REMOTE.CONTROL:1');await remote.ctx.close();checks.push('same_operator_other_device_exact_original_tombstone_readonly_no_control_POST');
}
async function foreignAndCorrupt(browser,checks){
 const foreign=await setup(browser,'foreign',390);assert.equal(await foreign.page.locator('[data-help-id="case-work.receipt.read"]').isDisabled(),true);await openRecovery(foreign.page);assert.equal(await foreign.page.locator('[data-help-id="metadata-intent.abandon.submit"]').isDisabled(),true);assert.equal(foreign.state.posts.length,0);await foreign.ctx.close();checks.push('foreign_actor_no_recovery_send');
 const {ctx,page,state}=await setup(browser,'unknown',390);await page.evaluate(()=>localStorage.setItem('wms.metadata-intent-control.v1:'+encodeURIComponent(location.origin)+':worker:CASE:7:'+JSON.parse(localStorage.getItem('wms.case-work.journal.v1')).pending.request_sha256,'{bad'));await page.locator('[data-help-id="case-work.refresh"]').click();await idle(page);
 assert.equal(await page.locator('[data-help-id="case-work.receipt.retry"]').isDisabled(),true);assert.ok((await stored(page)).pending);assert.equal(state.posts.length,0);checks.push('damaged_control_fail_closed_original_raw_retained');await ctx.close();
}
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({headless:true});const checks=[];
 try{await lostRecovery(browser,checks);await lostReadAndTabs(browser,checks);await simpleCases(browser,checks);await recordedRecovery(browser,checks);await otherTerminalProofs(browser,checks);await foreignAndCorrupt(browser,checks);
  fs.writeFileSync(path.join(out,'rendered-mock.json'),JSON.stringify({status:'PASS',checks,apiWrites:'INTERCEPTED_ONLY',staticFiles:dist,nativeAcceptance:false,hardware:false},null,2));console.log(checks.length+' rendered metadata recovery cases PASS');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
