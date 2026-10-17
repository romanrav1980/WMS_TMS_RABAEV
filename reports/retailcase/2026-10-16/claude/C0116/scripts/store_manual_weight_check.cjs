const {chromium}=require('C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright');
const {QRCodeWriter,BarcodeFormat}=require('C:/projects/TMS/terminal/wms_terminal_web/node_modules/@zxing/library');
const fs=require('fs'),path=require('path'),assert=require('assert');
const base=process.env.STORE_UI_URL||'http://127.0.0.1:3010/store/';
const signature='A'.repeat(64),load='TEST.LOAD:1',store='test-store';
const weightOf=body=>body&&body.manual_weight_kg?{capture_key:null,device_id:null,device_policy_version:null,measurement_origin:'MANUAL_CONFIRMED',recorded_by:'receiver',shipping_gross_kg:'12',observed_gross_kg:body.manual_weight_kg,tolerance_kg:'0.5',delta_kg:'0.45',in_tolerance:1,act_confirmed:0,photos:[]}:body&&body.scale_capture_key?{capture_key:body.scale_capture_key,device_id:'SCALE-12',device_policy_version:1,measurement_origin:'SCALE_CAPTURE',recorded_by:'receiver',shipping_gross_kg:'12',observed_gross_kg:'12',tolerance_kg:'0.5',delta_kg:'0',in_tolerance:1,act_confirmed:0,photos:[]}:undefined;
let lastBody=null;
const receipt=op=>({weight:weightOf(lastBody),operation_id:op,load_operation_id:load,store_address:'Магазин №12',root:'PALLET-1',status:'ACCEPTED',accepted_lines:[{line_no:1,lot_uid:'LOT1',article:'ART1',base_uom:'EA',accepted:'10'}]});
const preview=mode=>({load_operation_id:load,store_address:'Магазин №12',root:'PALLET-1',root_scan_identifier:'PALLET-1',composition_signature:signature,mode,shipping_gross_weight_kg:'12',shipping_weight_tolerance_kg:'0.5',requires_marked_recipient_flow:false,already_received:false,snapshot:{nodes:[{uid:'LOT1',kind:'STOCK',article:'ART1',quantity:'10',base_uom:'EA'}]}});
async function setup(browser,mode='BARCODE',width=390){
 const context=await browser.newContext({viewport:{width,height:844},serviceWorkers:'block'}),page=await context.newPage(),posts=[],allWrites=[],errors=[];
 const state={mode,completed:false,unknown:true,statusVisible:false,weigh:null,weighReady:false};
 page.on('pageerror',error=>errors.push(String(error)));page.on('console',msg=>{if(msg.type()==='error'&&/Maximum update depth|Too many re-renders/.test(msg.text()))errors.push(msg.text());});
 await page.route('**/api/**',async route=>{
  const req=route.request(),url=new URL(req.url());if(!['GET','HEAD','OPTIONS'].includes(req.method()))allWrites.push({method:req.method(),path:url.pathname});let data;
  if(url.pathname==='/api/store-app/session')data={username:'receiver',display_name:'Receiver',access_revision:1,stores:[{store_id:store,address:'Магазин №12',receipt_mode:state.mode,policy_version:1}],limit:200,has_more:false,auth_scope:'STORE_RECEIPT'};
  else if(url.pathname==='/api/store-app/deliveries')data={store_id:store,items:[{load_operation_id:load,trip_id:3521,root_key:'PALLET-1',gross_weight_kg:12,departed_at:'2026-10-15T10:25:54.957001',time_status:'UNRESOLVED_SERVER_LOCAL'},{load_operation_id:'SAVED.LOAD',trip_id:3520,root_key:'PALLET-2',gross_weight_kg:8,departed_at:'2026-10-15T09:12:00.123456',time_status:'UNRESOLVED_SERVER_LOCAL',receipt_operation_id:'SAVED:1',receipt_state:'ACCEPTED'}],next_after:null,limit:50};
  else if(url.pathname==='/api/store-app/deliveries/lookup')data={store_id:store,load_operation_id:load,scanned_code:url.searchParams.get('code')};
  else if(url.pathname.startsWith('/api/store-app/deliveries/'))data={...preview(state.mode),...(state.marked?{requires_marked_recipient_flow:true,marked_partial_control:false,marked_unit_control:{supported:true,expected_scan_count:1,physical_unit_count:1,profiles:[{system_code:'CRPT',profile_code:'UNIT',profile_version:'1',scan_mode:'UNIT'}],units:[]}}:{}),...(state.completed?{already_received:true,receipt:{operation_id:'SAVED:1',state:'APPLIED',result:receipt('SAVED:1')}}:{})};
  else if(url.pathname.startsWith('/api/store-app/receipts/')){const op=decodeURIComponent(url.pathname.split('/').pop());data={operation_id:op,state:state.statusVisible?'APPLIED':'NOT_VISIBLE',outcome_confirmed:state.statusVisible,result:state.statusVisible?receipt(op):null};}
  else if(url.pathname==='/api/delivery/store-receipts/confirm'){posts.push(req.postData());lastBody=JSON.parse(req.postData());if(state.unknown)return route.abort('failed');data=receipt(JSON.parse(req.postData()).operation_id);}
  else if(url.pathname==='/api/delivery/store-scales/devices')data={items:[{device_id:'SCALE-12',device_policy_version:1,active:true,capacity_kg:'1500',resolution_kg:'0.1',calibration_ref:'CAL1',calibrated_until:'2027-01-01T00:00:00+00:00',readiness:'READY',connectivity:'UNKNOWN'}]};
  else if(url.pathname==='/api/delivery/store-scales/requests'){state.weigh=JSON.parse(req.postData());if(state.weighReject)return route.fulfill({status:409,json:{detail:{request_id:state.weigh.request_id,outcome_confirmed:true,code:'SCALE_REQUEST_REJECTED',message:'WEIGH_DEVICE_BUSY'}}});data={...state.weigh,state:'REQUESTED',capture_key:null,expires_at:'2026-10-15T20:00:00+00:00',reason:null};}
  else if(url.pathname.startsWith('/api/delivery/store-scales/requests/'))data={...state.weigh,state:state.weighReady?'CAPTURED':'REQUESTED',capture_key:state.weighReady?'B'.repeat(64):null,expires_at:'2026-10-15T20:00:00+00:00',reason:null};
  else if(url.pathname.startsWith('/api/delivery/store-scales/captures/'))data={capture_key:'B'.repeat(64),device_id:'SCALE-12',capture_id:state.weigh.request_id,load_operation_id:load,store_address:'Магазин №12',gross_weight_kg:'12',received_at:'2026-10-15T10:00:00+00:00'};
  else if(url.pathname==='/api/delivery/store-photos/list')data=['FRONT','LEFT','RIGHT'].map((view,i)=>({photo_id:String(i+1).repeat(64),sha256:String(i+1).repeat(64),view,recorded_at:'2026-10-15T10:00:00+00:00'}));
  else if(url.pathname.startsWith('/api/help/articles/'))data={article_id:url.pathname.split('/').pop(),title:'Серверная инструкция',summary:'Из вики',body:'Текущая инструкция сервера',revision:'7',related:[]};
  else return route.fulfill({status:404,json:{detail:'Unknown test route '+url.pathname}});
  return route.fulfill({status:200,json:data});
 });
 async function login(){await page.locator('input[autocomplete="username"]').fill('receiver');await page.locator('input[type="password"]').fill('test-only');await page.getByRole('button',{name:'Войти',exact:true}).click();await page.locator('.store-app-list-item,.store-app-stepper,.store-app-receipt-act').first().waitFor();}
 async function open(){await page.locator('.store-app-list-item').first().click();await page.getByRole('heading',{name:'Приёмка',exact:true}).waitFor();}
 async function ready(){await page.getByLabel('Идентификатор паллеты или места',{exact:true}).fill('PALLET-1');await page.getByLabel('Место перед камерами наблюдения',{exact:true}).check();await page.getByRole('button',{name:'Продолжить',exact:true}).click();}
 async function next(){await page.getByRole('button',{name:'Продолжить',exact:true}).click();}
 await page.goto(base);await login();return{context,page,state,posts,allWrites,errors,login,open,ready,next};
}

