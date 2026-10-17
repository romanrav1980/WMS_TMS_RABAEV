// C0122: отладка 390 px страницы комплектации (живой GET под admin), список элементов за пределами экрана.
const fs=require("fs"),path=require("path");const {chromium}=require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const pass=fs.readFileSync("C:/projects/TMS/AGENTS.md","utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
(async()=>{const b=await chromium.launch();const p=await(await b.newContext({viewport:{width:390,height:844}})).newPage();
await p.route("**/api/case-pick/**",r=>r.request().method()==="GET"?r.continue():r.abort());
await p.goto("http://127.0.0.1:8088/wms-admin/case-pick-management.html");await p.fill("#loginUser","admin");await p.fill("#loginPassword",pass);await p.click("#adminLoginForm button[type=submit]");
await p.waitForSelector("#caseRows tr",{timeout:30000});await p.waitForTimeout(800);
const r=await p.evaluate(()=>{const vw=innerWidth;const out=[];document.querySelectorAll("body *").forEach(e=>{const b=e.getBoundingClientRect();if(b.width&&b.right>vw+1&&!e.closest(".case-table-wrap,.nav")){out.push((e.id?"#"+e.id:e.tagName+"."+[...e.classList].join("."))+" in "+e.parentElement.className+" l="+Math.round(b.left)+" r="+Math.round(b.right)+" w="+Math.round(b.width));}});return{sw:document.documentElement.scrollWidth,vw,out:out.slice(0,25)};});
console.log(JSON.stringify(r,null,1));await p.evaluate(()=>scrollTo(0,0));await p.screenshot({path:path.join(__dirname,"..","mobile_probe.png"),fullPage:false});await b.close();})();
