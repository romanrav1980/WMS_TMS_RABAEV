const fs=require('fs'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-22/T10',report={checks:[],errors:[],writes:[]};
const pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
(async()=>{
 const browser=await chromium.launch();
 try{
  for(const width of [1440,390]){
   const ctx=await browser.newContext({viewport:{width,height:width===390?844:1000}}),page=await ctx.newPage();let deny=false;
   page.on('pageerror',e=>report.errors.push(String(e)));
   await page.route('**/api/**',route=>{
    const r=route.request();if(!['GET','OPTIONS'].includes(r.method())&&!r.url().includes('/auth/')&&!r.url().includes('/picking/shift-overview')){report.writes.push(r.url());return route.abort();}return route.continue();
   });
   const real=await ctx.request.get('http://127.0.0.1:8088/api/case-pick/tasks?scope=all&ware_id=220793322&pick_wave_id=612&include_closed=true',{headers:{Authorization:'Basic '+Buffer.from('admin:'+pass).toString('base64')}});assert(real.ok());const task=(await real.json())[0];assert(task.case_pick_task_id===1168);
   await page.route('**/api/case-pick/tasks?*',route=>{
    const url=new URL(route.request().url());
    if(url.searchParams.has('pick_wave_id'))return deny?route.fulfill({status:403,contentType:'application/json',body:JSON.stringify({detail:{code:'DENIED'}})}):route.continue();
    return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(Array.from({length:200},(_,i)=>({...task,case_pick_task_id:100000+i})))});
   });
   const open=async()=>{
    await page.goto('http://127.0.0.1:3000/?page=workspace&workspace=shift&warehouse_id=220793322&wave_id=613');
    if(await page.locator('input[type=password]').count()){await page.fill('input[autocomplete=username]','admin');await page.fill('input[type=password]',pass);await page.click('button[type=submit]');}
   };
   await open();const card=page.locator('section[aria-label="Волна NB22.B.220793322"]');
   await card.waitFor();await page.waitForFunction(()=>/собрано/i.test(document.querySelector('section[aria-label="Волна NB22.B.220793322"]')?.textContent??''),null,{timeout:10000}).catch(async error=>{report.card=await card.innerText();await page.screenshot({path:out+`/selected-wave-failed-${width}.png`});throw error;});
   report.checks.push({width,test:'Real selected wave remains CONTROLLED despite capped unrelated global fixture'});
   const gantt=page.locator('section.rg[aria-label="Общий Гант ресурсов"]');await gantt.locator('input[type=search]').fill('33665');
   const bars=gantt.locator('button[title*="Погрузка подтверждена · рейс 33665"]');await bars.first().waitFor();assert.equal(await bars.count(),2);
   assert((await bars.first().getAttribute('title')).includes('подтверждённый момент'));await bars.first().click();
   const event=page.locator('section.ops-card').filter({hasText:'Погрузка подтверждена · рейс 33665'});assert((await event.innerText()).includes('N22DA1168'));assert((await event.innerText()).includes('N22VA1168'));assert(!(await event.innerText()).includes('окончание не задано'));
   await event.screenshot({path:out+`/physical-point-${width}.png`});report.checks.push({width,test:'One actual confirmation binds dock and vehicle as a known moment, not occupancy'});
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   deny=true;await open();await card.waitFor();await page.waitForFunction(()=>document.querySelector('section[aria-label="Волна NB22.B.220793322"]')?.textContent.includes('сборка не прочитана полностью'));
   assert(!(await card.innerText()).includes('1169'));report.checks.push({width,test:'Selected-wave 403 clears former task and does not infer completion from global list'});
   await ctx.close();
  }
  assert.deepStrictEqual(report.errors,[]);assert.deepStrictEqual(report.writes,[]);report.status='PASS';
 }finally{await browser.close();fs.writeFileSync(out+'/selected-wave-ui.json',JSON.stringify(report,null,2));}
 console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exit(1);});
