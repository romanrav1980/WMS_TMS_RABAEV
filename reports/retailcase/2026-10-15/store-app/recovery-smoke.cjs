const {chromium}=require('../../../../admin/wms_admin_frontend/node_modules/playwright');
const fs=require('fs'),path=require('path'),assert=require('assert');
const base=process.env.STORE_UI_URL||'http://127.0.0.1:3010/store/';
const signature='A'.repeat(64),load='TEST.LOAD:1',store='test-store';
const result=op=>({operation_id:op,load_operation_id:load,store_address:'Магазин проверки',root:'PALLET-1',status:'ACCEPTED',accepted_lines:[{line_no:1,lot_uid:'LOT1',article:'ART1',base_uom:'EA',accepted:'10'}]});
const preview=mode=>({load_operation_id:load,store_address:'Магазин проверки',root:'PALLET-1',root_scan_identifier:'PALLET-1',composition_signature:signature,mode,shipping_gross_weight_kg:'12',shipping_weight_tolerance_kg:'0.5',requires_marked_recipient_flow:false,already_received:false,snapshot:{nodes:[{uid:'LOT1',kind:'STOCK',article:'ART1',quantity:'10',base_uom:'EA'}]}});
async function setup(browser,mode='BARCODE'){
 const context=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'block'}),page=await context.newPage(),posts=[],errors=[];
 const state={mode,completed:false,unknown:true,statusVisible:false,hold:null};
 page.on('pageerror',error=>errors.push(String(error)));
 await page.route('**/api/**',async route=>{
  const req=route.request(),url=new URL(req.url());let data;
  if(url.pathname==='/api/store-app/session')data={username:'receiver',display_name:'Receiver',access_revision:1,stores:[{store_id:store,address:'Магазин проверки',receipt_mode:state.mode,policy_version:1}],limit:200,has_more:false,auth_scope:'STORE_RECEIPT'};
  else if(url.pathname==='/api/store-app/deliveries'){
   if(state.hold){await state.hold;state.hold=null;}
   data={store_id:store,items:[{load_operation_id:load,trip_id:1,root_key:'PALLET-1',gross_weight_kg:12,departed_at:'2026-10-15T10:00:00',time_status:'UNRESOLVED_SERVER_LOCAL'}],next_after:null,limit:50};
  }else if(url.pathname.startsWith('/api/store-app/deliveries/'))data={...preview(state.mode),...(state.completed?{already_received:true,receipt:{operation_id:'SAVED:1',state:'APPLIED',result:result('SAVED:1')}}:{})};
  else if(url.pathname.startsWith('/api/store-app/receipts/')){const op=decodeURIComponent(url.pathname.split('/').pop());data={operation_id:op,state:state.statusVisible?'APPLIED':'NOT_VISIBLE',outcome_confirmed:state.statusVisible,result:state.statusVisible?result(op):null};}
  else if(url.pathname==='/api/delivery/store-receipts/confirm'){
   posts.push(req.postData());
   if(state.unknown)return route.abort('failed');
   data=result(JSON.parse(req.postData()).operation_id);
  }else if(url.pathname.startsWith('/api/help/articles/'))data={article_id:url.pathname.split('/').pop(),title:'Серверная инструкция',summary:'Из вики',body:'Текущая инструкция сервера',revision:'7',related:[]};
  else if(url.pathname==='/api/delivery/store-scales/captures')data={items:[{capture_key:'B'.repeat(64),device_id:'Scale1',gross_weight_kg:'12',received_at:'2026-10-15T10:00:00+00:00'}]};
  else if(url.pathname==='/api/delivery/store-photos/list')data=['FRONT','LEFT','RIGHT'].map((view,i)=>({photo_id:String(i+1).repeat(64),sha256:String(i+1).repeat(64),view,recorded_at:'2026-10-15T10:00:00+00:00'}));
  else return route.fulfill({status:500,json:{detail:'Unexpected test request '+url.pathname}});
  return route.fulfill({status:200,json:data});
 });
 async function login(){await page.locator('input[autocomplete="username"]').fill('receiver');await page.locator('input[type="password"]').fill('test-only');await page.getByRole('button',{name:'Войти',exact:true}).click();await page.locator('.store-app-list-item').first().waitFor();}
 async function open(){await page.locator('.store-app-list-item').first().click();await page.locator('.store-app-snapshot li,.store-app-receipt-act tbody tr').first().waitFor();}
 async function ready(){await page.locator('input[autocomplete=off]').first().fill('PALLET-1');await page.getByLabel('Место установлено перед камерами наблюдения').check();}
 await page.goto(base);await login();return{context,page,state,posts,errors,login,open,ready};
}
(async()=>{const browser=await chromium.launch({headless:true}),checks=[];try{
 let t=await setup(browser);await t.open();await t.ready();
 await t.page.getByRole('button',{name:'Подтвердить полную приёмку',exact:true}).click();
 await t.page.getByRole('button',{name:'Повторить сохранённую операцию',exact:true}).waitFor();assert.equal(t.posts.length,1);
 const original=t.posts[0];await t.page.reload();await t.login();await t.open();
 await t.page.getByRole('button',{name:'Проверить результат',exact:true}).click();
 await t.page.getByText(/Квитанция не видна/).waitFor();assert.equal(t.posts.length,1);
 await t.page.getByRole('button',{name:'Повторить сохранённую операцию',exact:true}).click();
 await t.page.getByText(/Повторите сохранённую операцию/).first().waitFor();assert.equal(t.posts.length,2);assert.equal(t.posts[1],original);
 t.state.statusVisible=true;await t.page.getByRole('button',{name:'Проверить результат',exact:true}).click();await t.page.getByRole('heading',{name:/^Приёмка подтверждена/}).waitFor();assert.equal(t.posts.length,2);
 assert.deepEqual(t.errors,[]);checks.push('lost_response_reload_unknown_status_exact_body_retry_and_confirmed_receipt');await t.context.close();
 t=await setup(browser);t.state.completed=true;await t.open();await t.page.getByRole('heading',{name:/^Приёмка подтверждена/}).waitFor();assert.equal(await t.page.getByRole('button',{name:/^Подтвердить/}).count(),0);assert.equal(t.posts.length,0);checks.push('completed_delivery_original_receipt_no_mutation_form');await t.context.close();
 t=await setup(browser,'PAPER_COUNT');await t.open();await t.ready();
 const submit=t.page.getByRole('button',{name:'Подтвердить фактическую приёмку',exact:true});assert(await submit.isDisabled());
 const accepted=t.page.locator('.store-app-discrepancy-row').first().getByLabel('Принято',{exact:true});assert.equal(await accepted.inputValue(),'');
 await t.page.locator('input[maxlength="100"]').last().fill('Накладная 1');assert(await submit.isDisabled());await accepted.fill('10');assert(await submit.isEnabled());
 await submit.click();await t.page.getByRole('button',{name:'Повторить сохранённую операцию',exact:true}).waitFor();const body=JSON.parse(t.posts[0]);assert.equal(body.paper_reference,'Накладная 1');assert.equal(body.observations[0].accepted,'10');checks.push('paper_count_requires_operator_actual_count_and_reference');await t.context.close();
 t=await setup(browser,'WEIGHT_PHOTO');await t.open();await t.ready();
 const weightSubmit=t.page.getByRole('button',{name:'Подтвердить полную приёмку',exact:true});assert(await weightSubmit.isDisabled());
 await t.page.getByRole('button',{name:'Показать измерения склада'}).click();await t.page.getByRole('radio').first().check();assert(await weightSubmit.isDisabled());
 await t.page.getByRole('button',{name:'Показать фотоархив'}).click();await t.page.getByText('Фотографий для подтверждения: 3').waitFor();assert(await weightSubmit.isEnabled());checks.push('weight_mode_requires_real_capture_and_three_distinct_photos');assert.deepEqual(t.errors,[]);await t.context.close();
 t=await setup(browser);await t.page.evaluate(({store,load})=>localStorage.setItem('store-app-unloading:'+location.origin+':receiver:'+load+':Магазин проверки','{broken'),{store,load});await t.open();await t.ready();assert(await t.page.getByRole('button',{name:'Подтвердить полную приёмку',exact:true}).isDisabled());await t.page.getByRole('button',{name:'Восстановить состояние выгрузки'}).waitFor();assert.equal(t.posts.length,0);checks.push('corrupt_unloading_journal_blocks_receipt');await t.context.close();
 t=await setup(browser);await t.page.getByRole('button',{name:/Справка:/}).first().click();await t.page.getByText('Текущая инструкция сервера',{exact:true}).waitFor();await t.page.getByRole('button',{name:'Закрыть справку'}).click();
 let release;t.state.hold=new Promise(resolve=>release=resolve);await t.page.getByRole('button',{name:'Обновить список'}).click();await t.page.getByRole('button',{name:'Выйти',exact:true}).click();release();await t.page.getByRole('button',{name:'Войти',exact:true}).waitFor();assert.equal(await t.page.locator('.store-app-list-item').count(),0);checks.push('published_help_and_logout_clear_late_delivery_response');await t.context.close();
 const output={status:'PASS',checks,browserWrites:'INTERCEPTED_ONLY',physicalDeviceTested:false};fs.writeFileSync(path.join(__dirname,'recovery-ui.json'),JSON.stringify(output,null,2));console.log(JSON.stringify(output));
}finally{await browser.close();}})().catch(error=>{console.error(error);process.exitCode=1;});
