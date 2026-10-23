// Genuine native commit, injected503 after commit and simulated403 on retry; then actual exact replay.
const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const ROOT=path.resolve(__dirname,'../..'),OUT=path.join(ROOT,'runtime/test-evidence/tradecase/2026-10-23/T10');
const SOURCE=JSON.parse(fs.readFileSync(path.join(OUT,'YI2338ff7c3a0f.json'),'utf8')).tag;
const pass=fs.readFileSync(path.join(ROOT,'AGENTS.md'),'utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const auth='Basic '+Buffer.from('admin:'+pass).toString('base64');
const RUN=Date.now();
const report={status:'FAIL',basis:'Actual browser/native commit; injected503 after commit and simulated403 before retry reaches native; actual exact replay',screens:[],errors:[]};
const panel=p=>p.locator('section[aria-label="Двор"]');
async function enter(p){
 const password=p.locator('input[type=password]'),open=p.locator('[aria-label="Процессы старшего смены"]').getByRole('button',{name:/Двор и ворота/});
 await Promise.race([password.waitFor({timeout:30000}),open.waitFor({timeout:30000})]);
 if(await password.count()){await p.fill('input[autocomplete=username]','admin');await password.fill(pass);await p.click('button[type=submit]');}
 await open.waitFor({timeout:30000});await open.click();await panel(p).getByLabel('Назначение визита').waitFor();
}
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  for(const width of [1440,390]){
   const context=await browser.newContext({viewport:{width,height:width===390?844:1000}}),p=await context.newPage();
   const vehicle='YARDUI'+width+'.'+Date.now(),posts=[];let committed=null,drop=true,denyRetry=true;
   p.on('pageerror',e=>report.errors.push(String(e)));
   await p.route('**/api/tradecase/warehouses/220793322/yard/visits',async route=>{
    if(route.request().method()!=='POST')return route.continue();
    posts.push(route.request().postData());
    if(!drop){
     if(denyRetry){denyRetry=false;return route.fulfill({status:403,json:{detail:{code:'YARD_ACCESS_DENIED',outcome_confirmed:true,retry_same_operation_id:false}},headers:{'access-control-allow-origin':'*'}});}
     return route.continue();
    }drop=false;
    const response=await route.fetch();
    if(response.status()!==200)return route.fulfill({response});
    committed=await response.json();
    return route.fulfill({status:503,json:{detail:{code:'YARD_RESULT_UNKNOWN',outcome_confirmed:false,retry_same_operation_id:true}},headers:{'access-control-allow-origin':'*'}});
   });
   try{
    const start=Date.now();await p.goto('http://127.0.0.1:3000/?page=workspace&workspace=shift&warehouse_id=220793322');await enter(p);
    const ready=Date.now()-start;
    await panel(p).getByLabel('Назначение визита').selectOption('INBOUND');
    await panel(p).getByLabel('Основания поставки',{exact:true}).fill(SOURCE+'.A1\n'+SOURCE+'.A2');
    await panel(p).getByLabel('Номер машины',{exact:true}).fill(vehicle);
    await panel(p).getByLabel('План приезда',{exact:true}).fill('2026-10-23T09:00');
    await panel(p).getByRole('button',{name:'Добавить визит',exact:true}).click();
    await panel(p).getByRole('button',{name:'Повторить',exact:true}).waitFor({timeout:30000});assert(committed&&committed.visit_kind==='INBOUND');
    await p.reload();await enter(p);await panel(p).getByRole('button',{name:'Повторить',exact:true}).waitFor();
    const pending=await panel(p).getByRole('status').filter({hasText:'не подтверждена'}).innerText();assert(pending.includes(vehicle)&&pending.includes(SOURCE+'.A1'));
    await panel(p).getByRole('button',{name:'Повторить',exact:true}).click();
    await panel(p).getByText('Сервер не разрешил повтор сохранённой команды.',{exact:false}).waitFor();
    await p.reload();await enter(p);await panel(p).getByRole('button',{name:'Повторить',exact:true}).waitFor();
    const response=p.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/yard/visits'));
    await panel(p).getByRole('button',{name:'Повторить',exact:true}).click();
    const replay=await response;assert.equal(replay.status(),200);const result=await replay.json();
    assert.equal(result.visit_id,committed.visit_id);assert.equal(result.replayed,true);assert.equal(posts.length,3);assert.equal(posts[0],posts[1]);assert.equal(posts[1],posts[2]);
    await panel(p).getByText('Визит '+result.visit_id,{exact:true}).waitFor();
    const text=await panel(p).innerText();assert(text.includes('приёмка: '+SOURCE+'.A1, '+SOURCE+'.A2'));assert(!text.includes('рейс null'));
    const href=await panel(p).getByRole('link',{name:'Как зарегистрировать машину на приёмку'}).getAttribute('href');
    const help=await context.request.get('http://127.0.0.1:3000'+href);assert.equal(help.status(),200);assert((await help.text()).includes('id="yard-inbound"'));
    const missing=await panel(p).locator('button').evaluateAll(bs=>bs.filter(b=>!b.title||!b.dataset.helpId).map(b=>b.textContent));assert.deepEqual(missing,[]);
    const size=await p.evaluate(()=>({viewport:innerWidth,document:document.documentElement.scrollWidth}));assert(size.document<=size.viewport+1,JSON.stringify(size));
    const screenshot=path.join(OUT,'inbound-live-'+width+'-'+RUN+'.png');await panel(p).screenshot({path:screenshot});
    report.screens.push({width,visit:result.visit_id,operation_id:result.operation_id,ready_ms:ready,size,screenshot,actual_post_and_exact_replay:true,help:href});
   }finally{
    const active=await context.request.get('http://127.0.0.1:8088/api/tradecase/warehouses/220793322/yard/visits',{headers:{Authorization:auth}});
    assert.equal(active.status(),200);
    for(const v of (await active.json()).visits.filter(v=>v.vehicle===vehicle)){
     const cleanup=await context.request.post('http://127.0.0.1:8088/api/tradecase/warehouses/220793322/yard/visits/'+v.visit_id+'/transitions',{headers:{Authorization:auth},data:{operation_id:'YARDUI.cleanup.'+v.visit_id,expected_version:v.version,action:'CANCEL',reason:'End actual browser inbound expectation test'}});
     assert.equal(cleanup.status(),200,await cleanup.text());
    }
    await context.close();
   }
  }
  assert.deepEqual(report.errors,[]);report.status='PASS';
 }finally{await browser.close();const data=JSON.stringify(report,null,2);fs.writeFileSync(path.join(OUT,'inbound-live-ui-'+RUN+'.json'),data);fs.writeFileSync(path.join(OUT,'inbound-live-ui.json'),data);}
 console.log(JSON.stringify({status:report.status,screens:report.screens.length}));
})().catch(e=>{console.error(e);process.exit(1)});
