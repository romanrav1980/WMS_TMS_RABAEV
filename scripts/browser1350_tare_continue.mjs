import fs from 'node:fs';
import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
let input='';for await(const part of process.stdin)input+=part;const credentials=JSON.parse(input);
const ctx=JSON.parse(fs.readFileSync('tmp/context1348.json','utf8'));
const browser=await chromium.launch({headless:true}),facts=JSON.parse(fs.readFileSync('tmp/result1349.json','utf8')).facts,errors=[];
const save=()=>fs.writeFileSync('tmp/result1349.json',JSON.stringify({facts,errors},null,2));
try{
 const pages={};
 async function open(role){
  const page=await browser.newPage({viewport:{width:430,height:940}});pages[role]=page;page.on('pageerror',e=>{errors.push(e.message);save();});
  await page.goto('http://127.0.0.1:3000/?page=driver&driver_id=10018');
  await page.getByLabel('Пользователь',{exact:true}).fill(credentials.driver.username);
  await page.getByLabel('Пароль',{exact:true}).fill(credentials.driver.password);
  await page.getByRole('button',{name:'Войти',exact:true}).click();
  await page.locator('input[type=date]').fill('2026-11-03');await page.getByText('Рейс #33571',{exact:true}).click();await page.getByRole('button',{name:'📦 Адреса',exact:true}).click();
  const panel=page.locator('.tare-workspace');await panel.getByLabel('Учётная запись',{exact:true}).fill(credentials[role].username);await panel.getByLabel('Пароль',{exact:true}).fill(credentials[role].password);
  await panel.getByRole('button',{name:'Показать передачи этого рейса',exact:true}).click();await panel.locator('.tare-history').waitFor();
  return {page,panel};
 }
 const sessions={};for(const role of ['admin','driver','store'])sessions[role]=await open(role);
 async function offer(role,preset,qty){
  const {page,panel}=sessions[role];
  await panel.getByRole('button',{name:'Показать передачи этого рейса',exact:true}).click();await panel.getByRole('button',{name:preset,exact:true}).click();
  console.log(JSON.stringify(await panel.locator('fieldset').evaluateAll(nodes=>nodes.map(n=>({legend:n.querySelector('legend')?.textContent,disabled:n.disabled,labels:[...n.querySelectorAll('label')].map(x=>x.textContent.slice(0,110))}))))); const form=panel.getByRole('group',{name:'Отправитель передаёт тару',exact:true});
  await form.getByLabel('Склад-владелец',{exact:true}).selectOption(String(ctx.warehouse));await form.getByLabel('Тип тары',{exact:true}).selectOption(String(ctx.type));
  if(await form.getByLabel('Магазин-отправитель',{exact:true}).count())await form.getByLabel('Магазин-отправитель',{exact:true}).selectOption(ctx.store);
  if(await form.getByLabel('Магазин-получатель',{exact:true}).count())await form.getByLabel('Магазин-получатель',{exact:true}).selectOption(ctx.store);
  await form.getByLabel('Количество тары',{exact:true}).fill(String(qty));await form.getByLabel('Скан машины',{exact:true}).fill(ctx.plate);
  const response=page.waitForResponse(r=>r.url().endsWith('/tare/offer')&&r.request().method()==='POST');
  await form.getByRole('button',{name:'Предложить передачу',exact:true}).click();const r=await response;const result=await r.json();facts.push({role,action:'offer',request:r.request().postDataJSON(),result,status:r.status()});save();if(!r.ok())throw Error(JSON.stringify(result));
  await panel.getByRole('status').filter({hasText:'Передача предложена'}).waitFor();return result.operation_id;
 }
 async function accept(role,offerId,qty,lost=false){
  const {page,panel}=sessions[role];await panel.getByRole('button',{name:'Показать передачи этого рейса',exact:true}).click();
  await page.waitForFunction(()=>document.querySelectorAll('.tare-workspace fieldset').length>1);
  const form=panel.locator('fieldset').filter({hasText:'Фактически принято тары'}).first();
  await form.getByLabel('Фактически принято тары',{exact:true}).fill(String(qty));await form.getByLabel('Скан машины',{exact:true}).fill(ctx.plate);
  if(lost){
   await page.route('**/api/inventory/tare/accept',async route=>{
    const response=await route.fetch(),result=await response.json();facts.push({role,action:'accept-lost',request:route.request().postDataJSON(),result,status:response.status()});save();
    await route.abort('failed');
   },{times:1});
   await form.getByRole('button',{name:'Получатель принял тару',exact:true}).click();
   const retry=panel.getByRole('button',{name:'Повторить сохранённую операцию',exact:true});await retry.waitFor();await retry.click();
   await panel.getByRole('status').filter({hasText:'Приёмка тары проведена'}).waitFor();
   const saved=facts.at(-1);facts.push({role,action:'retry-visible',operation_id:saved.request.operation_id});save();
  }else{
   const response=page.waitForResponse(r=>r.url().endsWith('/tare/accept')&&r.request().method()==='POST');
   await form.getByRole('button',{name:'Получатель принял тару',exact:true}).click();const r=await response;const result=await r.json();facts.push({role,action:'accept',request:r.request().postDataJSON(),result,status:r.status()});save();if(!r.ok())throw Error(JSON.stringify(result));
   if(facts.at(-1).request.offer_operation_id!==offerId)throw Error('Wrong offer accepted');
   await panel.getByRole('status').filter({hasText:'Приёмка тары проведена'}).waitFor();
  }
 }
 
 const delivered=facts.find(f=>f.role==='driver'&&f.action==='offer').result.operation_id;await accept('store',delivered,6);
 const returned=await offer('store','Возврат из магазина',4);await accept('driver',returned,4);
 const unloaded=await offer('driver','Возврат на склад',4);await accept('admin',unloaded,4);
 const {panel}=sessions.admin;
 await panel.getByLabel('Склад-владелец',{exact:true}).selectOption(String(ctx.warehouse));
 await panel.locator('.tare-balances summary').click();await panel.getByRole('button',{name:'Обновить баланс тары',exact:true}).click();
 await panel.locator('.tare-balances strong').first().waitFor();
 await panel.locator('.tare-balances').screenshot({path:'reports/retailcase/2026-10-13/screenshots/90-b05-tare-balance.png'});
 await panel.locator('.tare-history').screenshot({path:'reports/retailcase/2026-10-13/screenshots/91-b05-tare-history.png'});
 save();console.log(JSON.stringify({actions:facts.length,errors}));if(errors.length)throw Error('Browser errors');
}finally{await browser.close();}
