// Actual compiled UI + real GET reader. Print-only: all business POSTs are blocked.
const fs=require('fs'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-23/T11/';
const pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const result={status:'RUNNING',checks:[],errors:[],businessPosts:0,injected:['changed version in print refresh']};
const ok=(width,name)=>{result.checks.push({width,name});console.log('PASS',width,name);};
(async()=>{
 const browser=await chromium.launch({headless:true});
 try {
  for(const width of [1440,390]){
   const ctx=await browser.newContext({viewport:{width,height:900}});
   await ctx.addInitScript(()=>{window.print=()=>{document.documentElement.dataset.printed='1';};});
   let changed=false;
   await ctx.route('**/api/**',async route=>{
    const req=route.request();
    if(req.method()==='POST'){result.businessPosts++;return route.abort();}
    if(changed&&/\/case-pick\/tasks\/1019\/paper$/.test(new URL(req.url()).pathname)){
     changed=false;const response=await route.fetch();const data=await response.json();
     data.lines[0].signature='0'.repeat(64);data.lines[0].reference=`CPICK:1019:${data.lines[0].line_id}:`+'0'.repeat(64);
     return route.fulfill({response,json:data});
    }
    return route.continue();
   });
   const page=await ctx.newPage();page.on('pageerror',e=>result.errors.push(String(e)));
   await page.goto('http://127.0.0.1:3000/?page=workspace&workspace=paper&warehouse_id=6667491');
   const login=page.locator('input[type=password]');await login.waitFor();
   await page.locator('input[autocomplete=username]').fill('admin');await login.fill(pass);await page.locator('button[type=submit]').click();
   await page.getByRole('button',{name:'Сборка коробов CASE',exact:true}).click();
   const desk=page.locator('[aria-label="Бумажная сборка CASE"]');
   const row=desk.locator('li').filter({hasText:/CASE 1019\b/});await row.waitFor();
   const open=()=>row.getByRole('button',{name:'Бланк',exact:true}).click();
   await open();await row.locator('.case-paper').waitFor();
   changed=true;const deniedPopup=page.waitForEvent('popup');await row.getByRole('button',{name:'Печать / PDF',exact:true}).click();
   const denied=await deniedPopup;await row.getByRole('alert').filter({hasText:/Задание изменилось/}).waitFor();
   await page.waitForFunction(()=>true);assert(denied.isClosed());ok(width,'print refresh rejects changed task before showing a sheet');
   await row.getByRole('button',{name:'Скрыть',exact:true}).click();await open();await row.locator('.case-paper').waitFor();
   const got=page.waitForEvent('popup');await row.getByRole('button',{name:'Печать / PDF',exact:true}).click();
   const popup=await got;await popup.locator('svg').first().waitFor();await popup.emulateMedia({media:'print'});
   const reference=await popup.locator('code').first().textContent();assert(/^CPICK:1019:/.test(reference));
   await popup.pdf({path:out+`case-paper-landscape-${width}.pdf`,preferCSSPageSize:true});
   await popup.screenshot({path:out+`case-paper-landscape-${width}.png`,fullPage:true});await popup.close();
   ok(width,'real current paper printed using a second native GET');
   const barcode=desk.locator('.case-scan input');await barcode.fill(reference.replace(/:[A-F0-9]{64}$/,':'+ '0'.repeat(64)));
   await barcode.press('Enter');await desk.getByRole('alert').filter({hasText:/устарел/}).waitFor();
   ok(width,'real stale signature409 shown in compiled UI');
   assert((await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth))<=1);
   ok(width,'compiled paper page fits the viewport');await ctx.close();
  }
  assert.equal(result.businessPosts,0);assert.deepStrictEqual(result.errors,[]);result.status='PASS';
 }finally{await browser.close();fs.writeFileSync(out+'case-paper-print-ui.json',JSON.stringify(result,null,2));}
})().catch(e=>{console.error(e);process.exitCode=1;});
