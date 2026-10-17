// C0122: регрессия плоских прав (admin, живой вход, только чтение): секции «Выезд» и HU по-прежнему видны, отказа нет.
const fs=require("fs"),assert=require("assert");const {chromium}=require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const pass=fs.readFileSync("C:/projects/TMS/AGENTS.md","utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
(async()=>{const b=await chromium.launch();const p=await(await b.newContext()).newPage();const errors=[];p.on("pageerror",e=>errors.push(String(e)));
await p.route("**/api/**",r=>r.request().method()==="GET"?r.continue():r.abort());
await p.goto("http://127.0.0.1:8088/wms-admin/transport-loading.html");await p.fill("#loginUser","admin");await p.fill("#loginPassword",pass);await p.click("#adminLoginForm button[type=submit]");await p.waitForTimeout(3000);
const loading=await p.locator('section[data-native-capability="dispatch"]').evaluateAll(n=>n.map(x=>!x.hidden));const depart=loading.length===2&&loading.every(Boolean);
await p.goto("http://127.0.0.1:8088/wms-admin/warehouse-hus.html");await p.waitForTimeout(3000);
const hus={denied:await p.locator(".access-denied").count(),sections:await p.locator("section[data-native-capability]").evaluateAll(n=>n.map(x=>!x.hidden))};
const r={depart,loading,hus,errors};console.log(JSON.stringify(r));assert(depart&&hus.denied===0&&hus.sections.every(Boolean)&&!errors.length);
fs.writeFileSync(__dirname+"/final-native-gates.json",JSON.stringify({...r,status:"PASS"},null,1));await b.close();})().catch(e=>{console.error(e.message);process.exit(1);});
