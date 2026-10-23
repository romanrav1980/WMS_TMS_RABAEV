// Read-only regression after compact direct-task navigation. No new stock effect.
const fs=require('fs'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const dir='runtime/test-evidence/tradecase/2026-10-23/T11/';
const state=JSON.parse(fs.readFileSync(dir+'paper-fact-ui-state.json','utf8'));
const pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const output={checks:[],errors:[],queueReads:0,posts:0};
(async()=>{
 const browser=await chromium.launch({headless:true});
 try {
  for(const width of [390,1440]){
   const context=await browser.newContext({viewport:{width,height:900}});
   await context.addInitScript(auth=>sessionStorage.setItem('wmsAdminAuth',JSON.stringify({apiBase:'http://127.0.0.1:8088',basic:auth})),
    'Basic '+Buffer.from('admin:'+pass).toString('base64'));
   const page=await context.newPage();page.on('pageerror',e=>output.errors.push(String(e)));
   await context.route('**/api/**',route=>{
    const req=route.request();if(req.method()==='POST'){output.posts++;return route.abort();}
    if(/\/api\/warehouse-tasks\?/.test(req.url()))output.queueReads++;
    return route.continue();
   });
   // Current read allows verification of the completed task; old paper is intentionally not reused.
   const paper=await context.request.get('http://127.0.0.1:8088/api/warehouse-tasks/'+state.task+'/paper',
    {headers:{Authorization:'Basic '+Buffer.from('admin:'+pass).toString('base64')}});
   assert.equal(paper.status(),200);const current=await paper.json();
   await page.goto('http://127.0.0.1:8088/wms-admin/warehouse-tasks.html?task_id='+state.task+'&paper_reference='+encodeURIComponent(current.reference));
   await page.waitForFunction(id=>warehouseTaskState.selectedTask?.task_id===id,state.task);
   assert(await page.locator('.warehouse-task-list-panel').isHidden());
   const panel=page.locator('.warehouse-task-paper');await panel.locator('input').press('Enter');
   await panel.locator('[role=status]').filter({hasText:/Бланк проверен/}).waitFor();
   assert(await page.locator('#warehouseTaskComplete').isDisabled(),'DONE must never permit another fact');
   await panel.locator('input').fill('CPICK:1235:1:'+'A'.repeat(64));await panel.locator('input').press('Enter');
   await panel.locator('[role=status]').filter({hasText:/полный штрихкод/}).waitFor();
   assert(await page.locator('#warehouseTaskComplete').isDisabled());
   const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);assert(overflow<=1);
   await page.screenshot({path:dir+`paper-fact-compact-${width}.png`,fullPage:true});
   await panel.screenshot({path:dir+`paper-fact-panel-${width}.png`});
   output.checks.push({width,compact:true,completedBlocked:true,wrongNamespaceBlocked:true,overflow});
   await context.close();
  }
  assert.equal(output.queueReads,0);assert.equal(output.posts,0);assert.deepStrictEqual(output.errors,[]);
  output.status='PASS';console.log(JSON.stringify(output));
 }finally{await browser.close();fs.writeFileSync(dir+'paper-fact-read-ui.json',JSON.stringify(output,null,2));}
})().catch(e=>{console.error(e);process.exitCode=1;});
