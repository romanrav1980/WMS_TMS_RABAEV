// C0122: ограниченный сквозной смоук (живой, только чтение): KPI и консолидация из рабочего места (desktop + 390),
// приложение магазина на 390 (экран входа), переход старший смены → магазин/справка. Изменяющих запросов нет.
const fs=require("fs"),path=require("path"),assert=require("assert");const {chromium}=require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT=path.join(__dirname,"..","screenshots");const pass=fs.readFileSync("C:/projects/TMS/AGENTS.md","utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE="http://127.0.0.1:3000/src/features/platform/workspaces/preview/index.html";const res={errors:[],writes:[],checks:[]};
const watch=p=>{p.on("pageerror",e=>res.errors.push(p.url().slice(0,60)+": "+e));p.on("request",r=>{if(r.method()!=="GET"&&r.url().includes("/api/")&&!r.url().endsWith("/shift-overview"))res.writes.push(r.method()+" "+r.url());});};
(async()=>{const b=await chromium.launch();
for(const [w,h] of [[1440,1000],[390,844]]){const p=await(await b.newContext({viewport:{width:w,height:h}})).newPage();watch(p);
 await p.goto(BASE+"?workspace=shift&warehouse_id=20902283");await p.fill("input[autocomplete=username]","admin");await p.fill("input[type=password]",pass);await p.click("button[type=submit]");
 await p.waitForSelector(".ops-kpi",{timeout:30000});
 const store=await p.locator("[data-help-id='shift.open.store']").getAttribute("title");const help=await p.locator("[data-help-id='shift.navigation.help']").getAttribute("href");
 const pick=async id=>{const tab=p.locator(`[data-help-id$='.${id}'][role=tab]`);if(await tab.isVisible())await tab.click();else await p.selectOption("select[data-help-id='workspace.role.select']",id);};await pick("kpi");await p.waitForTimeout(4000);
 const kpi=await p.evaluate(()=>({text:(document.querySelector("main")?.innerText||"").slice(0,300),wh:[...document.querySelectorAll("input[list]")].map(i=>i.value),overflow:document.documentElement.scrollWidth-innerWidth,helpLinks:[...document.querySelectorAll("a[href*='/help/']")].map(a=>a.getAttribute("href")).slice(0,3)}));
 await p.screenshot({path:path.join(OUT,`e1_kpi_${w}.png`)});
 await pick("consolidation");await p.waitForTimeout(2500);
 const cons=await p.evaluate(()=>({wh:[...document.querySelectorAll("input[list]")].map(i=>i.value),overflow:document.documentElement.scrollWidth-innerWidth}));
 res["w"+w]={store,help,kpi,cons};assert(kpi.overflow<=0&&cons.overflow<=0);await p.context().close();}
const s=await(await b.newContext({viewport:{width:390,height:844}})).newPage();watch(s);await s.goto("http://127.0.0.1:8088/store/");await s.waitForTimeout(2500);
res.store390={overflow:await s.evaluate(()=>document.documentElement.scrollWidth-innerWidth),title:await s.title()};assert(res.store390.overflow<=0);await s.screenshot({path:path.join(OUT,"e2_store_390.png")});
assert.deepEqual(res.writes,[]);assert.deepEqual(res.errors,[]);res.status="PASS";
fs.writeFileSync(path.join(__dirname,"..","e2e_smoke.json"),JSON.stringify(res,null,1));console.log(JSON.stringify(res,null,1));await b.close();})().catch(e=>{console.error(e);console.error(JSON.stringify(res));process.exit(1);});
