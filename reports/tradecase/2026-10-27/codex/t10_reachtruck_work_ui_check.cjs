// Read-only real shift UI: show and select a previously assigned reach-truck task from the seven-day window.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../../../..'),out=__dirname;
const {chromium}=require(path.join(root,'admin/wms_admin_frontend/node_modules/playwright'));
const pass=fs.readFileSync(path.join(root,'AGENTS.md'),'utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
(async()=>{const browser=await chromium.launch(),runs=[];try{for(const width of [390,1440]){
 const ctx=await browser.newContext({viewport:{width,height:900}}),page=await ctx.newPage(),posts=[],errors=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(r.method()==='POST')posts.push(r.url());});
 await page.goto('http://127.0.0.1:3023/?page=workspace&workspace=shift&warehouse_id=213059748');
 const password=page.locator('input[type=password]');if(await password.count()){await page.locator('input[autocomplete=username]').fill('admin');await password.fill(pass);await page.locator('button[type=submit]').click();}
 const gantt=page.locator('section.rg');await gantt.waitFor({timeout:40000});
 await page.locator('.rg-planner input[type=datetime-local]').fill('2026-10-20T18:00');
 await page.locator('.rg-planner input[type=number]').fill('168');
 await page.waitForFunction(()=>document.querySelector('.rg-summary')?.innerText.includes('работ 4'),null,{timeout:40000});
 const lane=gantt.locator('[role=rowgroup][aria-label^="Ричтраки"]');await lane.waitFor({timeout:10000});
 const bars=lane.locator('button.rg-bar');assert.ok(await bars.count()>0,'reach-truck assigned event has no visible Gantt bar');
 const label=await lane.locator('button.rg-label').first().innerText(),event=await bars.first().innerText();await bars.first().click({force:true});
 const card=page.locator('section.ops-card[aria-label^="Работа "]');await card.waitFor({timeout:10000});
 const cardText=await card.innerText(),audit=await page.evaluate(()=>({viewport:innerWidth,page:document.documentElement.scrollWidth}));
 assert.ok(cardText.includes(event.trim()),'selected event not shown in the detail card');assert.equal(audit.page,width);assert.deepEqual(posts,[]);assert.deepEqual(errors,[]);
 const row={warehouse:213059748,width,status:'PASS',reachtruck_lane:label,visible_bars:await bars.count(),selected_event:event,detail_card:true,page_width:audit.page,posts:0};runs.push(row);
 await page.screenshot({path:path.join(out,`t10-reachtruck-work-${width}.png`),fullPage:true});await ctx.close();
}fs.writeFileSync(path.join(out,'t10_reachtruck_work_ui_check.json'),JSON.stringify({kind:'LIVE_READ_ONLY_SHIFT_UI_7D',window:['2026-10-20T18:00:00Z','2026-10-27T18:00:00Z'],runs},null,2));console.log(JSON.stringify(runs));}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
