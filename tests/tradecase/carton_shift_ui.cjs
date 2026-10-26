const fs=require('fs'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-26/T08/carton-scale/physical';
const state=JSON.parse(fs.readFileSync(out+'/state.json','utf8'));
const phase=process.env.CARTON_SHIFT_PHASE||'initial';assert(/^[a-z0-9-]+$/.test(phase));
const pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const report={checks:[],writes:[],errors:[],httpErrors:[],api:[]};let browser;
(async()=>{
 browser=await chromium.launch();
 for(const width of[1440,390]){
  const context=await browser.newContext({viewport:{width,height:width===390?844:1000}}),page=await context.newPage();
  page.on('pageerror',e=>report.errors.push(String(e)));
  page.on('response',r=>{if(r.status()>=400&&r.url().includes('/api/'))report.httpErrors.push({status:r.status(),url:r.url()});});
  page.on('requestfinished',r=>{if(r.url().includes('/api/'))report.api.push({width,method:r.method(),path:new URL(r.url()).pathname,ms:r.timing().responseEnd});});
  await page.route('**/api/**',route=>{
   const r=route.request();
   if(!['GET','OPTIONS'].includes(r.method())&&!r.url().includes('/auth/')&&!r.url().endsWith('/picking/shift-overview')){report.writes.push(r.url());return route.abort();}
   return route.continue();
  });
  const start=Date.now();
  await page.goto('http://127.0.0.1:3000/?'+new URLSearchParams({page:'workspace',workspace:'shift',warehouse_id:String(state.fixture.warehouse_id),wave_id:'636'}));
  if(await page.locator('input[type=password]').count()){await page.fill('input[autocomplete=username]','admin');await page.fill('input[type=password]',pass);await page.click('button[type=submit]');}
  const card=page.locator('section.ops-card[aria-label^="Волна "]');await card.waitFor({timeout:30000});
  await page.waitForFunction(()=>!document.querySelector('section.ops-card[aria-label^="Волна "]')?.textContent.includes('Подробные проверки загружаются'),null,{timeout:30000});
  const text=await card.innerText();assert(text.includes('660'),'Selected wave must retain 660 tasks');
  assert(text.includes('Сборка коробов и штук'));
  assert(!text.includes('заданий сборки в выборке нет'));
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Document overflow');
  await card.scrollIntoViewIfNeeded();await page.screenshot({path:out+'/shift-660-'+phase+'-'+width+'.png'});
  report.checks.push({width,usefulScreenMs:Date.now()-start,card:text});await context.close();
 }
 assert.deepStrictEqual(report.writes,[]);assert.deepStrictEqual(report.errors,[]);assert.deepStrictEqual(report.httpErrors,[]);report.status='PASS';
})().catch(error=>{report.status='FAIL';report.error=String(error);process.exitCode=1;}).finally(async()=>{fs.writeFileSync(out+'/shift-660-'+phase+'-ui.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser?.close();});
