import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const out='reports/nicora/2026-10-13/codex/C0023/';fs.mkdirSync(out,{recursive:true});const native=JSON.parse(fs.readFileSync('tmp/codex_c0023_receipt_result.json','utf8'));
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[],posts=[],checks=[];page.on('pageerror',e=>{errors.push(e.message);console.log('PAGEERROR '+e.message);});
 await page.route('**/c0023-harness',route=>route.fulfill({contentType:'text/html',body:`<div id="root"></div><script type="module">import RefreshRuntime from '/@react-refresh';RefreshRuntime.injectIntoGlobalHook(window);window.$RefreshReg$=()=>{};window.$RefreshSig$=()=>type=>type;window.__vite_plugin_react_preamble_installed__=true;</script><script type="module">import React from '/node_modules/.vite/deps/react.js';import ReactDOM from '/node_modules/.vite/deps/react-dom_client.js';import {StoreReceiptPanel} from '/src/features/delivery/StoreReceiptPanel.tsx';ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(StoreReceiptPanel,{tripId:33571,addresses:['Store C0023']}));</script>`}));
 const preview={load_operation_id:'LOAD.C0023',store_address:'Store C0023',root:'ROOT.C0023',root_scan_identifier:'PAL.C0023',composition_signature:'A'.repeat(64),mode:'WEIGHT_PHOTO',shipping_gross_weight_kg:'1.45',shipping_weight_tolerance_kg:'0.225',requires_marked_recipient_flow:true,already_received:false,marked_partial_control:true,marked_unit_control:{supported:true,expected_scan_count:1,physical_unit_count:1,profiles:[{system_code:'CRPT',profile_code:'TOBACCO',profile_version:'1',scan_mode:'UNIT'}],units:[{key:'u1',lot_uid:'LOT.C0023',article:'ART.C0023',quantity:'7',base_uom:'EA',profiles:[{system_code:'CRPT',profile_code:'TOBACCO',profile_version:'1',scan_mode:'UNIT'}]}]},snapshot:{nodes:[{uid:'LOT.C0023',kind:'STOCK',article:'ART.C0023',quantity:'7',base_uom:'EA'}]}};
 let responseMode='reject';
 await page.route('**/api/delivery/**',async route=>{
  const r=route.request(),url=new URL(r.url());
  if(r.method()==='OPTIONS'){await route.fulfill({status:204,headers:{'access-control-allow-origin':'*','access-control-allow-headers':'*','access-control-allow-methods':'GET,POST,OPTIONS'}});return;}
  let body,status=200;
  if(url.pathname.endsWith('/places'))body=[{load_operation_id:'LOAD.C0023',root_key:'ROOT.C0023',receipt_state:null}];
  else if(url.pathname.endsWith('/preview'))body=preview;
  else if(url.pathname.endsWith('/store-photos/list'))body=['FRONT','LEFT','RIGHT'].map((view,i)=>({photo_id:'PHOTO'+i,sha256:'sha'+i,view,recorded_at:'2026-10-14T12:00:00Z',recorded_by:'STORE',mime_type:'image/png'}));
  else if(url.pathname.endsWith('/store-scales/captures'))body={items:[{capture_key:'CAPTURE.C0023',device_id:'DEV',gross_weight_kg:'1.45',received_at:'2026-10-14T12:00:00Z',sample_count:4,span_ms:1500,calibration_ref:'TEST'}]};
  else if(url.pathname.endsWith('/confirm')){
   const input=r.postDataJSON();posts.push(input);
   if(responseMode==='reject'){status=422;body={detail:{message:'TEST: проверьте количество',outcome_confirmed:true,operation_id:input.operation_id}};}
   else body={...native,operation_id:responseMode==='wrong'?'OTHER.OP':input.operation_id,load_operation_id:input.load_operation_id,store_address:input.store_address,discrepancy_case_id:input.operation_id};
  }else{await route.fulfill({status:404,json:{detail:'Unexpected mocked path '+url.pathname}});return;}
  await route.fulfill({status,json:body,headers:{'access-control-allow-origin':'*'}});
 });
 await page.goto('http://127.0.0.1:3000/c0023-harness');await page.getByLabel('Пользователь получателя').fill('STORE');await page.getByLabel('Пароль',{exact:true}).fill('fixture');await page.getByRole('button',{name:'Показать доставленные места'}).click();await page.getByRole('button',{name:/ROOT.C0023/}).click();
 await page.getByLabel('Идентификатор грузового места').fill('PAL.C0023');await page.getByLabel('Грузовое место установлено перед камерами').check();
 await page.getByLabel('QR штуки',{exact:true}).fill('QR.C0023');await page.getByRole('button',{name:'Добавить',exact:true}).click();await page.getByRole('button',{name:'Показать фотоархив',exact:true}).click();await page.getByRole('button',{name:'Показать архивированные измерения'}).click();await page.getByLabel('Выбрать измерение').check();
 await page.getByLabel('Указать фактические количества и расхождения').check();await page.getByLabel('Принято',{exact:true}).fill('3');await page.getByLabel('Недостача',{exact:true}).fill('2');await page.getByLabel('Отказ',{exact:true}).fill('1');await page.getByLabel('Повреждено',{exact:true}).fill('1');await page.getByLabel('Причина расхождения').fill('C0023: input must survive');
 await page.getByRole('button',{name:'Подтвердить фактическую приёмку'}).click();await page.getByRole('button',{name:'Исправить данные после отказа'}).click();
 await page.waitForFunction(()=>document.body.textContent.includes('количества, фотографии и сканы сохранены'));
 if(await page.getByLabel('Принято',{exact:true}).inputValue()!=='3'||!await page.getByLabel('Выбрать измерение').isChecked()||await page.locator('input[type=checkbox]:checked').count()<5||!(await page.textContent('body')).includes('QR: 1.'))throw Error('Correction lost input');
 checks.push('confirmed rejection fresh preview preserves quantities, note, photos, scale and QR');responseMode='wrong';await page.getByRole('button',{name:'Подтвердить фактическую приёмку'}).click();await page.getByRole('button',{name:'Повторить сохранённую операцию',exact:true}).waitFor();
 if(await page.getByRole('heading',{name:'Акт расхождения при приёмке'}).count())throw Error('Wrong ID accepted');checks.push('mismatched response preserves pending');responseMode='success';await page.getByRole('button',{name:'Повторить сохранённую операцию',exact:true}).click();await page.getByRole('heading',{name:'Акт расхождения при приёмке'}).waitFor();
 if(JSON.stringify(posts[1])!==JSON.stringify(posts[2]))throw Error('Retry changed body');const act=page.getByRole('region',{name:'Подтверждённый акт приёмки'});await act.screenshot({path:out+'confirmed-act.png'});
 const href=await act.getByRole('link').getAttribute('href');if(!href.includes('/wms-admin/store-investigations.html?case_id='))throw Error('Wrong dossier link');checks.push('same request retry displays native result quantities and next steps');
 await page.getByLabel('Пользователь получателя').fill('OTHER');await page.waitForFunction(()=>!document.querySelector('[aria-label="Подтверждённый акт приёмки"]'));checks.push('actor change clears prior receipt');
 if(errors.length)throw Error(JSON.stringify(errors));fs.writeFileSync(out+'browser.json',JSON.stringify({mocked_api:true,native_result_fixture:'STORE383.RECEIPT:c09bc5c0',checks,post_count:posts.length,real_posts:0,errors},null,2));console.log(JSON.stringify({checks,errors}));
}finally{await browser.close();}