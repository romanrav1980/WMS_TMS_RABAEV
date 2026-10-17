// C0125: собранное приложение магазина http://127.0.0.1:3010/store/ — ЖИВОЙ вход admin (существующий процесс входа) и чтение.
// Фиксируем: список доставок или явный отказ прав (не сбой UI), ссылки справки, ошибки JS, переполнение 390. Изменяющих запросов нет.
const fs=require("fs"),path=require("path");const {chromium}=require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const pass=fs.readFileSync("C:/projects/TMS/AGENTS.md","utf8").match(/PASS=(\S+?)[`,)\s]/)[1];const res={writes:[],errors:[],runs:{}};
(async()=>{const b=await chromium.launch();for(const [w,h] of [[1440,900],[390,844]]){const p=await(await b.newContext({viewport:{width:w,height:h}})).newPage();
const api=[];p.on("pageerror",e=>res.errors.push(w+": "+e));p.on("response",r=>{if(r.url().includes(":8088/api/"))api.push(r.request().method()+" "+r.status()+" "+r.url().replace(/^.*\/api\//,"/api/").slice(0,90));});
p.on("request",r=>{if(r.method()!=="GET"&&r.method()!=="OPTIONS"&&r.url().includes(":8088/api/"))res.writes.push(r.method()+" "+r.url());});
await p.goto("http://127.0.0.1:3010/store/");await p.waitForTimeout(1500);const login=await p.locator("input[type=password]").count();
if(login){const u=p.locator("input[autocomplete=username], input[name=username], input[type=text]").first();await u.fill("admin");await p.fill("input[type=password]",pass);await p.locator("button[type=submit]").first().click();await p.waitForTimeout(4000);}
const stores=await p.locator("text=Открыть поставки →").count();let deliveries=null,receipt=null;
if(stores){await p.locator("text=Открыть поставки →").first().click();await p.waitForTimeout(3000);deliveries=(await p.locator("body").innerText()).slice(0,600);
 const open=p.locator("button, a").filter({hasText:/Открыть|Принять|→/}).first();if(await open.count()){await open.click();await p.waitForTimeout(3000);
 receipt={text:(await p.locator("body").innerText()).slice(0,900),scan:await p.locator("input").evaluateAll(n=>n.map(i=>(i.getAttribute("aria-label")||i.placeholder||i.name||i.type)).slice(0,6)),
  helpBtn:await p.locator("[data-help-id], a[href*='help']").evaluateAll(n=>n.map(x=>x.getAttribute("data-help-id")||x.getAttribute("href")).slice(0,8))};}}
const r={stores,deliveries,receipt,loginForm:login,text:(await p.locator("body").innerText()).slice(0,700),help:await p.locator("a[href*='/help/']").evaluateAll(n=>n.map(a=>a.getAttribute("href")).slice(0,5)),overflow:await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth),api:api.slice(-8)};
res.runs[w]=r;await p.screenshot({path:path.join(__dirname,"..","screenshots",`st_live_${w}.png`)});await p.context().close();}
res.status=res.writes.length||res.errors.length?"FAIL":"OBSERVED";fs.writeFileSync(path.join(__dirname,"..","store_live.json"),JSON.stringify(res,null,1));console.log(JSON.stringify(res,null,1));await b.close();})();
