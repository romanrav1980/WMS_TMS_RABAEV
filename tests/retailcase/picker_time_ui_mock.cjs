// Production CASE-work bundle; all requests intercepted. No actual native facts.
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../..'),dist=path.join(root,'terminal/wms_terminal_web/dist'),out=path.join(root,'reports/retailcase/2026-10-15/picker-time-ui'),origin='http://127.0.0.1:8088';
const canonical=v=>JSON.stringify(Object.fromEntries(Object.keys(v).sort().map(k=>[k,v[k]]))),hash=v=>crypto.createHash('sha256').update(v).digest('hex').toUpperCase();
const blank=()=>({operator_id:'worker',stream_version:0,shift_state:'OFF',work_state:'IDLE',warehouse_id:null,resource_session_id:null,resource_id:null,source_kind:null,source_id:null,shift_started_at:null,work_started_at:null,pause_started_at:null,last_event_at:null,work_coverage_certified:false,source_mode:'MANUAL_CONFIRMED'});
function apply(state,b){const before=state.current.stream_version,at=`2026-10-15T18:00:${String(before+1).padStart(2,'0')}+00:00`,s={...state.current,stream_version:before+1,last_event_at:at};
 if(b.action==='ACTUAL_SHIFT_START')Object.assign(s,{shift_state:'OPEN',warehouse_id:7,resource_id:4,resource_session_id:3,shift_started_at:at});
 if(b.action==='WORK_START')Object.assign(s,{work_state:'WORK',source_kind:b.source_kind,source_id:b.source_id,work_started_at:at});
 if(b.action==='PAUSE')Object.assign(s,{work_state:'PAUSED',pause_started_at:at});
 if(b.action==='RESUME')Object.assign(s,{work_state:'WORK',pause_started_at:null});
 if(b.action==='WORK_FINISH')Object.assign(s,{work_state:'IDLE',source_kind:null,source_id:null,work_started_at:null,pause_started_at:null});
 if(b.action==='ACTUAL_SHIFT_FINISH')Object.assign(s,{shift_state:'OFF',warehouse_id:null,resource_id:null,resource_session_id:null,shift_started_at:null});state.current=s;
 return {operation_id:b.operation_id,actor:'worker',action:b.action,resource_session_id:b.resource_session_id,warehouse_id:7,request_sha256:hash(canonical(b)),outcome:'APPLIED',outcome_confirmed:true,changed:true,may_create_corrected_operation:false,error_code:null,stock_posted:false,event_at:at,before_version:before,after_version:before+1,state:s};}
