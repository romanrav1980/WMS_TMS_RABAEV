const fs=require('fs'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-22/T10';fs.mkdirSync(out,{recursive:true});
const pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const report={checks:[],errors:[],writes:[],overview:[],http:[]};let browser;
(async()=>{
 browser=await chromium.launch();
 for(const width of [1440,390]){
  const ctx=await browser.newContext({viewport:{width,height:width===390?844:1000}}),page=await ctx.newPage();let phase='positive';
  page.on('pageerror',e=>report.errors.push(String(e)));
  page.on('requestfinished',async req=>{if(req.url().includes('/api/'))report.http.push({method:req.method(),path:new URL(req.url()).pathname,elapsedMs:req.timing().responseEnd,status:(await req.response())?.status()});});
  await ctx.route('**/api/**',route=>{
   const req=route.request();if(req.method()==='POST'&&req.url().includes('/picking/shift-overview')){const b=req.postDataJSON();report.overview.push({phase,...b});if(b.warehouse_id===219023232)assert(!b.wave_ids.includes(604));return route.continue();}
   if(!['GET','OPTIONS'].includes(req.method())&&!req.url().includes('/auth/')){report.writes.push(req.url());return route.abort();}return route.continue();
  });
  const url=w=>'http://127.0.0.1:3000/?'+new URLSearchParams({page:'workspace',workspace:'shift',warehouse_id:String(w),wave_id:'604'});
  const login=async()=>{if(await page.locator('input[type=password]').count()){await page.fill('input[autocomplete=username]','admin');await page.fill('input[type=password]',pass);await page.click('button[type=submit]');}};
  const began=Date.now();await page.goto(url(220639789));await login();
  report.asset=await page.locator('script[type=module][src]').getAttribute('src');
  const card=page.locator('section[aria-label="Волна FP21.220639789"]');await card.waitFor({timeout:30000});assert((await card.innerText()).includes('Завершена'));assert(!(await card.innerText()).includes('Риски запуска'));
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await card.screenshot({path:out+'/wave-direct-'+width+'.png'});
  report.checks.push({width,test:'real DONE604 outside active wave lists opened from native header/overview',usefulScreenMs:Date.now()-began});
  await card.getByRole('button',{name:'Панель смены',exact:true}).click();await card.waitFor({timeout:30000});assert.equal(await page.locator('input[type=password]').count(),0);
  assert.equal(new URL(page.url()).searchParams.get('wave_id'),'604');assert.equal(new URL(page.url()).searchParams.get('warehouse_id'),'220639789');assert.equal(new URL(page.url()).searchParams.get('page'),'workspace');assert(!page.url().includes('shift-supervisor-wave.html'));
  report.checks.push({width,test:'wave action keeps actual shift/warehouse/selection and never opens static stage demo'});
  if(width===390)await page.locator('[data-help-id="workspace.role.select"]').selectOption('director');else await page.getByRole('tab',{name:'Директор РЦ',exact:true}).click();
  await page.getByRole('button',{name:'Панель смены',exact:true}).click();await page.waitForFunction(()=>document.querySelector('[data-help-id="workspace.role.select"]')?.value==='shift');
  assert.equal(new URL(page.url()).searchParams.get('workspace'),'shift');assert.equal(new URL(page.url()).searchParams.get('warehouse_id'),'220639789');assert.equal(new URL(page.url()).searchParams.get('wave_id'),null);assert.equal(await page.locator('input[type=password]').count(),0);
  report.checks.push({width,test:'director opens actual shift with current warehouse; no stale wave'});
  phase='foreign';await page.goto(url(219023232));await login();await page.getByRole('alert').filter({hasText:'Выбранная волна недоступна'}).waitFor({timeout:30000});assert.equal(await card.count(),0);
  report.checks.push({width,test:'foreign selected warehouse rejects wave604; no wrong wave in overview batch'});
  phase='denied';await page.route('**/api/picking/waves/604/header?*',route=>route.fulfill({status:403,contentType:'application/json',body:JSON.stringify({detail:'Denied'})}));
  await page.goto(url(220639789));await login();await page.getByRole('alert').filter({hasText:'Выбранная волна недоступна'}).waitFor({timeout:30000});assert.equal(await card.count(),0);
  report.checks.push({width,test:'403 clears selected header/card; no static fallback'});await ctx.close();
 }
 assert.deepEqual(report.errors,[]);assert.deepEqual(report.writes,[]);report.status='PASS';fs.writeFileSync(out+'/wave-navigation-ui.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser.close();
})().catch(async e=>{report.status='FAIL';report.error=String(e);const p=browser?.contexts().at(-1)?.pages().at(-1);if(p){report.url=p.url();report.dom=await p.locator('.ops').innerText({timeout:1000}).catch(()=>null);await p.screenshot({path:out+'/wave-navigation-failure.png',fullPage:true});}fs.writeFileSync(out+'/wave-navigation-ui.json',JSON.stringify(report,null,2));console.error(e);if(browser)await browser.close();process.exit(1);});
