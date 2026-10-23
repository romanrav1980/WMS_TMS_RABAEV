const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const ROOT=path.resolve(__dirname,'../..'),OUT=path.join(ROOT,'runtime/test-evidence/tradecase/2026-10-23/T10');
const source=JSON.parse(fs.readFileSync(path.join(OUT,'dock-plan-live.json'),'utf8')).tag+'.Q';
const pass=fs.readFileSync(path.join(ROOT,'AGENTS.md'),'utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const headers={Authorization:'Basic '+Buffer.from('admin:'+pass).toString('base64')};
const base='http://127.0.0.1:8088/api/tradecase/warehouses/220793322/yard';
const target=process.env.UI_BASE||'http://127.0.0.1:3021';
const report={status:'FAIL',basis:'Actual UI/native plan, injected lost response after commit and403 before retry; exact replay, move, Gantt read and cancel actual',screens:[],errors:[]};
const panel=p=>p.getByLabel('План ворот',{exact:true});
async function enter(p){
 const password=p.locator('input[type=password]'),open=p.locator('[aria-label="Процессы старшего смены"]').getByRole('button',{name:/Двор и ворота/});
 await Promise.race([password.waitFor({timeout:30000}),open.waitFor({timeout:30000})]);
 if(await password.count()){await p.fill('input[autocomplete=username]','admin');await password.fill(pass);await p.click('button[type=submit]');}
 await open.waitFor();await open.click();await panel(p).getByRole('button',{name:'Обновить план',exact:true}).waitFor();
}
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  for(const width of [1440,390]){
   const context=await browser.newContext({viewport:{width,height:1000},timezoneId:'Europe/Moscow'}),p=await context.newPage();
   const tag='DPU'+width+'.'+Date.now(),vehicle=tag,posts=[];let committed=null,drop=true,deny=true;
   const start=new Date(Date.now()+4*3600e3),finish=new Date(+start+3600e3);
   start.setUTCSeconds(0,0);finish.setUTCSeconds(0,0);
   const local=d=>new Date(+d+3*3600e3).toISOString().slice(0,16);
   const vresponse=await context.request.post(base+'/visits',{headers,data:{operation_id:tag+'.visit',supply_ids:[source],vehicle,planned_arrival_at:start.toISOString()}});
   assert.equal(vresponse.status(),200,await vresponse.text());const visit=await vresponse.json();let planId=null;
   p.on('pageerror',e=>report.errors.push(String(e)));
   await p.route('**/yard/dock-plans',async route=>{
    if(route.request().method()!=='POST')return route.continue();posts.push(route.request().postData());
    if(!drop){if(deny){deny=false;return route.fulfill({status:403,json:{detail:{code:'YARD_ACCESS_DENIED',outcome_confirmed:false,retry_same_operation_id:true}},headers:{'access-control-allow-origin':'*'}});}return route.continue();}
    drop=false;const response=await route.fetch();if(response.status()!==200)return route.fulfill({response});
    committed=await response.json();planId=committed.plan_id;
    return route.fulfill({status:503,json:{detail:{code:'YARD_RESULT_UNKNOWN',outcome_confirmed:false,retry_same_operation_id:true}},headers:{'access-control-allow-origin':'*'}});
   });
   try{
    const t=Date.now();await p.goto(target+'/?page=workspace&workspace=shift&warehouse_id=220793322');await enter(p);const ready=Date.now()-t;
    await panel(p).getByRole('button',{name:'Запланировать ворота',exact:true}).click();
    await panel(p).getByLabel('Визит',{exact:true}).selectOption(String(visit.visit_id));
    await panel(p).getByLabel('Ворота',{exact:true}).fill('B22D1161');
    await panel(p).getByLabel('Начало',{exact:true}).fill(local(start));await panel(p).getByLabel('Конец',{exact:true}).fill(local(finish));
    await panel(p).getByRole('button',{name:'Запланировать',exact:true}).click();
    await panel(p).getByRole('button',{name:'Повторить команду плана',exact:true}).waitFor({timeout:30000});assert(committed);
    await p.reload();await enter(p);await panel(p).getByRole('button',{name:'Повторить команду плана',exact:true}).click();
    await panel(p).getByText('Сервер не разрешил повтор сохранённой команды.',{exact:false}).waitFor();
    await p.reload();await enter(p);
    const response=p.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/yard/dock-plans'));
    await panel(p).getByRole('button',{name:'Повторить команду плана',exact:true}).click();
    const replay=await response;assert.equal(replay.status(),200);const result=await replay.json();assert(result.replayed&&result.plan_id===planId);assert.equal(posts.length,3);assert(posts.every(b=>b===posts[0]));
    await panel(p).getByText('План ворот сохранён.',{exact:true}).waitFor();
    const row=panel(p).getByRole('listitem').filter({hasText:vehicle});await row.waitFor();
    await row.getByRole('button',{name:'Перенести',exact:true}).click();
    await row.getByLabel('Ворота',{exact:true}).fill('N22DA1168');
    const moved=p.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/'+planId+'/move'));
    await row.getByRole('button',{name:'Перенести план',exact:true}).click();assert.equal((await moved).status(),200);
    await panel(p).getByText('План перенесён.',{exact:true}).waitFor();
    const timeline=await context.request.get('http://127.0.0.1:8088/api/resources/timeline?'+new URLSearchParams({warehouse_id:'220793322',start_at:start.toISOString(),finish_at:finish.toISOString()}),{headers});
    assert.equal(timeline.status(),200);const tl=await timeline.json();fs.writeFileSync(path.join(OUT,'dock-plan-timeline-'+width+'.json'),JSON.stringify(tl,null,2));
    assert(JSON.stringify(tl).includes('YARD_DOCK_PLAN:'+planId),'Actual Gantt must contain plan');
    const help=await panel(p).locator('button').evaluateAll(bs=>bs.filter(b=>!b.title||!b.dataset.helpId).map(b=>b.textContent));assert.deepEqual(help,[]);
    const size=await p.evaluate(()=>({width:innerWidth,document:document.documentElement.scrollWidth}));assert(size.document<=size.width+1,JSON.stringify(size));
    const screenshot=path.join(OUT,'dock-plan-live-'+width+'.png');await panel(p).screenshot({path:screenshot});
    await row.getByRole('button',{name:'Отменить план',exact:true}).click();await row.getByLabel('Причина отмены плана',{exact:true}).fill('End actual browser plan proof');
    const cancel=p.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/'+planId+'/cancel'));
    await row.getByRole('button',{name:'Отменить план',exact:true}).filter({has:p.locator('xpath=ancestor::form')}).count();
    await row.locator('form').getByRole('button',{name:'Отменить план',exact:true}).click();assert.equal((await cancel).status(),200);
    await panel(p).getByText('План отменён.',{exact:true}).waitFor();report.screens.push({width,plan_id:planId,visit_id:visit.visit_id,ready_ms:ready,size,screenshot,post_count:posts.length,exact_bytes_replay:true,gantt_actual:true});
   }catch(e){report.failure={error:String(e),text:await panel(p).innerText(),html:await panel(p).innerHTML()};await p.screenshot({path:path.join(OUT,"dock-plan-live-failed.png"),fullPage:true});throw e;}finally{
    if(planId){const plans=await context.request.get(base+'/dock-plans?'+new URLSearchParams({from:start.toISOString(),to:finish.toISOString()}),{headers});if(plans.ok()){const active=(await plans.json()).plans.find(x=>x.plan_id===planId);if(active){const r=await context.request.post(base+'/dock-plans/'+planId+'/cancel',{headers,data:{operation_id:tag+'.cleanup.plan',expected_version:active.version,reason:'End actual UI proof'}});assert.equal(r.status(),200,await r.text());}}}
    const visits=await context.request.get(base+'/visits',{headers});assert.equal(visits.status(),200);const v=(await visits.json()).visits.find(x=>x.visit_id===visit.visit_id);
    if(v&&!['CANCELLED','DEPARTED'].includes(v.state)){const r=await context.request.post(base+'/visits/'+v.visit_id+'/transitions',{headers,data:{operation_id:tag+'.cleanup.visit',expected_version:v.version,action:'CANCEL',reason:'End actual UI proof'}});assert.equal(r.status(),200,await r.text());}
    await context.close();
   }
  }
  assert.deepEqual(report.errors,[]);report.status='PASS';
 }finally{await browser.close();fs.writeFileSync(path.join(OUT,'dock-plan-live-ui.json'),JSON.stringify(report,null,2));}
 console.log(JSON.stringify({status:report.status,screens:report.screens.length}));
})().catch(e=>{console.error(e);process.exit(1)});