async function setup(browser,mode='normal',width=390){const ctx=await browser.newContext({viewport:{width,height:844},serviceWorkers:'block'}),state={mode,current:blank(),acks:new Map(),posts:[],unexpected:[],errors:[],allowReceipt:false,revoked:false};
 if(mode==='warehouse')state.current={...blank(),stream_version:2,shift_state:'OPEN',work_state:'WORK',warehouse_id:7,resource_session_id:3,resource_id:4,source_kind:'WAREHOUSE_TASK',source_id:1188,shift_started_at:'2026-10-15T18:00:00Z',work_started_at:'2026-10-15T18:00:01Z',last_event_at:'2026-10-15T18:00:01Z'};
 if(mode==='quota')await ctx.addInitScript(()=>{const old=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k.startsWith('wms.picker-time.journal.v1:'))throw new DOMException('quota','QuotaExceededError');return old.call(this,k,v);};});
 await ctx.route('**/*',async route=>{const req=route.request(),u=new URL(req.url()),p=u.pathname;
 if(!p.startsWith('/api/')){const file=path.join(dist,p.endsWith('/')?p+'index.html':p);if(!file.startsWith(dist)||!fs.existsSync(file)){state.unexpected.push(p);return route.fulfill({status:404,body:'missing'});}return route.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.svg':'image/svg+xml'})[path.extname(file)]||'application/octet-stream'});}
 let data;
 if(p==='/api/terminal/auth/me')data={username:'worker',display_name:'UI worker',user_group:'TEST',permissions:['case_pick_execute']};
 else if(p.endsWith('/resource-context')){if(state.caseDenied)return route.fulfill({status:403,json:{detail:'CASE unavailable'}});const task=Number(p.split('/')[4]);data={task_id:task,warehouse_id:7,status:'IN_PROGRESS',assignment_version:2,content_version:1,assigned_to:'worker',resource_id:4,resource_session_id:3,equipment_id:null,started_at_instant:'2026-10-15T17:00:00Z',started_shift_time_zone:null,current_actor:'worker'};}
 else if(p.endsWith('/resource-sessions')){const task=Number(p.split('/')[4]);data={task_id:task,warehouse_id:7,current_actor:'worker',action:'START',items:[{resource_session_id:3,resource_id:4,equipment_id:null,resource_code:'PICKER',ready:true,reason:null}],command_revalidates:true};}
 else if(p.startsWith('/api/resources/picker-time')){
 if(state.revoked)return route.fulfill({status:403,json:{detail:'revoked'}});
 if(p.endsWith('/me/current'))data=state.current;
 else if(req.method()==='POST'){
 const raw=req.postData();state.posts.push(raw);const b=JSON.parse(raw);let receipt=state.acks.get(b.operation_id);if(!receipt){receipt=apply(state,b);state.acks.set(b.operation_id,receipt);}
 if(mode==='lost'&&state.posts.length===1)return route.abort('failed');
 data=mode==='mismatch'?{...receipt,request_sha256:'F'.repeat(64)}:receipt;
 }else if(p.includes('/commands/')){data=state.allowReceipt?state.acks.get(decodeURIComponent(p.split('/').pop())):null;if(!data)return route.fulfill({status:404,json:{detail:'not found'}});}
 }else{state.unexpected.push(p);return route.fulfill({status:404,json:{detail:'unmocked'}});}
 return route.fulfill({status:200,json:data});});
 async function open(task=7){const page=await ctx.newPage();page.on('pageerror',e=>state.errors.push(String(e)));await page.goto(origin+`/case-work/?task_id=${task}`);await login(page);return page;}
 const page=await open();return{ctx,page,state,open};}
