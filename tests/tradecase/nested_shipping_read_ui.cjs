const fs=require('fs'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-23/T06/nested-shipping';
const native=JSON.parse(fs.readFileSync(out+'/hu-ui-tree.json','utf8')).snapshot;
const password=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const report={status:'FAIL',checks:[],writes:[],errors:[],http:[]};let browser;
(async()=>{
 browser=await chromium.launch();
 for(const width of [1440,390])for(const host of ['react','raw']){
  const ctx=await browser.newContext({viewport:{width,height:width===390?844:1000}}),page=await ctx.newPage();
  page.on('pageerror',e=>report.errors.push(String(e)));
  await page.route('**/api/**',route=>{
   const r=route.request(),path=new URL(r.url()).pathname;
   if(!['GET','OPTIONS'].includes(r.method())&&!path.includes('/auth/')){report.writes.push(path);return route.abort();}
   return route.continue();
  });
  page.on('response',r=>{if(r.url().includes('/api/warehouse-hus/composition'))report.http.push({width,host,status:r.status(),timing:r.request().timing()});});
  const started=Date.now();
  await page.goto(host==='react'?'http://127.0.0.1:3000/?page=workspace&workspace=consolidation&warehouse_id=222385707':'http://127.0.0.1:8088/wms-admin/warehouse-hus.html');
  if(host==='react'){
   await page.getByLabel('Пользователь',{exact:true}).fill('admin');await page.getByLabel('Пароль',{exact:true}).fill(password);await page.getByRole('button',{name:'Войти',exact:true}).click();
   await page.getByLabel('Идентификатор паллеты / места',{exact:true}).fill(native.root);await page.getByRole('button',{name:'Показать состав',exact:true}).click();
   await page.locator('.hu-tree-select').last().waitFor();assert.equal(await page.locator('.hu-tree-select').count(),3);
   await page.locator('.hu-tree-select').last().click();assert.ok((await page.locator('.hu-tree-inspector').innerText()).includes('10 EA'));
   const plans=page.locator('details.cp-plan-section');assert.equal(await plans.getAttribute('open'),null);
   await page.getByRole('button',{name:'Новый план',exact:true}).click();
   await page.locator('.cp-editor').waitFor();assert.notEqual(await plans.getAttribute('open'),null);
   await page.locator('.cp-editor').getByRole('button',{name:'Закрыть',exact:true}).click();
   await plans.locator('summary').click();assert.equal(await plans.getAttribute('open'),null);
   assert.equal(await page.locator('.hu-tree-select').count(),3);
   report.checks.push({width,host,test:'Plan section compact by default; New plan opens editor; closing preserves read tree; no writes'});

  }else{
   if(await page.locator('#loginUser').count()){await page.fill('#loginUser','admin');await page.fill('#loginPassword',password);await page.click('#adminLoginForm button[type=submit]');}
   await page.waitForFunction(()=>window.wmsAdminAuth?.state.user?.username==='admin');
   await page.fill('#huIdentifier',native.root);await page.click('#huLoad');await page.waitForFunction(()=>document.querySelectorAll('#huRows tr').length===3);
   assert.ok((await page.locator('#huSummary').innerText()).includes('10'));
  }
  const loadMs=Date.now()-started;
  const geometry=await page.evaluate(()=>({viewport:innerWidth,page:document.documentElement.scrollWidth}));assert.ok(geometry.page<=width+1,JSON.stringify({width,host,...geometry}));
  await page.screenshot({path:`${out}/hu-${host}-${width}.png`,fullPage:true});
  report.checks.push({width,host,test:'Actual departed3-node tree;10 physical units counted once; bounded layout',load_including_login_ms:loadMs,geometry});
  await page.route('**/api/warehouse-hus/composition?**',route=>route.fulfill({status:403,json:{detail:'HU_CURRENT_STOCK_OWNER_VIEW_REQUIRED'}}));
  if(host==='react'){
   await page.getByRole('button',{name:'Показать состав',exact:true}).click();await page.getByText('Нет доступа к складу или собственнику товара в составе грузового места.',{exact:true}).waitFor();assert.equal(await page.locator('.hu-tree-select').count(),0);
  }else{
   await page.click('#huLoad');await page.locator('#huStatus').filter({hasText:'Нет доступа к складу или собственнику товара'}).waitFor();assert.equal(await page.locator('#huRows tr').count(),0);
  }
  report.checks.push({width,host,test:'fixture403 clears the previously loaded tree'});await ctx.close();
 }
 assert.deepEqual(report.errors,[]);assert.deepEqual(report.writes,[]);report.status='PASS';console.log(JSON.stringify(report.checks));
})().catch(e=>{report.error=String(e);console.error(e);process.exitCode=1;}).finally(async()=>{fs.writeFileSync(out+'/hu-tree-ui.json',JSON.stringify(report,null,2));if(browser)await browser.close();});
