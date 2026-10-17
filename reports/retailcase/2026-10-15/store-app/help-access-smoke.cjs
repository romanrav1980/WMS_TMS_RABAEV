const {chromium}=require('../../../../admin/wms_admin_frontend/node_modules/playwright');
const {QRCodeWriter,BarcodeFormat}=require('../../../../terminal/wms_terminal_web/node_modules/@zxing/library');
const fs=require('fs'),path=require('path'),assert=require('assert');
const base=process.env.STORE_UI_URL||'http://127.0.0.1:3010/store/';
const signature='A'.repeat(64),load='TEST.LOAD:1',store='test-store';
const receipt=op=>({operation_id:op,load_operation_id:load,store_address:'Магазин №12',root:'PALLET-1',status:'ACCEPTED',accepted_lines:[{line_no:1,lot_uid:'LOT1',article:'ART1',base_uom:'EA',accepted:'10'}]});
const preview=mode=>({load_operation_id:load,store_address:'Магазин №12',root:'PALLET-1',root_scan_identifier:'PALLET-1',composition_signature:signature,mode,shipping_gross_weight_kg:'12',shipping_weight_tolerance_kg:'0.5',requires_marked_recipient_flow:false,already_received:false,snapshot:{nodes:[{uid:'LOT1',kind:'STOCK',article:'ART1',quantity:'10',base_uom:'EA'}]}});
async function setup(browser,mode='BARCODE',width=390){
 const context=await browser.newContext({viewport:{width,height:844},serviceWorkers:'block'}),page=await context.newPage(),posts=[],errors=[];
 const state={mode,completed:false,unknown:true,statusVisible:false,weigh:null,weighReady:false};
 page.on('pageerror',error=>errors.push(String(error)));page.on('console',msg=>{if(msg.type()==='error'&&/Maximum update depth|Too many re-renders/.test(msg.text()))errors.push(msg.text());});
 await page.route('**/api/**',async route=>{
  const req=route.request(),url=new URL(req.url());let data;
  if(url.pathname==='/api/store-app/session')data={username:'receiver',display_name:'Receiver',access_revision:1,stores:[{store_id:store,address:'Магазин №12',receipt_mode:state.mode,policy_version:1}],limit:200,has_more:false,auth_scope:'STORE_RECEIPT'};
  else if(url.pathname==='/api/store-app/deliveries')data={store_id:store,items:[{load_operation_id:load,trip_id:3521,root_key:'PALLET-1',gross_weight_kg:12,departed_at:'2026-10-15T10:25:54.957001',time_status:'UNRESOLVED_SERVER_LOCAL'},{load_operation_id:'SAVED.LOAD',trip_id:3520,root_key:'PALLET-2',gross_weight_kg:8,departed_at:'2026-10-15T09:12:00.123456',time_status:'UNRESOLVED_SERVER_LOCAL',receipt_operation_id:'SAVED:1',receipt_state:'ACCEPTED'}],next_after:null,limit:50};
  else if(url.pathname==='/api/store-app/deliveries/lookup')data={store_id:store,load_operation_id:load,scanned_code:url.searchParams.get('code')};
  else if(url.pathname.startsWith('/api/store-app/deliveries/'))data={...preview(state.mode),...(state.marked?{requires_marked_recipient_flow:true,marked_partial_control:false,marked_unit_control:{supported:true,expected_scan_count:1,physical_unit_count:1,profiles:[{system_code:'CRPT',profile_code:'UNIT',profile_version:'1',scan_mode:'UNIT'}],units:[]}}:{}),...(state.completed?{already_received:true,receipt:{operation_id:'SAVED:1',state:'APPLIED',result:receipt('SAVED:1')}}:{})};
  else if(url.pathname.startsWith('/api/store-app/receipts/')){const op=decodeURIComponent(url.pathname.split('/').pop());data={operation_id:op,state:state.statusVisible?'APPLIED':'NOT_VISIBLE',outcome_confirmed:state.statusVisible,result:state.statusVisible?receipt(op):null};}
  else if(url.pathname==='/api/delivery/store-receipts/confirm'){posts.push(req.postData());if(state.unknown)return route.abort('failed');data=receipt(JSON.parse(req.postData()).operation_id);}
  else if(url.pathname==='/api/delivery/store-scales/devices')data={items:[{device_id:'SCALE-12',device_policy_version:1,active:true,capacity_kg:'1500',resolution_kg:'0.1',calibration_ref:'CAL1',calibrated_until:'2027-01-01T00:00:00+00:00',readiness:'READY',connectivity:'UNKNOWN'}]};
  else if(url.pathname==='/api/delivery/store-scales/requests'){state.weigh=JSON.parse(req.postData());if(state.weighReject)return route.fulfill({status:409,json:{detail:{request_id:state.weigh.request_id,outcome_confirmed:true,code:'SCALE_REQUEST_REJECTED',message:'WEIGH_DEVICE_BUSY'}}});data={...state.weigh,state:'REQUESTED',capture_key:null,expires_at:'2026-10-15T20:00:00+00:00',reason:null};}
  else if(url.pathname.startsWith('/api/delivery/store-scales/requests/'))data={...state.weigh,state:state.weighReady?'CAPTURED':'REQUESTED',capture_key:state.weighReady?'B'.repeat(64):null,expires_at:'2026-10-15T20:00:00+00:00',reason:null};
  else if(url.pathname.startsWith('/api/delivery/store-scales/captures/'))data={capture_key:'B'.repeat(64),device_id:'SCALE-12',capture_id:state.weigh.request_id,load_operation_id:load,store_address:'Магазин №12',gross_weight_kg:'12',received_at:'2026-10-15T10:00:00+00:00'};
  else if(url.pathname==='/api/delivery/store-photos/list')data=['FRONT','LEFT','RIGHT'].map((view,i)=>({photo_id:String(i+1).repeat(64),sha256:String(i+1).repeat(64),view,recorded_at:'2026-10-15T10:00:00+00:00'}));
  else if(url.pathname.startsWith('/api/help/articles/')&&state.helpStatus)return route.fulfill({status:state.helpStatus,json:{detail:'Access denied'}});
  else if(url.pathname.startsWith('/api/help/articles/')&&state.helpOffline)return route.abort('failed');
  else if(url.pathname.startsWith('/api/help/articles/'))data={article_id:url.pathname.split('/').pop(),title:'Серверная инструкция',summary:'Из вики',body:'Текущая инструкция сервера',revision:'7',related:[]};
  else return route.fulfill({status:404,json:{detail:'Unknown test route '+url.pathname}});
  return route.fulfill({status:200,json:data});
 });
 async function login(){await page.locator('input[autocomplete="username"]').fill('receiver');await page.locator('input[type="password"]').fill('test-only');await page.getByRole('button',{name:'Войти',exact:true}).click();await page.locator('.store-app-list-item,.store-app-stepper,.store-app-receipt-act').first().waitFor();}
 async function open(){await page.locator('.store-app-list-item').first().click();await page.getByRole('heading',{name:'Приёмка',exact:true}).waitFor();}
 async function ready(){await page.getByLabel('Идентификатор паллеты или места',{exact:true}).fill('PALLET-1');await page.getByLabel('Место перед камерами наблюдения',{exact:true}).check();await page.getByRole('button',{name:'Продолжить',exact:true}).click();}
 async function next(){await page.getByRole('button',{name:'Продолжить',exact:true}).click();}
 await page.goto(base);await login();return{context,page,state,posts,errors,login,open,ready,next};
}


