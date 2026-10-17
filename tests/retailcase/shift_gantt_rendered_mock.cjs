// Production bundle, fully intercepted synthetic API responses. No live API or native effects.
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../..'),dist=path.join(root,'admin/wms_admin_frontend/dist'),out=path.join(root,'reports/retailcase/2026-10-15/shift-gantt-ui');
const wave={pick_wave_id:1,wave_code:'UI-WAVE',status:'LAUNCHED',ware_id:7,ware_name:'TEST warehouse',wave_kind:'CASE',order_count:1,task_count:3};
const tasks=['PARTIAL','WAIT_REPLENISHMENT','PICKED'].map((status,i)=>({case_pick_task_id:10+i,pick_wave_id:1,wave_code:wave.wave_code,status,total_lines:4,picked_lines:i+1,assigned_to:'UI-worker',blocking_reason:null}));
const kinds=['REACHTRUCK','CASE_PICKER','DOCK','VEHICLE'];
const timeline={warehouse_id:7,start_at:'2026-10-15T00:00:00Z',finish_at:'2026-10-16T00:00:00Z',observed_at:'2026-10-15T10:00:00Z',warehouse_time_zone:'UTC',resources:kinds.map((kind,i)=>({resource_id:'R:'+i,kind,label:kind,warehouse_id:7,source_state:'ACTIVE',availability:'UNKNOWN'})),events:[],unscheduled:[],assignments:[],sources:[],overlap_candidates:[]};
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({headless:true});const results=[];
try{for(const width of [360,390,1440]){
 const ctx=await browser.newContext({viewport:{width,height:900},serviceWorkers:'block'}),page=await ctx.newPage(),unexpected=[],posts=[],errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await ctx.route('**/*',async route=>{const req=route.request(),url=new URL(req.url()),p=url.pathname;
 if(!p.startsWith('/api/')){const file=path.join(dist,p==='/'?'index.html':p);if(!file.startsWith(dist)||!fs.existsSync(file)){unexpected.push(p);return route.fulfill({status:404,body:'missing'});}return route.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.svg':'image/svg+xml'})[path.extname(file)]||'application/octet-stream'});}
 let data;
 if(req.method()==='POST')posts.push(p);
 if(p==='/api/access/me')data={username:'UI-worker',permissions:[]};
 else if(p==='/api/access/navigation')data={username:'UI-worker',access_revision:1};
 else if(p==='/api/access/workspaces')data={warehouses:[{warehouse_id:7,title:'TEST warehouse',capabilities:{waves:true,resources:true}}],limit:50,has_more:false,navigation_only:true};
 else if(p==='/api/picking/waves')data=url.searchParams.get('status')==='LAUNCHED'?[wave]:[];
 else if(p==='/api/case-pick/tasks')data=tasks;
 else if(p==='/api/case-pick/shorts')data=[{case_pick_short_id:31,pick_wave_id:1,case_pick_task_id:10,status:'CREATED',articul:'UI-SKU',short_qty:1}];
 else if(p==='/api/resources/sessions'||p==='/api/inventory/recovery-shorts')data=[];
 else if(p==='/api/resources/timeline')data={...timeline,start_at:url.searchParams.get('start_at')||timeline.start_at,finish_at:url.searchParams.get('finish_at')||timeline.finish_at};
 else if(p==='/api/picking/shift-overview')data={warehouse_id:7,wave_ids:[1],observed_at:timeline.observed_at,waves:[{wave_id:1,readiness:{status:'READY',data:{blockers:[],summary:{}}},pick:{status:'ERROR',data:null,error:'TEST_SOURCE_UNAVAILABLE'},time:{status:'READY',data:{plan_status:'NO_APPROVED_PLAN'}},replenishment:{status:'READY',data:[]}}]};
 else{unexpected.push(p);return route.fulfill({status:404,json:{detail:'unmocked'}});}
 return route.fulfill({status:200,json:data});});
 await page.goto('http://127.0.0.1:3000/?page=workspace&workspace=shift');
 await page.getByLabel('Пользователь',{exact:true}).fill('UI-worker');await page.getByLabel('Пароль',{exact:true}).fill('test-only');await page.getByRole('button',{name:'Войти',exact:true}).click();
 await page.locator('.rg').waitFor();
 for(const kind of kinds)await page.locator('.rg-label').filter({hasText:kind}).waitFor();
 await page.getByRole('button',{name:/Текущая сборка/}).click();
 const card=page.locator('.ops-right');for(const status of ['PARTIAL','WAIT_REPLENISHMENT','PICKED'])await card.getByText(status,{exact:false}).waitFor();
 await page.getByRole('button',{name:/Риски запуска/}).click();await card.getByText(/Недостача ждёт решения/).waitFor();
 await page.getByRole('button',{name:'Волна UI-WAVE',exact:true}).click();await card.getByText(/Подготовка не проверена полностью/).waitFor();
 assert.equal(await page.locator('.ops-center [data-help-id="shift.scene.stage.UNREAD"] [role="button"]').count(),1);
 assert.equal(await page.locator('.ops-center [data-help-id="shift.scene.stage.CLEAR"] [role="button"]').count(),0);
 const missingHelp=await page.locator('button:visible').evaluateAll(xs=>xs.filter(x=>!x.title||!x.dataset.helpId).map(x=>x.textContent));assert.deepEqual(missingHelp,[]);
 await page.keyboard.press("Escape");await page.mouse.move(0,0);await page.locator("body").click({position:{x:2,y:2}});
 await page.screenshot({path:path.join(out,`shift-${width}.png`),fullPage:true});
 assert.deepEqual(errors,[]);assert.deepEqual(unexpected,[]);assert.ok(posts.every(p=>p==='/api/picking/shift-overview'));
 results.push({width,status:'PASS',checks:['actual open CASE statuses','actual pending shortage','failed preparation UNREAD not CLEAR','four resource families','all visible buttons help'],all_network_intercepted:true,synthetic_readonly_post:posts});await ctx.close();
}const assets=fs.readdirSync(path.join(dist,'assets')).filter(x=>/\.(js|css)$/.test(x)).map(name=>({name,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(dist,'assets',name))).digest('hex')}));fs.writeFileSync(path.join(out,'rendered-mock.json'),JSON.stringify({status:'PASS',kind:'OFFLINE_PRODUCTION_BUNDLE_MOCK',actual_api_calls:0,oracle_writes:0,hardware:false,assets,results},null,2));console.log(JSON.stringify(results));}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
