import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const out='reports/nicora/2026-10-13/codex/VEHICLE_OUTER/';fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch({headless:true}),page=await browser.newPage({viewport:{width:1350,height:1100}});
const profile={vehicle_id:999991,version:0,state:'NOT_CONFIGURED',base_hash:'A'.repeat(64),base:{vehicle_number:'UI FIXTURE — NOT LIVE',vehicle_type:'20',pallet_capacity:'10',max_weight_kg:'10000'},profile:{vehicle_size_class:'TRUCK',cargo_length_mm:5000,cargo_width_mm:2000,cargo_height_mm:2200,outer_height_mm:null,outer_length_mm:null}};
const posts=[];let lose=true;
try{
 await page.route('**/api/**',async route=>{const req=route.request(),url=new URL(req.url());
  if(url.pathname.endsWith('/vehicles/999991/profile'))return route.fulfill({json:profile});
  if(url.pathname.endsWith('/vehicle-profiles/tare-types'))return route.fulfill({json:[]});
  if(url.pathname.endsWith('/vehicle-profiles')&&req.method()==='POST'){const body=req.postDataJSON();posts.push(body);if(lose){lose=false;return route.abort();}profile.profile={...profile.profile,...body};profile.version=1;return route.fulfill({json:{version:1}});}
  return route.fulfill({json:[]});
 });
 await page.goto('http://127.0.0.1:3000/');
 await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js')).default,{createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js')).default,{VehiclePhysicalProfile}=await import('/src/features/finance/VehiclePhysicalProfile.tsx');document.body.innerHTML='<main id="outer" style="padding:24px;background:white;color:#172238;font:15px Arial"><h1>UI fixture — Oracle migration not applied</h1></main>';const node=document.createElement('div');document.getElementById('outer').append(node);createRoot(node).render(React.createElement(VehiclePhysicalProfile,{vehicle:999991,onClose:()=>{}}));});
 await page.getByRole('button',{name:'Показать текущую карточку',exact:true}).click();
 await page.getByLabel('Наружная высота автомобиля, мм',{exact:true}).fill('3500');
 await page.getByLabel('Полная наружная длина автомобиля, мм',{exact:true}).fill('6500');
 await page.getByLabel('Причина настройки',{exact:true}).fill('UI fixture external dimensions');
 await page.getByLabel('Основание габаритов и температурного диапазона',{exact:true}).fill('UI fixture');
 await page.screenshot({path:out+'profile.png',fullPage:true});
 await page.getByRole('button',{name:'Сохранить профиль',exact:true}).click();
 await page.getByText('Результат не подтверждён',{exact:false}).waitFor();
 await page.getByRole('button',{name:'Повторить сохранённую операцию',exact:true}).click();
 await page.getByText('Профиль сохранён, версия 1.',{exact:true}).waitFor();
 if(posts.length!==2||JSON.stringify(posts[0])!==JSON.stringify(posts[1])||posts[0].outer_height_mm!==3500||posts[0].outer_length_mm!==6500)throw Error('outer intent mismatch');
 await page.evaluate(()=>{for(const key of Object.keys(localStorage))if(key.endsWith(':999991'))localStorage.removeItem(key);});
 fs.writeFileSync(out+'browser.json',JSON.stringify({fixture:true,native_migration_applied:false,requests:posts,checks:['outer separate fromcargo','lost response preserves immutable outervalues','same operation exact replay']},null,2));console.log('PASS outer dimensions UI fixture/exact lostresponse replay; screenshot');
}finally{await browser.close();}
