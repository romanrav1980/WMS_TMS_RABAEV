// Actual counter, actual commit, lost HTTP reply, current-owner403, same request replay.
const fs=require('fs'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-23/T11';
const s=JSON.parse(fs.readFileSync(out+'/inventory-browser-live.json'));
assert.equal(s.stage,'READY_FOR_REAL_BROWSER');
const admin=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const report={posts:[],replies:[],errors:[],checks:[],status:'FAIL'};
(async()=>{
 const browser=await chromium.launch();
 try{
  const ctx=await browser.newContext({viewport:{width:390,height:900}});
  await ctx.addInitScript(basic=>sessionStorage.setItem('wmsAdminAuth',JSON.stringify({apiBase:'http://127.0.0.1:8088',basic})),'Basic '+Buffer.from(s.actor+':'+s.password).toString('base64'));
  const page=await ctx.newPage();page.on('pageerror',e=>report.errors.push(String(e)));
  await page.route('**/api/inventory/stock-posting/inventory/counts',async route=>{
   const body=route.request().postDataJSON();report.posts.push(body);
   const response=await route.fetch();report.replies.push({status:response.status(),body:await response.json()});
   if(report.posts.length===1){assert.equal(response.status(),200,JSON.stringify(report.replies.at(-1)));return route.abort('connectionreset');}
   return route.fulfill({response});
  });
  const url=`http://127.0.0.1:8088/wms-admin/inventory-count.html?revision_id=${s.revision}&cell=${s.selected_lot.cell}`;
  await page.goto(url);await page.locator('[data-count="0"]').waitFor();
  await page.locator('[data-count="0"]').fill('19');
  await page.locator('[data-units="0"]').fill(s.browser_codes.filter(r=>r[0]!==s.selected_key).map(r=>r[1]).join('\n'));
  await page.locator('#countReason').fill('Physical browser reply recovery');
  await page.locator('#countPost').click();await page.locator('#countRetry').waitFor();
  await page.waitForFunction(()=>document.getElementById('countMessage').textContent.includes('\u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0430'));
  const grant=async(key,version,operate)=>{
   const r=await ctx.request.put('http://127.0.0.1:8088/api/tradecase/warehouses/210564699/stock/owner-grants',{
    headers:{Authorization:'Basic '+Buffer.from('admin:'+admin).toString('base64')},
    data:{operation_id:s.tag+'.'+key,expected_version:version,username:s.actor,owner_id:'SNS',can_view:true,can_operate:operate,reason:'Actual browser current-owner acceptance'}});
   assert.equal(r.status(),200,await r.text());
  };
  await grant('browser.viewonly',1,false);
  await page.reload();await page.locator('#countRetry').waitFor();
  await page.locator('#countRetry').click();
  await page.waitForFunction(()=>document.getElementById('countMessage').textContent.includes('\u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0430'));
  assert.equal(report.replies[1].status,403);assert.deepStrictEqual(report.posts[1],report.posts[0]);
  await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:out+'/inventory-real-pending-390.png',fullPage:true});
  report.checks.push('Actual commit then lost reply; reload and native owner403 preserve original body');
  await grant('browser.restore',2,true);
  await page.locator('#countRetry').click();await page.locator('#countRetry').waitFor({state:'hidden'});
  assert.equal(report.replies[2].status,200);assert.deepStrictEqual(report.posts[2],report.posts[0]);
  assert.deepStrictEqual(report.replies[2].body,report.replies[0].body);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:out+'/inventory-real-confirmed-390.png',fullPage:true});
  assert.deepStrictEqual(report.errors,[]);report.checks.push('Restored authority replays committed result once; mobile width fits');
  report.status='PASS';await ctx.close();
 }finally{fs.writeFileSync(out+'/inventory-browser-ui.json',JSON.stringify(report,null,2));await browser.close();}
 console.log(JSON.stringify({status:report.status,posts:report.posts.length,checks:report.checks.length}));
})().catch(e=>{console.error(e);process.exit(1);});
