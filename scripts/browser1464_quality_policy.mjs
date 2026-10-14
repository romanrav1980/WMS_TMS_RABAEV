import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const b=await chromium.launch({headless:true});
try{
 const p=await b.newPage({viewport:{width:1300,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto('http://127.0.0.1:8088/wms-admin/quality-policy.html?warehouse_id=6524567');await p.locator('#adminLoginForm button[type=submit]').click();
 await p.locator('#qsCategory').selectOption('STOCK');await p.locator('#qsRead').click();await p.locator('#qsVersion').filter({hasText:'Текущая версия'}).waitFor();
 const before=await p.locator('#qsVersion').textContent();let first=true;const sent=[];let committed;
 await p.route('**/api/inventory/quality-policies/warehouses/6524567',async route=>{
  if(route.request().method()!=='POST')return route.continue();sent.push(route.request().postData());
  if(first){first=false;const real=await route.fetch();committed=await real.json();if(real.status()!==200)throw Error(JSON.stringify(committed));return route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'Synthetic response loss after real commit'})});}
  return route.continue();
 });
 await p.locator('#qsReason').fill('Адресная проверка восстановления после потери ответа');await p.locator('#qsSave').click();await p.locator('#qsStatus').filter({hasText:'Результат не подтверждён'}).waitFor();
 await p.reload();await p.locator('#qsRetry').click();await p.locator('#qsStatus').filter({hasText:'Правило сохранено'}).waitFor();
 if(sent.length!==2||sent[0]!==sent[1])throw Error('Command changed on replay');
 await p.locator('main').screenshot({path:'reports/nicora/2026-10-13/screenshots/113-ni051-quality-policy.png'});
 const operation=JSON.parse(sent[0]).operation_id;
 await p.locator('#qsActive').uncheck();await p.locator('#qsReason').fill('Завершение частной проверки, возврат исходного режима склада');
 const disabled=p.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/quality-policies/warehouses/6524567'));
 await p.locator('#qsSave').click();const end=await disabled;if(end.status()!==200)throw Error(await end.text());const result=await end.json();if(result.active!==0)throw Error('Private rule not disabled');
 if(errors.length)throw Error(JSON.stringify(errors));
 const report={before,operation,firstCommitted:committed,replayExact:true,disabled:result,errors};fs.writeFileSync('tmp/result1464.json',JSON.stringify(report,null,2));console.log(JSON.stringify({replayExact:true,operation,version:committed.version,disabledVersion:result.version,errors}));
}finally{await b.close();}
