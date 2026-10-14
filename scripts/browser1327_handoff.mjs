import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
let input='';for await(const part of process.stdin)input+=part;const credentials=JSON.parse(input);
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:430,height:920}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 let started=false,submitted=null;const responses=[];
 await page.route('**/api/delivery/store-receipts/**',async route=>{
  const request=route.request(),url=new URL(request.url());
  if(request.method()==='POST'){
   if(url.pathname.endsWith('/unloading/start')){started=true;await route.fulfill({status:200,json:{operation_id:request.postDataJSON().operation_id,status:'STARTED'}});return;}
   if(url.pathname.endsWith('/confirm')){submitted=request.postDataJSON();await route.fulfill({status:200,json:{operation_id:submitted.operation_id,status:'ACCEPTED'}});return;}
   await route.abort();return;
  }
  const response=await route.fetch(),data=await response.json();
  if(url.pathname.endsWith('/preview')){data.already_received=false;data.unloading=started?{...data.unloading,status:'STARTED',receipt_operation_id:null}:null;}
  if(url.pathname.endsWith('/places')&&Array.isArray(data))for(const row of data){row.receipt_state=null;row.receipt_operation_id=null;}
  await route.fulfill({response,json:data});
 });
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

 await receipt.getByRole('button',{name:/B01.1238/}).first().click();
 await receipt.getByLabel('Идентификатор грузового места',{exact:true}).fill('B01.1238:c0c2a00c0b:1');
 await receipt.getByLabel('Грузовое место установлено перед камерами').check();
 await receipt.getByRole('button',{name:'Начать выгрузку',exact:true}).click();
 await receipt.getByLabel('Способ выгрузки').selectOption('PALLET');
 await receipt.getByLabel('Основание подтверждения',{exact:true}).fill('UI_ONLY_NO_DB_WRITE');
 await receipt.getByRole('button',{name:'Подтвердить полную приёмку',exact:true}).click();
 try{await receipt.getByText(/Приёмка подтверждена/).waitFor({timeout:4000});}catch{}
 console.log(JSON.stringify({kind:'synthetic API lifecycle; no writes',started,submitted,text:await receipt.innerText(),errors}));
 if(!submitted?.unloading)throw Error('Continuous UI did not send unloading receipt');
}finally{await browser.close();}
