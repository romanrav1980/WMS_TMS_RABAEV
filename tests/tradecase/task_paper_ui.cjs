// Real read-only API/browser; UI 403/network failure are injected. window.print is observed, not a physical printer.
const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const ROOT=path.resolve(__dirname,'../..'),OUT=path.join(ROOT,'runtime/test-evidence/tradecase/2026-10-23/T11');
const PDF=path.join(ROOT,'output/pdf');fs.mkdirSync(PDF,{recursive:true});
const password=fs.readFileSync(path.join(ROOT,'AGENTS.md'),'utf8').match(/PASS=(\S+?)[`,)\s]/)[1];
const auth='Basic '+Buffer.from('admin:'+password).toString('base64');
const report={status:'FAIL',basis:'Actual native timeline/task reads; actual stale409; injected network failure/UI403; browser print stubbed; no physical printer/scanner',widths:[],errors:[],posts:[]};
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{for(const width of [1440,390]){
  const context=await browser.newContext({viewport:{width,height:width===390?844:1000}});
  await context.addInitScript(()=>{window.__paperPrintCalls=0;window.print=()=>{window.__paperPrintCalls++;};});
  const p=await context.newPage();let deny=false,offline=false;
  p.on('pageerror',e=>report.errors.push(String(e)));
  p.on('request',r=>{if(r.method()==='POST')report.posts.push(new URL(r.url()).pathname);});
  await p.route('**/api/warehouse-tasks/1233/paper*',async route=>offline?route.abort('failed'):deny?route.fulfill({status:403,json:{detail:{code:'TEST_UI_DENIED'}},headers:{'access-control-allow-origin':'*'}}):route.continue());
  try{
   const native=await context.request.get('http://127.0.0.1:8088/api/warehouse-tasks/1233/paper',{headers:{Authorization:auth}});assert.equal(native.status(),200);const snapshot=await native.json();
   await p.goto('http://127.0.0.1:3000/?page=workspace&workspace=shift&warehouse_id=212476763');
   await p.locator('input[type=password]').waitFor({timeout:30000});
   await p.locator('input[autocomplete=username]').fill('admin');await p.locator('input[type=password]').fill(password);await p.locator('button[type=submit]').click();
   await p.locator('input[type=date]').waitFor();await p.locator('input[type=date]').fill('2026-10-23');
   const task=p.locator('.rg-queue button').filter({hasText:/1233/});await task.waitFor({timeout:30000});await task.click();
   await p.getByRole('button',{name:'Бланк задания',exact:true}).click();
   const panel=p.locator('section[aria-label="Бумажное задание"]');await panel.getByRole('button',{name:'Печать / PDF',exact:true}).waitFor();
   const started=Date.now();await panel.getByLabel('Штрихкод с бланка',{exact:true}).fill(width===390?snapshot.reference.toLowerCase():snapshot.reference);
   if(width===390)await panel.getByLabel('Штрихкод с бланка',{exact:true}).press('Enter');else await panel.getByRole('button',{name:'Проверить бланк',exact:true}).click();
   await panel.getByRole('button',{name:'Печать / PDF',exact:true}).waitFor();const readMs=Date.now()-started;
   await panel.getByRole('status').filter({hasText:'Версия бланка совпадает'}).waitFor();
   const popupEvent=p.waitForEvent('popup');await panel.getByRole('button',{name:'Печать / PDF',exact:true}).click();const popup=await popupEvent;
   await popup.locator('img').waitFor();await popup.waitForFunction(()=>window.__paperPrintCalls===1,{timeout:10000});
   assert((await popup.locator('body').innerText()).includes('Выполнено - копия'));
   assert((await popup.locator('body').innerText()).includes('PH23.68eb5dba.HU'));
   assert(!await popup.locator('body').innerText().then(x=>x.includes(snapshot.task.task_signature)));
   const pdf=path.join(PDF,`task-paper-1233-${width}.pdf`);await popup.pdf({path:pdf,format:'A4',landscape:true,preferCSSPageSize:true,printBackground:true});
   await popup.screenshot({path:path.join(OUT,`paper-print-${width}.png`),fullPage:true});await popup.close();
   await panel.scrollIntoViewIfNeeded();
   const overflow=await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);assert.equal(overflow,false);
   const input=await panel.locator('input').evaluate(e=>({background:getComputedStyle(e).backgroundColor,height:e.getBoundingClientRect().height}));assert(input.height>=44);
   const buttons=await panel.locator('button').evaluateAll(es=>es.map(e=>({title:e.title,height:e.getBoundingClientRect().height})));assert(buttons.every(x=>x.title&&x.height>=44),JSON.stringify(buttons));
   await panel.screenshot({path:path.join(OUT,`paper-panel-${width}.png`)});
   await panel.getByLabel('Штрихкод с бланка',{exact:true}).fill('WTASK:1233:'+'0'.repeat(64));await panel.getByRole('button',{name:'Проверить бланк',exact:true}).click();
   await panel.getByRole('alert').filter({hasText:'Этот бланк устарел'}).waitFor();assert.equal(await panel.getByRole('button',{name:'Печать / PDF',exact:true}).count(),0);
   await panel.getByRole('button',{name:'Новый бланк',exact:true}).click();await panel.getByRole('button',{name:'Печать / PDF',exact:true}).waitFor();
   offline=true;await panel.getByRole('button',{name:'Новый бланк',exact:true}).click();await panel.getByRole('alert').filter({hasText:'Связь с сервером прервана'}).waitFor();assert.equal(await panel.locator('.task-paper-fields').count(),0);
   offline=false;deny=true;await panel.getByRole('button',{name:'Новый бланк',exact:true}).click();await panel.getByRole('alert').filter({hasText:'Задание недоступно'}).waitFor();
   assert.equal(await panel.locator('.task-paper-fields').count(),0);assert.equal(await panel.getByRole('button',{name:'Печать / PDF',exact:true}).count(),0);
   const article=await context.request.get('http://127.0.0.1:3000/help/warehouse-task-paper.html');assert.equal(article.status(),200);
   report.widths.push({width,readMs,overflow,input,pdf,checks:['actual task snapshot/barcode check','keyboard Enter/lowercase hex accepted at390','print version reread and PDF','native stale409 clears snapshot','injected network/403 clears snapshot','44px/help/local article']});
  }finally{await context.close();}
 }
 assert.equal(report.errors.length,0);assert(report.posts.every(p=>!p.includes('/complete')&&!p.includes('/warehouse-hus/')));report.status='PASS';
 }finally{fs.writeFileSync(path.join(OUT,'paper-ui.json'),JSON.stringify(report,null,2));await browser.close();console.log(JSON.stringify(report));}
})().catch(e=>{console.error(e);process.exitCode=1;});
