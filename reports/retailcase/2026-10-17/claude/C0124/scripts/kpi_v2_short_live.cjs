// C0124: ЖИВОЕ чтение KPI V2 (вход admin, GET picker-kpis) по свежему native-кейсу root CASE1153 / склад 20033496:
// строка с согласованной недостачей засчитана последнему отборщику. Только чтение; пароль не печатается; учётку кейса не используем.
const fs=require("fs"),path=require("path"),assert=require("assert");const {chromium}=require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const pass=fs.readFileSync("C:/projects/TMS/AGENTS.md","utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const URL0="http://127.0.0.1:3000/src/features/platform/workspaces/preview/index.html?workspace=kpi&warehouse_id=20033496&kpi_start=2026-10-17T04:00&kpi_finish=2026-10-17T06:00&kpi_zone=%2B00:00";
const res={writes:[],errors:[]};
(async()=>{const b=await chromium.launch();for(const [w,h] of [[1440,1000],[390,844]]){const p=await(await b.newContext({viewport:{width:w,height:h}})).newPage();
p.on("pageerror",e=>res.errors.push(w+": "+e));p.on("request",r=>{if(r.method()!=="GET"&&r.url().includes(":8088/api/"))res.writes.push(r.method()+" "+r.url());});
const reply=p.waitForResponse(r=>r.url().includes("/api/resources/picker-kpis")&&r.request().method()==="GET",{timeout:40000});
await p.goto(URL0);await p.fill("input[autocomplete=username]","admin");await p.fill("input[type=password]",pass);await p.click("button[type=submit]");
res["status"+w]=(await reply).status();const sec=p.locator("section[aria-label='Выработка комплектовщиков']");await sec.locator(".kpi-metric").first().waitFor();
await sec.locator("select[data-help-id='kpi.operator']").selectOption("OC16Pd21d129674");await sec.locator("summary[data-help-id='kpi.pick.details']").click();
const r=await sec.evaluate(s=>({summary:s.querySelector(".kpi-summary")?.innerText,completions:s.querySelector(".kpi-details table")?.innerText,quality:s.querySelector(".kpi-quality")?.innerText??null,overflow:document.documentElement.scrollWidth-innerWidth}));
assert(/из них с согласованной недостачей: 1/.test(r.summary),r.summary);assert(/С согласованной недостачей/.test(r.completions),r.completions);
assert(/Согласованная недостача\s*AS16A082D87DBD8: 1 EA/.test(r.quality),r.quality);assert(r.overflow<=0);res["w"+w]=r;
await sec.locator(".kpi-details table").first().scrollIntoViewIfNeeded();await p.screenshot({path:path.join(__dirname,"..","screenshots",`k3_live_short_${w}.png`)});await p.context().close();}
assert.deepEqual(res.writes,[]);assert.deepEqual(res.errors,[]);res.status="PASS";res.label="actual admin login + GET picker-kpis warehouse 20033496 (root native CASE1153)";
fs.writeFileSync(path.join(__dirname,"..","kpi_v2_short_live.json"),JSON.stringify(res,null,1));console.log(JSON.stringify(res,null,1));await b.close();})().catch(e=>{console.error(e.message);console.error(JSON.stringify(res).slice(0,1500));process.exit(1);});
