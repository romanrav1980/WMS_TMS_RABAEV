// Real owned A->B PATCH committed; abort its reply; retain intent across reload and read back.
const fs=require('fs'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-23/T07/vehicle-change';
const s=JSON.parse(fs.readFileSync(out+'/vehicle-change.json','utf8'));
const trip=s.transport.transport_task_id, pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const report={status:'FAIL',posts:[],checks:[],errors:[],readback403:'UI fault injection only; current native authority unchanged'};
const prior=out+'/vehicle-live-ui.json';
if(fs.existsSync(prior)&&JSON.parse(fs.readFileSync(prior)).posts?.length)throw Error('Prior physical edit exists; do not send another edit. Use readback recovery only.');
let deny=false;
(async()=>{
 const browser=await chromium.launch();
 try{
  const ctx=await browser.newContext({viewport:{width:390,height:900}}),p=await ctx.newPage();
  p.on('pageerror',e=>report.errors.push(String(e)));
  const endpoint=`/api/admin/transport/tasks/${trip}`;
  await p.route(u=>u.href.endsWith(endpoint),async r=>{
   const req=r.request();
   if(req.method()==='GET'&&deny)return r.fulfill({status:403,json:{detail:'UI injected read denial after committed PATCH'},headers:{'access-control-allow-origin':'*'}});
   if(req.method()!=='PATCH')return r.continue();
   assert.equal(report.posts.length,0,'Do not issue another physical edit');
   const body=req.postDataJSON();assert.equal(body.transport,s.vehicles.B.number);
   deny=true;const reply=await r.fetch();report.posts.push({body,status:reply.status(),response:await reply.json()});
   assert.equal(reply.status(),200,JSON.stringify(report.posts));return r.abort('connectionreset');
  });
  async function open(){
   await p.goto(`http://127.0.0.1:3000/?page=transport&task_id=${trip}`);
   await p.waitForTimeout(700);
   if(await p.locator('input[type=password]').count()){
    await p.locator('input[autocomplete=username]').fill('admin');await p.locator('input[type=password]').fill(pass);await p.locator('button[type=submit]').click();
   }
   await p.getByText('\u0420\u0435\u0439\u0441 #'+trip,{exact:true}).first().waitFor({timeout:60000});await p.locator('button.dispatch-tab').filter({hasText:'\u0417\u0430\u044f\u0432\u043a\u0438'}).click();
   await p.locator('input[type=date]').nth(1).fill(s.transport.shipment_date);
   await p.locator('tr',{hasText:'#'+trip}).first().click({timeout:30000});
   await p.locator('button.dispatch-edit-btn').waitFor({timeout:15000}).catch(async e=>{await p.screenshot({path:out+'/vehicle-open-failed.png',fullPage:true});fs.writeFileSync(out+'/vehicle-open-body.txt',await p.locator('body').innerText());throw e;});
  }
  await open();await p.locator('button.dispatch-edit-btn').click();
  await p.locator('select.dispatch-trip-ms').first().selectOption(s.vehicles.B.number);
  await p.locator('button.dispatch-save-btn').click();
  await p.waitForFunction(()=>document.querySelector('.dispatch-vehicle-pending'));
  await p.waitForTimeout(600);
  assert.equal(report.posts.length,1);
  await p.screenshot({path:out+'/vehicle-real-unknown-390.png',fullPage:true});
  const keys=await p.evaluate(()=>Object.keys(localStorage).filter(k=>k.startsWith('retailcase.trip.edit.pending:')));
  assert.equal(keys.length,1);report.pending=await p.evaluate(k=>JSON.parse(localStorage.getItem(k)),keys[0]);
  await p.reload();await p.getByText('Заявки',{exact:true}).first().waitFor({timeout:60000});
  await p.getByText('Заявки',{exact:true}).first().click();await p.locator('input[type=date]').nth(1).fill(s.transport.shipment_date);
  // Keep the readback denied on opening the owned card; the list itself is real.
  await p.locator('tr',{hasText:'#'+trip}).first().click();
  await p.locator('.dispatch-vehicle-pending').waitFor({timeout:30000});
  assert(await p.evaluate(k=>!!localStorage.getItem(k),keys[0]));report.checks.push('Real PATCH committed once; lost reply, reload and injected GET403 preserve original intent');
  deny=false;await p.getByRole('button',{name:'Проверить снова',exact:true}).click();
  await p.waitForFunction(k=>localStorage.getItem(k)===null,keys[0]);
  assert.equal(report.posts.length,1);assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await p.screenshot({path:out+'/vehicle-real-readback-390.png',fullPage:true});
  report.checks.push('Real readback finds vehicle B, clears intent without another PATCH;390px fits');
  assert.deepStrictEqual(report.errors,[]);report.status='PASS';await ctx.close();
 }finally{fs.writeFileSync(out+'/vehicle-live-ui.json',JSON.stringify(report,null,2));await browser.close();}
 console.log(JSON.stringify({status:report.status,checks:report.checks.length,posts:report.posts.length}));
})().catch(e=>{console.error(e);process.exit(1)});
