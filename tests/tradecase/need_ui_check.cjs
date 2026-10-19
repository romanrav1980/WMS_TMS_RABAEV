const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const fixture=JSON.parse(fs.readFileSync('runtime/test-evidence/tradecase/2026-10-19/T09/need-fixture.json','utf8'));
const pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const out='runtime/test-evidence/tradecase/2026-10-19/T09';const r={checks:[],http:[],errors:[],businessWrites:[]};
(async()=>{const browser=await chromium.launch();
for(const width of[1440,390]){
 const page=await(await browser.newContext({viewport:{width,height:width===390?844:1000}})).newPage();page.on('pageerror',e=>r.errors.push(String(e)));
 page.on('response',res=>{if(res.url().includes('/api/tradecase/'))r.http.push({status:res.status(),url:res.url(),ms:res.request().timing().responseEnd});});
 await page.route('**/api/**',async route=>{const req=route.request();if(!['GET','OPTIONS'].includes(req.method())&&!req.url().includes('/auth/')){r.businessWrites.push(req.method()+' '+req.url());return route.abort();}return route.continue();});
 const url=id=>'http://127.0.0.1:3000/?page=tradecase&tc_wh='+fixture.warehouse_id+'&tc_tab=NEED&tc_open='+id;
 await page.goto(url(fixture.a_id));if(await page.locator('input[type=password]').count()){await page.fill('input[autocomplete=username]','admin');await page.fill('input[type=password]',pass);await page.click('button[type=submit]');}
 const panel=page.locator('section[aria-label="Расчёт потребности получателя"]');await panel.waitFor({timeout:30000});
 const calc=panel.locator('[data-help-id="tradecase.need.calculate"]');assert(await calc.isDisabled());await panel.locator('input').fill('60');await calc.click();await panel.locator('dl').waitFor({timeout:30000});assert((await panel.innerText()).includes('40 кор.'));
 assert((await panel.locator('a[href$="#need"]').getAttribute('href')).includes('tradecase-documents.html'));
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'page overflow '+width);
 await page.screenshot({path:out+'/need-'+width+'.png',fullPage:true});r.checks.push(width+':live40/explanation/help/noOverflow');
 await panel.locator('input').fill('61');assert(await panel.locator('dl').count()===0,'changed threshold retained result');
 await page.route('**/needs/**',route=>route.fulfill({status:403,contentType:'application/json',body:JSON.stringify({detail:{code:'TRADECASE_ACCESS_DENIED'}}),headers:{'access-control-allow-origin':'*'}}));await calc.click();await panel.locator('[role=alert]').waitFor();assert(await panel.locator('dl').count()===0);r.checks.push(width+':403/clearedResult');await page.unroute('**/needs/**');
 await page.goto(url(fixture.tag+'.STALE'));if(await page.locator('input[type=password]').count()){await page.fill('input[autocomplete=username]','admin');await page.fill('input[type=password]',pass);await page.click('button[type=submit]');}await panel.waitFor();await panel.locator('input').fill('60');await calc.click();await panel.getByRole('alert').filter({hasText:'Снимок устарел'}).waitFor();await page.screenshot({path:out+'/need-stale-'+width+'.png',fullPage:true});r.checks.push(width+':staleWarning');await page.close();
}
assert.deepEqual(r.errors,[]);assert.deepEqual(r.businessWrites,[]);r.status='PASS';fs.writeFileSync(out+'/ui-result.json',JSON.stringify(r,null,2));console.log(JSON.stringify({status:r.status,checks:r.checks,http:r.http.length,businessWrites:r.businessWrites.length}));await browser.close();
})().catch(e=>{r.status='FAIL';r.error=String(e);fs.writeFileSync(out+'/ui-result.json',JSON.stringify(r,null,2));console.error(e);process.exit(1);});
