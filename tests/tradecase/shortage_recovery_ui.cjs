// Read the actual recovered CASE through the served UI; no warehouse writes.
const fs=require('fs'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-26/T11';
const s=JSON.parse(fs.readFileSync(out+'/trade-pick-shortage-state.json','utf8'));
assert(['RECOVERED','CLEANED'].includes(s.phase));
const stage=s.phase==='CLEANED'?'closed':'recovered';
const pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const report={status:'FAIL',checks:[],writes:[],errors:[]};
(async()=>{const browser=await chromium.launch();try{
 for(const width of [1440,390]){
  const context=await browser.newContext({viewport:{width,height:950}});
  await context.addInitScript(basic=>sessionStorage.setItem('wmsAdminAuth',JSON.stringify({apiBase:'http://127.0.0.1:8088',basic})),'Basic '+Buffer.from('admin:'+pass).toString('base64'));
  const page=await context.newPage();page.on('pageerror',e=>report.errors.push(String(e)));
  await page.route('**/api/**',route=>{const method=route.request().method();if(!['GET','OPTIONS'].includes(method)){report.writes.push(method+' '+route.request().url());return route.abort()}return route.continue()});
  await page.goto(`http://127.0.0.1:8088/wms-admin/case-pick-management.html?warehouse_id=${s.fixture.warehouse_id}&task_id=${s.case}`);
  await page.waitForFunction(({id,closed})=>typeof caseState!=='undefined'&&(caseState.tasks.some(t=>t.case_pick_task_id===id)||(closed&&caseState.tasks.length===0)),{id:s.case,closed:stage==='closed'},{timeout:30000});
  const detail=await page.locator('#caseDetail').innerText();
  const fits=await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1);
  report.checks.push({width,detail,pageFits:fits});
  await page.screenshot({path:out+`/shortage-${stage}-${width}.png`,fullPage:false});
  assert(fits,`Horizontal overflow at${width}`);if(stage==='recovered')assert(/8\s*\/\s*8/.test(detail),detail);
  assert.equal(await page.locator('#caseDetail .case-alert').count(),0);
  for(const id of ['caseApproveShort','caseAcceptShort','caseAcceptWeight','caseRejectShort']){const button=page.locator('#'+id);if(await button.count())assert(await button.isDisabled(),id);}
  assert(!(await page.locator('body').innerText()).includes('19.05.2026'));
  await context.close();
 }
 assert.deepStrictEqual(report.errors,[]);assert.deepStrictEqual(report.writes,[]);report.status='PASS';
}finally{fs.writeFileSync(out+'/shortage-ui-'+stage+'.json',JSON.stringify(report,null,2));await browser.close()}
console.log(report.status)})().catch(e=>{console.error(e);process.exit(1)});
