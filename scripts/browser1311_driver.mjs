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
 await page.screenshot({path:'reports/retailcase/2026-10-13/screenshots/85-b03-driver-places.png',fullPage:true});
 console.log(JSON.stringify({text:await receipt.innerText(),errors}));
}finally{await browser.close();}
