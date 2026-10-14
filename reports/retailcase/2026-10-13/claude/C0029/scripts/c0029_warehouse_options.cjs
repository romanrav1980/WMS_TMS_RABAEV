// C-0029 п.2: лёгкий справочник складов в quality-policy. Только чтение.
const fs=require("fs");const {chromium}=require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT=process.argv[2];
(async()=>{const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1280,height:900}})).newPage();const calls=[];
 p.on("response",r=>{if(/warehouses/.test(r.url()))calls.push({path:r.url().replace(/^.*\/api/,"/api"),status:r.status()});});
 await p.goto("http://127.0.0.1:5190/quality-policy.html");await p.click("#loginFillAdmin");await p.locator("input[type=password]").evaluate(el=>el.closest("form").requestSubmit());
 await p.waitForFunction(()=>/Показано|не найден|недоступен/.test(document.getElementById("qsWareNote").textContent),null,{timeout:30000});
 const initial=await p.textContent("#qsWareNote");
 await p.fill("#qsWareFind","9807");await p.waitForFunction(()=>document.getElementById("qsWareList").options.length===2,null,{timeout:15000});
 await p.selectOption("#qsWareList","9807");await p.waitForTimeout(300);
 const res={initial,afterSearch:await p.locator("#qsWareList option").allTextContents(),ware:await p.inputValue("#qsWare"),scope:await p.textContent("#qsScope"),calls};
 await p.locator(".qs-box").first().screenshot({path:OUT+"/w1_warehouse_options.png"});
 fs.writeFileSync(OUT+"/../c0029_warehouse_options.json",JSON.stringify(res,null,1));console.log(JSON.stringify(res,null,1));await b.close();})().catch(e=>{console.error(e);process.exit(1);});
