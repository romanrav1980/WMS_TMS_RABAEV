// Actual API/Oracle empty-HU completion. Abort only the response AFTER the server commits.
const fs = require('fs'), assert = require('assert');
const {chromium} = require('../../admin/wms_admin_frontend/node_modules/playwright');
const out = 'runtime/test-evidence/tradecase/2026-10-23/T11/';
const state = JSON.parse(fs.readFileSync(out+'paper-fact-ui-state.json', 'utf8'));
const pass = fs.readFileSync('AGENTS.md', 'utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const auth = 'Basic '+Buffer.from('admin:'+pass).toString('base64');
const result = {checks: [], posts: [], errors: [], timings: {}, synthetic: ['403 paper read', 'lost response after real commit']};
const ok = name => {result.checks.push(name); console.log('PASS', name);};
const endpoint = `/api/warehouse-tasks/${state.task}/complete`;
(async () => {
  const browser = await chromium.launch({headless:true});
  try {
    const ctx = await browser.newContext({viewport:{width:390,height:844}});
    await ctx.addInitScript(({auth}) => {
      sessionStorage.setItem('wmsAdminAuth', JSON.stringify({apiBase:'http://127.0.0.1:8088',basic:auth}));
    }, {auth});
    const page = await ctx.newPage(); page.on('pageerror', e => result.errors.push(String(e)));
    let lose = true, deny = false;
    await ctx.route('**/api/**', async route => {
      const req=route.request(), url=new URL(req.url());
      if (deny && url.pathname.endsWith('/paper')) return route.fulfill({status:403,json:{detail:'QA_INJECTED_REVOKE'}});
      if (req.method()==='POST') {
        assert.equal(url.pathname, endpoint, 'No other business mutation allowed');
        result.posts.push(req.postData());
        const response = await route.fetch();
        const value = await response.json();
        assert.equal(response.status(),200,JSON.stringify(value));
        if (lose) {lose=false;result.receipt=value;return route.abort('failed');}
        assert.deepStrictEqual(value,result.receipt); return route.fulfill({response});
      }
      return route.continue();
    });
    const url='http://127.0.0.1:8088/wms-admin/warehouse-tasks.html?task_id='+state.task+'&paper_reference='+encodeURIComponent(state.paper.reference);
    await page.goto(url); await page.waitForFunction(id => warehouseTaskState.selectedTask?.task_id===id,state.task);
    const panel=page.locator('.warehouse-task-paper'), input=panel.locator('input');
    const complete=page.locator('#warehouseTaskComplete');
    assert(await complete.isDisabled()); assert(await page.locator('#warehouseTaskStart').isDisabled());
    ok('390: paper prevents confirmation before version check and separate START');
    await input.fill(`WTASK:${state.task}:`+'0'.repeat(64)); await input.press('Enter');
    await panel.locator('[role=status]').filter({hasText:/устарел/}).waitFor();
    assert(await complete.isDisabled()); ok('Real stale paper409 disables new confirmation');
    await input.fill(state.paper.reference); deny=true; await input.press('Enter');
    await panel.locator('[role=status]').filter({hasText:/недоступно/}).waitFor();
    assert(await complete.isDisabled()); deny=false;ok('Injected403 clears version admission');
    await input.press('Enter'); await panel.locator('[role=status]').filter({hasText:/Бланк проверен/}).waitFor();
    assert(!(await complete.isDisabled()));ok('Real current paper permits existing fact form');
    await page.locator('#warehouseTaskScanPallet').fill(state.hu);
    await page.locator('#warehouseTaskScanFrom').fill(state.source);
    await page.locator('#warehouseTaskScanTo').fill(state.target);
    // A whole HU is one indivisible place; the existing form fixes its quantity.
    const qty=page.locator('#warehouseTaskFactQty');
    if (await qty.isDisabled()) assert.equal(await qty.inputValue(),'1');
    else await qty.fill('1');
    const t0=Date.now(); await complete.click();
    await page.locator('#warehouseTaskRecovery').waitFor({state:'visible'});
    await page.waitForFunction(() => document.querySelector('#warehouseTaskRecovery button')?.disabled===false);
    result.timings.completeWithResponseLoss=Date.now()-t0;
    assert.equal(result.posts.length,1);const payload=JSON.parse(result.posts[0]);
    assert.equal(payload.expected_task_signature,state.paper.task.task_signature);
    assert.equal(payload.scanned_pallet,state.hu);ok('Real completion committed with printed signature; lost response retained');
    await page.reload();await page.waitForFunction(id=>warehouseTaskState.selectedTask?.task_id===id,state.task);
    await page.locator('#warehouseTaskRecovery button').click();
    await page.locator('#warehouseTaskRecovery').waitFor({state:'hidden'});
    assert.equal(result.posts.length,2); assert.equal(result.posts[0],result.posts[1]);
    assert.equal(await page.evaluate(()=>Object.keys(localStorage).filter(k=>k.startsWith('wms.task.complete.v1:')).length),0);
    ok('Reload and exact retry returned original receipt without another command body');
    for (const width of [390,1440]) {
      await page.setViewportSize({width,height:900});
      await panel.scrollIntoViewIfNeeded();
      const bounds=await panel.boundingBox();assert(bounds.x>=0&&bounds.x+bounds.width<=width+1);
      const size=await panel.locator('button').boundingBox();assert(size.height>=44);
      result.timings['overflow'+width]=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
      await page.screenshot({path:out+`paper-fact-${width}.png`,fullPage:true});
      ok(`${width}: panel fits viewport and check target >=44px`);
    }
    const help = await ctx.request.get('http://127.0.0.1:8088/help/warehouse-task-paper.html');assert.equal(help.status(),200);
    ok('Raw screen help URL serves actual instructions');assert.deepStrictEqual(result.errors,[]);
    result.status='PASS';await ctx.close();
  } finally {
    await browser.close();fs.writeFileSync(out+'paper-fact-ui.json',JSON.stringify(result,null,2));
  }
})().catch(e=>{console.error(e);process.exitCode=1;});
