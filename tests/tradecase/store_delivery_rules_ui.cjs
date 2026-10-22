// Actual store reads; PUT success/failure are fixtures and never reach the business API.
const fs=require('fs'),path=require('path'),assert=require('assert');
const ROOT=path.resolve(__dirname,'../..');
const {chromium}=require(path.join(ROOT,'admin/wms_admin_frontend/node_modules/playwright'));
const OUT=path.join(ROOT,'runtime/test-evidence/tradecase/2026-10-23/T09');
const fixture=JSON.parse(fs.readFileSync(path.join(OUT,'store-ui-fixture.json'),'utf8'));
const originalDuration=String(fixture.profile.delivery_rules.unload_norm_min);
const report={status:'FAIL',checks:[],errors:[],writes:[]};
(async()=>{const browser=await chromium.launch({headless:true});
try{for(const width of [1440,390]){
 const context=await browser.newContext({viewport:{width,height:1000}}),p=await context.newPage();let shadow=null,source=null,posts=[],deny=false,loggedIn=false;
 p.on('pageerror',e=>report.errors.push(e.message));
 await p.route('**/api/**',async r=>{const req=r.request(),url=req.url(),m=req.method();
  if(url.includes('/stores/profile')&&m==='GET'){
   if(deny)return r.fulfill({status:403,json:{detail:'Profile read revoked'}});
   if(shadow)return r.fulfill({json:shadow});
   const original=await r.fetch();source=await original.json();return r.fulfill({response:original});
  }
  if(url.endsWith('/stores/profile')&&m==='PUT'){
   posts.push(req.postData());const b=JSON.parse(req.postData());
   if(posts.length===1)return r.fulfill({status:503,json:{detail:{message:'Unknown fixture outcome',outcome_confirmed:false}}});
   shadow={...source,version:b.expected_version+1,configured:true,operation_id:b.operation_id,store_addr:b.store_addr,stock_changed:false,
    profile:{...source.profile,...b},windows:b.windows,delivery_rules:{...source.delivery_rules,
     unload_norm_min:b.unload_norm_min??source.delivery_rules.unload_norm_min,
     window_strict:b.window_strict??false,source_hash:'c'.repeat(64)}};
   if(posts.length===3)deny=true;
   return r.fulfill({json:shadow});
  }
  if(!['GET','OPTIONS'].includes(m)){report.writes.push(m+' '+url);return r.abort();}return r.continue();
 });
 async function open(){await p.goto('http://127.0.0.1:8088/wms-admin/store-directory.html?addr='+encodeURIComponent(fixture.address));
  if(!loggedIn){await p.locator('#loginUser').fill('admin');await p.locator('#loginPassword').fill('admin123');await p.locator('#adminLoginForm button[type=submit]').click();}
  await p.locator('#sdProfile input[name=unload_norm_min]').waitFor({timeout:30000});loggedIn=true;}
 await open();let form=p.locator('#sdProfile');assert(await form.locator('[name=unload_norm_min]').inputValue()===originalDuration);
 await form.locator('[name=window_strict]').selectOption('0');await form.locator('[name=reason]').fill('Synthetic strictness acceptance');await form.locator('#sdSave').click();
 await form.locator('#sdRetry').waitFor();await p.waitForFunction(()=>!document.querySelector('#sdRetry')?.disabled);
 await open();form=p.locator('#sdProfile');assert(await form.locator('[name=unload_norm_min]').inputValue()===originalDuration);
 await form.locator('#sdRetry').click();await form.locator('#sdRetry').waitFor({state:'hidden'});
 assert(posts.length===2&&posts[0]===posts[1]);const first=JSON.parse(posts[0]);
 assert(!('unload_norm_min'in first)&&first.window_strict===false&&first.expected_delivery_rules_hash===source.delivery_rules.source_hash);
 assert(first.receiving_window_mode==='WEEKLY'&&first.timezone_region==='UTC'&&first.windows.length===1);
 report.checks.push({width,case:'Existing duration and weekly windows preserved; only strictness changed; 503/reload exact retry'});
 await form.locator('[name=unload_norm_min]').fill('45');await form.locator('[name=reason]').fill('Synthetic duration acceptance');
 const filledSize=await p.evaluate(()=>({viewport:innerWidth,document:document.documentElement.scrollWidth}));
 assert(filledSize.document<=filledSize.viewport+1,JSON.stringify(filledSize));
 await p.screenshot({path:path.join(OUT,`store-rules-edit-${width}.png`),fullPage:true});
 await form.locator('#sdSave').click();
 await form.getByText('Профиль не прочитан:',{exact:false}).waitFor();assert(posts.length===3);
 const second=JSON.parse(posts[2]);assert(second.unload_norm_min===45&&second.expected_delivery_rules_hash==='c'.repeat(64)&&!('window_strict'in second));
 assert(await form.locator('input,select,textarea').count()===0);
 const size=await p.evaluate(()=>({viewport:innerWidth,document:document.documentElement.scrollWidth}));assert(size.document<=size.viewport+1,JSON.stringify(size));
 await p.screenshot({path:path.join(OUT,`store-rules-${width}.png`),fullPage:true});report.checks.push({width,case:'Duration edit uses fresh basis; failed read clears form without JS error',size});
 await context.close();
}assert(!report.errors.length,report.errors.join(';'));assert(!report.writes.length);report.status='PASS';}
finally{fs.writeFileSync(path.join(OUT,'store-rules-ui.json'),JSON.stringify(report,null,2));await browser.close();}
console.log(JSON.stringify(report));})().catch(e=>{console.error(e);process.exitCode=1;});
