// C-0032 коррекция (C-0036): HTML 404 прокси не подтверждает отказ команды; структурированный 409 {detail:{code}} — подтверждает.
// POST перехватывается (mocked), реальный рейс не утверждается. Ответ Ганта сдвинут только для открытия карточки.
const fs=require("fs");const {chromium}=require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT=process.argv[2];const KEY='nicora.trip.time.pending:["http://127.0.0.1:8088","admin"]';
(async()=>{const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1440,height:950},serviceWorkers:"block"})).newPage();let mode="html404";const res={};
 await p.route("**/api/admin/transport/vehicles/gantt**",async r=>{const real=await (await r.fetch()).json();const sh=t=>t&&t.replace(/ 0(\d):/,(m,h)=>" "+String(8+Number(h)).padStart(2,"0")+":");
  r.fulfill({status:200,headers:{"access-control-allow-origin":"*","content-type":"application/json"},body:JSON.stringify(real.map(v=>({...v,operations:v.operations.map(o=>({...o,plan_start:sh(o.plan_start),plan_end:sh(o.plan_end)}))})))});});
 await p.route("**/api/transport/preflight/time-approvals",r=>mode==="html404"
  ?r.fulfill({status:404,headers:{"access-control-allow-origin":"*","content-type":"text/html"},body:"<html><body>404 Not Found (proxy)</body></html>"})
  :r.fulfill({status:409,headers:{"access-control-allow-origin":"*","content-type":"application/json"},body:JSON.stringify({detail:{code:"TIME_SOURCE_APPROVAL_CHANGED",message:"План изменился"}})}));
 await p.goto("http://127.0.0.1:3000/?page=gantt");await p.waitForSelector("svg rect[style*=pointer]",{timeout:60000});await p.locator("svg rect[style*=pointer]").first().click();
 await p.locator('select[aria-label="Часовой пояс плановых дат"]').selectOption("Europe/Moscow");await p.getByRole("button",{name:"Прочитать актуальный план"}).click();
 await p.waitForSelector('input[aria-label="Основание утверждения времени"]',{timeout:20000});await p.fill('input[aria-label="Основание утверждения времени"]',"MOCK C0032 malformed 404");
 await p.getByRole("button",{name:"Утвердить маршрут и время"}).click();await p.waitForTimeout(800);
 res.html404={message:await p.locator(".gantt-card-actions p[role=status]").last().textContent(),kept:(await p.evaluate(k=>localStorage.getItem(k),KEY))!==null,retryVisible:await p.getByRole("button",{name:"Повторить сохранённое утверждение"}).isVisible()};
 mode="structured409";await p.getByRole("button",{name:"Повторить сохранённое утверждение"}).click();await p.waitForTimeout(800);
 res.structured409={message:await p.locator(".gantt-card-actions p[role=status]").last().textContent(),cleared:(await p.evaluate(k=>localStorage.getItem(k),KEY))===null};
 await p.evaluate(k=>localStorage.removeItem(k),KEY);fs.writeFileSync(OUT+"/../c0032_malformed404.json",JSON.stringify(res,null,1));console.log(JSON.stringify(res,null,1));await b.close();})().catch(e=>{console.error(e);process.exit(1);});