// C0116 UI fixtures (перехват /api в браузере, не native/hardware): ручной вес магазина и источник веса.
const OUT=path.join(__dirname,'..','screenshots');
const scroll=async page=>page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
(async()=>{const browser=await chromium.launch({headless:true}),checks=[],result={};try{
 // 1. По умолчанию — «Ввести вес»; продолжить можно только с корректным весом и фото.
 let t=await setup(browser,'WEIGHT_PHOTO',390);await t.open();await t.ready();
 const manualBtn=t.page.getByRole('radio',{name:'Ввести вес'}),scaleBtn=t.page.getByRole('radio',{name:'Электронные весы'});
 assert.equal(await manualBtn.getAttribute('aria-checked'),'true');assert.equal(await t.page.getByRole('button',{name:'Получить вес',exact:true}).count(),0);
 const next=t.page.getByRole('button',{name:'Продолжить',exact:true});
 const input=()=>t.page.getByLabel('Вес брутто по весам, кг');
 await t.page.waitForFunction(()=>/3\/3/.test(document.body.innerText));assert(await next.isDisabled());
 await input().fill('0');assert(await next.isDisabled());await input().fill('12,4,5');assert(await next.isDisabled());
 await input().fill('12,450');await t.page.getByText('Будет передано 12.450 кг',{exact:false}).waitFor();assert(!(await next.isDisabled()));
 result.manualHint=await t.page.locator('.store-app-manual [role=status]').innerText();
 assert.equal(await scroll(t.page),false);await t.page.screenshot({path:path.join(OUT,'s1_manual_weight_390.png'),fullPage:true});checks.push('manual_default_validation_390_no_overflow');
 // 2. Переключение источника очищает неотправленный выбор; весы — прежний API без массы в запросе.
 await scaleBtn.click();assert.equal(await input().count(),0);assert(await next.isDisabled());
 await t.page.getByRole('button',{name:'Получить вес',exact:true}).click();assert(t.state.weigh&&!('gross_weight_kg'in t.state.weigh));
 t.state.weighReady=true;await t.page.getByText('12 кг',{exact:true}).last().waitFor({timeout:10000});
 await t.page.waitForFunction(()=>{const b=[...document.querySelectorAll('footer button')].find(x=>x.textContent==='Продолжить');return b&&!b.disabled;},null,{timeout:10000});
 await manualBtn.click();await t.page.waitForFunction(()=>{const b=[...document.querySelectorAll('footer button')].find(x=>x.textContent==='Продолжить');return b&&b.disabled;},null,{timeout:3000});assert.equal(await input().inputValue(),'');checks.push('source_switch_clears_unsent_choice_both_directions');
 await input().fill('12.45');await next.click();
 result.summary=await t.page.locator('.store-app-step-content:not([hidden])').innerText();assert(result.summary.includes('введено пользователем'));
 // 3. Отправка: только manual_weight_kg; исход неизвестен (обрыв) — черновик заморожен, после reload точный повтор тех же байт.
 await t.page.getByRole('button',{name:'Подтвердить приёмку',exact:true}).click();await t.page.getByRole('button',{name:'Повторить сохранённую операцию',exact:true}).waitFor();
 const body=JSON.parse(t.posts[0]);result.body={manual_weight_kg:body.manual_weight_kg,has_scale_capture_key:'scale_capture_key' in body,photo_ids:(body.photo_ids||[]).length};
 assert.equal(body.manual_weight_kg,'12.45');assert(!('scale_capture_key' in body));
 result.sourceLockedWhilePending=await t.page.getByRole('radio',{name:'Электронные весы'}).isDisabled().catch(()=>'not-rendered');
 await t.page.reload();await t.login();
 await t.page.getByRole('button',{name:'Повторить сохранённую операцию',exact:true}).click();await t.page.waitForTimeout(700);
 assert.equal(t.posts[1],t.posts[0]);checks.push('pending_draft_exact_bytes_retry_after_reload');
 t.state.unknown=false;await t.page.getByRole('button',{name:'Повторить сохранённую операцию',exact:true}).click();
 await t.page.getByText('Приёмка подтверждена',{exact:false}).waitFor({timeout:10000});assert.equal(t.posts[2],t.posts[0]);
 result.act=await t.page.locator('.store-app-weight-outcome').innerText();assert(result.act.includes('введено пользователем'));
 await t.page.screenshot({path:path.join(OUT,'s2_act_manual_390.png'),fullPage:true});checks.push('act_shows_entered_by_user');
 // 4. Источник «весы»: тело только со scale_capture_key, акт — «получено от прибора».
 t=await setup(browser,'WEIGHT_PHOTO',1440);await t.open();await t.ready();t.state.unknown=false;
 await t.page.getByRole('radio',{name:'Электронные весы'}).click();await t.page.getByRole('button',{name:'Получить вес',exact:true}).click();t.state.weighReady=true;
 await t.page.getByText('12 кг',{exact:true}).last().waitFor({timeout:10000});await t.page.screenshot({path:path.join(OUT,'s3_scale_source_desktop.png'),fullPage:true});
 await t.page.waitForFunction(()=>{const b=[...document.querySelectorAll('footer button')].find(x=>x.textContent==='Продолжить');return b&&!b.disabled;},null,{timeout:10000});await t.next();
 await t.page.getByRole('button',{name:'Подтвердить приёмку',exact:true}).click();await t.page.getByText('Приёмка подтверждена',{exact:false}).waitFor({timeout:10000});
 const sbody=JSON.parse(t.posts[0]);assert.equal(sbody.scale_capture_key,'B'.repeat(64));assert(!('manual_weight_kg' in sbody));
 result.scaleAct=await t.page.locator('.store-app-weight-outcome').innerText();assert(result.scaleAct.includes('получено от прибора'));checks.push('scale_source_body_and_act');
 // 5. Desktop: ручной ввод и обычный help URL.
 t=await setup(browser,'WEIGHT_PHOTO',1440);await t.open();await t.ready();await t.page.getByLabel('Вес брутто по весам, кг').fill('11,9');
 await t.page.screenshot({path:path.join(OUT,'s4_manual_weight_desktop.png'),fullPage:true});
 result.helpLink=await t.page.locator('[data-help-id="weight.help"]').getAttribute('href');assert(/\/help\/manual-weight\.html#store$/.test(result.helpLink));
 result.errors=t.errors;assert.deepEqual(t.errors,[]);checks.push('desktop_help_url');
 const output={status:'PASS',fixtures:'UI_FIXTURES_INTERCEPTED_API_NOT_NATIVE_OR_HARDWARE',checks,result};
 fs.writeFileSync(path.join(__dirname,'..','store_manual_weight_result.json'),JSON.stringify(output,null,1));console.log(JSON.stringify(output,null,1));
}finally{await browser.close();}})().catch(error=>{console.error(error);process.exitCode=1;});