async function login(page){await page.locator('[data-help-id="assembly.login.username"]').fill('worker');await page.locator('[data-help-id="assembly.login.password"]').fill('TEST');await page.locator('[data-help-id="assembly.login.submit"]').click();await page.locator('.pt-panel').waitFor();await idle(page);await page.locator('[data-help-id="picker-time.open"]').click();}
async function idle(page){await page.waitForFunction(()=>{const x=document.querySelector('[data-help-id="picker-time.refresh"]');return x&&!x.disabled;});}
async function click(page,action){await page.locator('[data-help-id="picker-time.reason"]').fill('Подтверждаю ручную отметку времени');await page.locator('[data-help-id="picker-time.'+action.toLowerCase()+'"]').click();await idle(page);}
async function journal(page){return page.evaluate(()=>JSON.parse(localStorage.getItem('wms.picker-time.journal.v1:'+location.origin+':worker')||'null'));}
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({headless:true}),checks=[];
try{
 for(const width of [360,390,1440]){const x=await setup(browser,'normal',width);for(const a of ['ACTUAL_SHIFT_START','WORK_START','PAUSE','RESUME','WORK_FINISH','ACTUAL_SHIFT_FINISH'])await click(x.page,a);
 assert.equal(x.state.posts.length,6);assert.equal(x.state.current.stream_version,6);assert.equal(x.state.current.shift_state,'OFF');assert.equal((await journal(x.page)).pending,null);assert.ok(x.state.posts.every(raw=>raw===canonical(JSON.parse(raw))));
 await x.page.getByText(/Полнота времени сборки не подтверждена/).waitFor();await x.page.mouse.move(0,0);await x.page.screenshot({path:path.join(out,`time-${width}.png`),fullPage:true});assert.deepEqual(x.state.errors,[]);assert.deepEqual(x.state.unexpected,[]);checks.push('six_explicit_transitions_'+width);await x.ctx.close();}
 {const x=await setup(browser,'warehouse');for(const a of ['PAUSE','RESUME','WORK_FINISH'])await click(x.page,a);assert.ok(x.state.posts.every(raw=>{const b=JSON.parse(raw);return b.source_kind==='WAREHOUSE_TASK'&&b.source_id===1188;}));await click(x.page,'WORK_START');const b=JSON.parse(x.state.posts[3]);assert.equal(b.source_kind,'CASE_PICK_TASK');assert.equal(b.source_id,7);checks.push('original_WAREHOUSE_TASK_pinned_pause_resume_finish_then_new_CASE_work');await x.ctx.close();}
 {const x=await setup(browser,'lost');await click(x.page,'ACTUAL_SHIFT_START');const original=(await journal(x.page)).pending;assert.ok(original);await x.page.reload();await login(x.page);assert.equal((await journal(x.page)).pending.wire,original.wire);
 const second=await x.open(99);await second.getByText('Исход запроса неизвестен',{exact:true}).waitFor();assert.equal((await journal(second)).pending.body.resource_session_id,3);
 await second.locator('[data-help-id="picker-time.retry"]').click();await idle(second);assert.equal(x.state.posts[0],x.state.posts[1]);assert.equal(x.state.current.stream_version,1);assert.equal((await journal(second)).pending,null);checks.push('lost_reload_two_tabs_changed_CASE_exact_same_wire_session_pinned');assert.deepEqual(x.state.unexpected,[]);await x.ctx.close();}
 {const x=await setup(browser,'lost');await click(x.page,'ACTUAL_SHIFT_START');x.state.allowReceipt=true;await x.page.locator('[data-help-id="picker-time.receipt"]').click();await idle(x.page);assert.equal(x.state.posts.length,1);assert.equal((await journal(x.page)).pending,null);checks.push('GET_receipt_recovers_without_POST');await x.ctx.close();}
 {const x=await setup(browser,'lost');await click(x.page,'ACTUAL_SHIFT_START');x.state.caseDenied=true;await x.page.reload();await login(x.page);await x.page.locator('[data-help-id="picker-time.retry"]').click();await idle(x.page);assert.equal(x.state.posts[0],x.state.posts[1]);assert.equal((await journal(x.page)).pending,null);checks.push('CASE_context_denied_does_not_hide_independent_time_exact_retry');await x.ctx.close();}
 {const x=await setup(browser,'mismatch');await click(x.page,'ACTUAL_SHIFT_START');assert.ok((await journal(x.page)).pending);x.state.revoked=true;await x.page.locator('[data-help-id="picker-time.receipt"]').click();await idle(x.page);assert.ok((await journal(x.page)).pending);checks.push('malformed_ACK_and_403_preserve_unknown');await x.ctx.close();}
 {const x=await setup(browser,'quota');await click(x.page,'ACTUAL_SHIFT_START');assert.equal(x.state.posts.length,0);checks.push('quota_before_POST_zero_commands');await x.ctx.close();}
 const entry=fs.readFileSync(path.join(dist,'case-work/index.html'),'utf8');const assets=[...entry.matchAll(/(?:src|href)="([^\"]+\.(?:js|css))"/g)].map(m=>{const file=m[1];return{file,sha256:hash(fs.readFileSync(path.join(dist,file)))};});
 fs.writeFileSync(path.join(out,'rendered-mock.json'),JSON.stringify({status:'PASS',checks,assets,actual_api_calls:0,oracle_writes:0,hardware:false,all_network_intercepted:true,kind:'PRODUCTION_BUNDLE_SYNTHETIC_RESPONSES'},null,2));console.log(checks);
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
