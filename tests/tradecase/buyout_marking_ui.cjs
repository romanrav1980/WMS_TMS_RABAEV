const fs=require('fs'),assert=require('assert');
const{chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-26/T05';
const proof=JSON.parse(fs.readFileSync(out+'/program-25-boxes.json','utf8')),reads=JSON.parse(fs.readFileSync(out+'/buyout-marking-read-carrier.json','utf8'));
const pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1],report={checks:[],writes:[],errors:[]};let browser;
(async()=>{
 browser=await chromium.launch();
 for(const width of[1440,390])for(const mode of['AFTER','TRANSIT']){
  const ctx=await browser.newContext({viewport:{width,height:width===390?844:1000}}),page=await ctx.newPage();
  page.on('pageerror',e=>report.errors.push(String(e)));
  await page.route('**/api/**',route=>{const req=route.request();if(!['GET','OPTIONS'].includes(req.method())&&!req.url().includes('/auth/')){report.writes.push(req.url());return route.abort();}return route.continue();});
  const id='B25.'+proof.fixture.tag+'.'+mode;
  const expected=new Set(reads.http.filter(c=>c.status===200&&c.path.includes('/'+id+'/units?')).flatMap(c=>(c.response.items||[]).flatMap(u=>u.marking_codes.map(m=>m.code))));assert.equal(expected.size,250);
  const began=Date.now();await page.goto('http://127.0.0.1:3000/?'+new URLSearchParams({page:'tradecase',tc_wh:String(proof.fixture.warehouse_id),tc_tab:'BUYOUTS',tc_open:id}));
  if(await page.locator('input[type=password]').count()){await page.fill('input[autocomplete=username]','admin');await page.fill('input[type=password]',pass);await page.click('button[type=submit]');}
  const card=page.locator('section.tc-card');await card.locator('.tc-marking-code').first().waitFor({timeout:30000});
  assert((await card.innerText()).includes('подтверждено 250, ожидает 0, отклонено 0'));
  assert((await card.locator('.tc-buyout-units').innerText()).includes('Отгружено'));assert(!(await card.locator('.tc-buyout-units').innerText()).includes('CASELOT:'));
  if(width===390){const box=await card.locator('.tc-buyout-units tbody tr').first().locator('td').nth(1).boundingBox();assert(box.x+box.width<=390,'marking outcome must be visible beside code');} assert(await card.locator('a[href="/help/tradecase-documents.html#buyout"]').count());const help=await page.request.get('http://127.0.0.1:3000/help/tradecase-documents.html');assert(help.ok());assert((await help.text()).includes('полный код для сверки с этикеткой')); const codes=new Set(),counts=[];
  for(let i=0;i<3;i++){
   const entries=card.locator('.tc-marking-code code');await entries.first().waitFor({state:'attached'});
   const values=await entries.allTextContents();assert.equal(values.length,i===2?50:100);counts.push(values.length);values.forEach(c=>codes.add(c));
   if(i===0){await card.locator('.tc-marking-code summary').first().click();assert(await entries.first().isVisible());assert(expected.has(await entries.first().innerText()));assert((await card.locator('.tc-buyout-units').boundingBox()).height<=513);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await card.scrollIntoViewIfNeeded();await page.screenshot({path:out+'/buyout-codes-'+mode+'-'+width+'.png',fullPage:false});}
   if(i<2){const first=values[0];await card.locator('[data-help-id="tradecase.more.units"]').click();await page.waitForFunction(previous=>{const c=document.querySelector('section.tc-card .tc-marking-code code');return c&&c.textContent!==previous;},first);}
  }
  assert.equal(codes.size,250);assert.deepStrictEqual([...codes].sort(),[...expected].sort());
  report.checks.push({width,mode,codes:codes.size,pages:counts,usefulScreenMs:Date.now()-began});await ctx.close();
 }
 assert.equal(report.writes.length,0);assert.equal(report.errors.length,0);report.status='PASS';
})().catch(e=>{report.status='FAIL';report.error=String(e);process.exitCode=1;}).finally(async()=>{fs.writeFileSync(out+'/buyout-codes-ui.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser?.close();});
