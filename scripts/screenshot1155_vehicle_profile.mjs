import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const context=JSON.parse(fs.readFileSync('tmp/context1152.json','utf8'));
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1080}});
 await page.goto('http://127.0.0.1:3000/?page=fleet',{waitUntil:'domcontentloaded',timeout:30000});
 const row=page.locator('tr').filter({hasText:context.profile.base.vehicle_number});
 await row.getByRole('button',{name:'Профиль',exact:true}).click({timeout:30000});
 const card=page.getByRole('region',{name:'Физический класс автомобиля'});
 await card.getByRole('button',{name:'Показать текущую карточку',exact:true}).click();
 await card.getByText('Профиль соответствует карточке.',{exact:false}).waitFor({timeout:30000});
 const lower=card.getByRole('textbox',{name:'Минимум температуры машины, °C',exact:true});
 if(await lower.inputValue()!=='-20.125')throw Error('Real range not rendered');
 await card.scrollIntoViewIfNeeded();
 await page.screenshot({path:'reports/nicora/2026-10-13/screenshots/45-vehicle-temperature-profile.png'});
 await page.setViewportSize({width:390,height:844});
 await card.scrollIntoViewIfNeeded();
 await card.screenshot({path:'reports/nicora/2026-10-13/screenshots/46-vehicle-temperature-profile-mobile.png'});
 console.log('PASS1155 real current fleet profile/Celsius fields/desktop and mobile screenshots; no UI writes');
}finally{await browser.close();}
