import fs from 'node:fs';
import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
let input='';for await(const part of process.stdin)input+=part;const credentials=JSON.parse(input);
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:430,height:920}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:3000/?page=driver&driver_id=10018');
 await page.getByLabel('Пользователь',{exact:true}).fill(credentials.driver.username);
 await page.getByLabel('Пароль',{exact:true}).fill(credentials.driver.password);
 await page.getByRole('button',{name:'Войти',exact:true}).click();
 await page.locator('input[type=date]').fill('2026-11-03');
 await page.getByText('Рейс #33571',{exact:true}).click();
 await page.getByRole('button',{name:'📦 Адреса',exact:true}).click();
 const receipt=page.locator('section').filter({has:page.getByRole('heading',{name:'Приёмка магазина',exact:true})}).first();
 await receipt.getByLabel('Адрес магазина').selectOption({index:1});
 await receipt.getByLabel('Пользователь получателя').fill(credentials.receiver.username);
 await receipt.getByLabel('Пароль',{exact:true}).fill(credentials.receiver.password);
 await receipt.getByRole('button',{name:'Показать доставленные места',exact:true}).click();
 await receipt.getByRole('button',{name:/B01.1238/}).first().waitFor();

 const facts=[];
 for (const suffix of [':1',':2']) {
  const place=receipt.getByRole('button',{name:new RegExp('B01.1238.*'+suffix+' ')});
  await place.click();
  await receipt.getByLabel('Идентификатор грузового места',{exact:true}).waitFor();
  const root='B01.1238:c0c2a00c0b'+suffix;
  await receipt.getByLabel('Идентификатор грузового места',{exact:true}).fill(root);
  await receipt.getByLabel('Грузовое место установлено перед камерами').check();
  if(await receipt.getByRole('button',{name:'Начать выгрузку',exact:true}).count()){
   const response=page.waitForResponse(r=>r.url().endsWith('/unloading/start')&&r.request().method()==='POST');
   await receipt.getByRole('button',{name:'Начать выгрузку',exact:true}).click();
   const r=await response;facts.push({kind:'start',status:r.status(),body:await r.json()});
   if(!r.ok())throw Error('Start failed: '+JSON.stringify(facts.at(-1)));
  }
  await receipt.getByLabel('Способ выгрузки').selectOption('PALLET');
  await receipt.getByLabel('Основание подтверждения',{exact:true}).fill('OWN.DEV.B03.1313'+suffix);
  const response=page.waitForResponse(r=>r.url().endsWith('/store-receipts/confirm')&&r.request().method()==='POST');
  await receipt.getByRole('button',{name:'Подтвердить полную приёмку',exact:true}).click();
  const r=await response;facts.push({kind:'receipt',status:r.status(),body:await r.json(),request:r.request().postDataJSON()});
  fs.writeFileSync('tmp/result1313.json',JSON.stringify({facts,errors},null,2));
  if(!r.ok())throw Error('Receipt failed: '+JSON.stringify(facts.at(-1)));
  await receipt.getByText('Это место уже принято.',{exact:true}).waitFor();
 }
 await receipt.screenshot({path:'reports/nicora/2026-10-13/screenshots/86-b03-store-received.png'});
 console.log(JSON.stringify({facts,errors}));
}finally{await browser.close();}
