import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const data=JSON.parse(fs.readFileSync('tmp/context1182.json','utf8'));
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1080}});
 await page.goto('http://127.0.0.1:3000/?page=fleet',{waitUntil:'domcontentloaded'});
 const row=page.locator('tr').filter({hasText:data.after.base.vehicle_number});
 await row.getByRole('button',{name:'Профиль',exact:true}).click();
 const card=page.getByRole('region',{name:'Физический класс автомобиля'});
 await card.getByRole('button',{name:'Показать текущую карточку',exact:true}).click();
 const variants=card.getByRole('region',{name:'Нормативные варианты загрузки'});
 await card.getByText('Версия 2.',{exact:false}).waitFor();
 const code=variants.getByRole('textbox',{name:'Код варианта'}).first();
 if(await code.inputValue()!=='MIXED')throw Error('Saved current variants missing');
 if(await variants.getByRole('combobox').count()!==3)throw Error('Expected 3 configured type rows');
 await variants.scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/nicora/2026-10-13/screenshots/49-vehicle-tare-variants.png'});
 await page.setViewportSize({width:390,height:844});
 await variants.screenshot({path:'reports/nicora/2026-10-13/screenshots/50-vehicle-tare-variants-mobile.png'});
 console.log('PASS1184 real current fleet profile version2/three tare limits; no UI writes');
}finally{await browser.close();}