(async()=>{const browser=await chromium.launch({headless:true}),checks=[];try{
 for(const status of [401,403,404]){
  const t=await setup(browser);t.state.helpStatus=status;
  await t.page.locator('button.store-app-help-hint').first().click();
  const panel=t.page.getByRole('dialog',{name:'Справка'});await panel.getByText('Статья недоступна для текущей учётной записи.',{exact:false}).waitFor();
  assert.equal(await panel.getByText('Из вики',{exact:true}).count(),0);
  assert.equal(await panel.locator('nav[aria-label="Связанные статьи"]').count(),0);
  checks.push('http_'+status+'_does_not_expose_bundled_or_published_body');assert.deepEqual(t.errors,[]);await t.context.close();
 }
 let t=await setup(browser);await t.page.locator('button.store-app-help-hint').first().click();
 await t.page.getByRole('dialog',{name:'Справка'}).getByText('Текущая инструкция сервера',{exact:true}).waitFor();checks.push('published_article_used');await t.context.close();
 t=await setup(browser);t.state.helpOffline=true;await t.page.locator('button.store-app-help-hint').first().click();
 const panel=t.page.getByRole('dialog',{name:'Справка'});await panel.getByText('Встроенная копия этой версии приложения; актуальность не подтверждена.',{exact:false}).waitFor();
 assert.equal(await panel.locator('nav[aria-label="Связанные статьи"]').count(),1);checks.push('network_failure_uses_explicit_public_bundle');assert.deepEqual(t.errors,[]);await t.context.close();
 const report={status:'PASS',checks,apiWrites:'INTERCEPTED_ONLY'};fs.writeFileSync(path.join(__dirname,'help-access-ui.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});