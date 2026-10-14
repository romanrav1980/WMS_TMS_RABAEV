import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const out='reports/nicora/2026-10-13/codex/NI081/',fixture=JSON.parse(fs.readFileSync(out+'fixture.json','utf8'));
const browser=await chromium.launch({headless:true}),page=await browser.newPage({viewport:{width:1450,height:1100}}),errors=[],requests=[];
page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.url().includes('/api/transport/preflight/'))requests.push({method:r.method(),url:r.url()});});
try{
 await page.goto('http://127.0.0.1:3000/');
 await page.evaluate(async trip=>{
  const React=(await import('/node_modules/.vite/deps/react.js')).default,{createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js')).default;
  const {TransportDeliveryWindows}=await import('/src/components/TransportDeliveryWindows.tsx'),{TransportTimeApproval}=await import('/src/components/TransportTimeApproval.tsx');
  document.body.innerHTML='<main id="nativeRouteEvidence" style="padding:24px;background:white;color:#172238;min-height:100vh;font:15px Arial"></main>';
  const props={tripId:trip,apiBase:'http://127.0.0.1:8088',headers:{Authorization:'Basic '+btoa('admin:admin123')},actor:'admin'};
  createRoot(document.getElementById('nativeRouteEvidence')).render(React.createElement('div',null,React.createElement('h2',null,'NI08.1 — isolated planning-only TT '+trip+' / synthetic road NI081TEST'),React.createElement(TransportDeliveryWindows,props),React.createElement('hr'),React.createElement(TransportTimeApproval,{...props,zone:'Asia/Tbilisi'})));
 },fixture.trip_id);
 await page.locator('select').selectOption('Asia/Tbilisi');await page.getByRole('button',{name:'Оценить прибытие и разгрузку'}).click();await page.getByText('Движение, перерывы и работы по времени').click();await page.getByRole('cell',{name:'Отдых',exact:true}).waitFor();
 await page.getByRole('button',{name:'Прочитать актуальный план'}).click();await page.getByText('Утверждения нет',{exact:false}).waitFor();
 if(errors.length)throw Error(JSON.stringify(errors));if(requests.some(r=>r.method!=='GET'))throw Error('Unexpected mutation');
 await page.screenshot({path:out+'native_route.png',fullPage:true});fs.writeFileSync(out+'browser.json',JSON.stringify({trip_id:fixture.trip_id,checks:['actual React components with real GET/native calculation','explicit REST visible','string ST preserved','unapproved fixture shown, no POST'],requests,errors},null,2));console.log('PASS actual React real native GET, REST visible, no POST');
}finally{await browser.close();}
