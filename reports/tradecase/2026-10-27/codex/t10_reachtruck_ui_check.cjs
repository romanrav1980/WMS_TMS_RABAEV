// Read-only live UI check for real REACHTRUCK lanes. Own Vite -> API 8093; no POST writes.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../../../..'),out=__dirname;
const {chromium}=require(path.join(root,'admin/wms_admin_frontend/node_modules/playwright'));
const warehouses=[51365792,213059748,220639789,222385707],widths=[390,1440];
const pass=fs.readFileSync(path.join(root,'AGENTS.md'),'utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
(async()=>{const browser=await chromium.launch(),runs=[];try{
 for(const warehouse of warehouses)for(const width of widths){
  const ctx=await browser.newContext({viewport:{width,height:900}}),page=await ctx.newPage(),errors=[],posts=[];
  page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(r.method()==='POST')posts.push(r.url());});
  await page.goto(`http://127.0.0.1:3023/?page=workspace&workspace=shift&warehouse_id=${warehouse}`);
  const pwd=page.locator('input[type=password]');if(await pwd.count()){await page.locator('input[autocomplete=username]').fill('admin');await pwd.fill(pass);await page.locator('button[type=submit]').click();}
  const gantt=page.locator('section.rg');await gantt.waitFor({timeout:40000});
  const kinds=await gantt.locator('[aria-label="Типы ресурсов"] button').allInnerTexts();
  assert.ok(kinds.some(x=>x.includes('Ричтраки')),`reach-truck type missing: ${warehouse}/${width} ${JSON.stringify(kinds)}`);
  const labels=await gantt.locator('button.rg-label').allInnerTexts();
  const groups=await gantt.locator('.rg-group').allInnerTexts();
  assert.ok(groups.some(x=>x.includes('Ричтраки')),`reach-truck lane missing: ${warehouse}/${width} ${JSON.stringify(groups)}`);
  await gantt.locator('[aria-label="Типы ресурсов"] button').filter({hasText:'Ричтраки'}).click();
  assert.ok(!(await gantt.locator('.rg-group').allInnerTexts()).some(x=>x.includes('Ричтраки')),'reach-truck lane did not hide');
  await gantt.locator('[aria-label="Типы ресурсов"] button').filter({hasText:'Ричтраки'}).click();
  assert.ok((await gantt.locator('.rg-group').allInnerTexts()).some(x=>x.includes('Ричтраки')),'reach-truck lane did not restore');
  const audit=await page.evaluate(()=>({viewport:innerWidth,page:document.documentElement.scrollWidth}));assert.equal(audit.page,width);
  assert.deepEqual(posts,[]);assert.deepEqual(errors,[]);
  runs.push({warehouse,width,status:'PASS',type_filters:kinds,reachtruck_lane:true,labels,events:0,assignments:0,posts:0,page_width:audit.page});await ctx.close();
 }
 const report={kind:'LIVE_READ_ONLY_UI',api:'127.0.0.1:8093',runs};fs.writeFileSync(path.join(out,'t10_reachtruck_ui_check.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
 }finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
