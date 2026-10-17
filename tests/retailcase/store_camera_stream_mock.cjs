// Actual getUserMedia/video-frame/ZXing path with Chromium software camera only.
// Every app network request is fulfilled locally; no physical camera or API effect.
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const {QRCodeWriter,BarcodeFormat}=require('../../terminal/wms_terminal_web/node_modules/@zxing/library');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../..'),dist=path.join(root,'terminal/wms_terminal_web/dist');
const FORMAT=(process.argv[2]||'QR').toUpperCase(),codes={QR:'PALLET-1',CODE128:'090000000000010017',EAN13:'4006381333931',GS1128:'00090000000000010017'};
assert(Object.hasOwn(codes,FORMAT),'Use QR, CODE128, EAN13 or GS1128');
const RUN=process.argv[3]||'';assert(['','messages'].includes(RUN));
const out=path.join(root,'reports/retailcase/2026-10-15',FORMAT==='QR'?'store-camera-stream':'store-camera-formats/'+FORMAT.toLowerCase()+(RUN?'-'+RUN:''));
const CODE=codes[FORMAT],LOAD='CAMERA.QA.LOAD',ORIGIN='http://127.0.0.1:3010';
const ROOT_CODE=FORMAT==='GS1128'?'090000000000010017':CODE;
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function videoFile(name,code){const width=640,height=480,y=Buffer.alloc(width*height,235),uv=Buffer.alloc(width*height/2,128);
 let encoder=null;
 if(code&&FORMAT==='QR'){const matrix=new QRCodeWriter().encode(code,BarcodeFormat.QR_CODE,384,384,new Map());for(let row=0;row<384;row++)for(let col=0;col<384;col++)y[(row+48)*width+col+128]=matrix.get(col,row)?16:235;}
 else if(code){encoder=JSON.parse(require('node:child_process').execFileSync('python',[path.join(__dirname,'barcode_camera_fixture.py'),FORMAT,code],{encoding:'utf8'}));
  const scale=Math.floor(576/encoder.width),left=Math.floor((width-encoder.width*scale)/2),top=120;
  assert(scale>=2&&encoder.height*3<=240);
  for(const[x,bottom,w,h]of encoder.bars)for(let row=top+Math.floor((encoder.height-bottom-h)*3);row<top+Math.ceil((encoder.height-bottom)*3);row++)for(let col=left+Math.floor(x*scale);col<left+Math.ceil((x+w)*scale);col++)y[row*width+col]=16;
 }
 const frame=Buffer.concat([Buffer.from('FRAME\n'),y,uv]),bytes=Buffer.concat([Buffer.from('YUV4MPEG2 W640 H480 F10:1 Ip A1:1 C420\n'),frame,frame,frame]);
 const file=path.join(out,name);fs.writeFileSync(file,bytes);return{file,sha256:sha(bytes),bytes:bytes.length,encoder};}
async function run(video,width,decode){const browser=await chromium.launch({headless:true,args:['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream','--use-file-for-fake-video-capture='+video.file]});
try{const ctx=await browser.newContext({viewport:{width,height:844},serviceWorkers:'block'}),page=await ctx.newPage(),errors=[],unexpected=[],requests=[],mockPosts=[];
 await ctx.addInitScript(()=>{window.cameraProof={streams:[],constraints:[],frames:[]};const actual=navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
 document.addEventListener('loadeddata',event=>{const v=event.target;if(v instanceof HTMLVideoElement)window.cameraProof.frames.push({width:v.videoWidth,height:v.videoHeight,readyState:v.readyState});},true);
 navigator.mediaDevices.getUserMedia=async constraints=>{const stream=await actual(constraints);window.cameraProof.streams.push(stream);window.cameraProof.constraints.push(constraints);return stream;};});
 page.on('pageerror',error=>errors.push(String(error)));
 await ctx.route('**/*',async route=>{const req=route.request(),url=new URL(req.url()),p=url.pathname;
 if(!p.startsWith('/api/')){const file=path.join(dist,p.endsWith('/')?p+'index.html':p);if(!file.startsWith(dist)||!fs.existsSync(file)){unexpected.push(p);return route.fulfill({status:404,body:'missing'});}return route.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.svg':'image/svg+xml'})[path.extname(file)]||'application/octet-stream'});}
 requests.push({method:req.method(),path:p,code:url.searchParams.get('code')});let data;
 if(FORMAT==='GS1128'&&req.method()==='POST'&&p==='/api/delivery/store-receipts/confirm'){mockPosts.push(req.postData());return route.fulfill({status:503,json:{detail:{code:'TEST_OUTCOME_UNCERTAIN',outcome_confirmed:false,retry_same_operation_id:true}}});}
 if(p==='/api/store-app/session')data={username:'receiver',display_name:'QA receiver',access_revision:1,stores:[{store_id:'QA',address:'QA store',receipt_mode:'BARCODE',policy_version:1}],limit:200,has_more:false,auth_scope:'STORE_RECEIPT'};
 else if(p==='/api/store-app/deliveries')data={store_id:'QA',items:[{load_operation_id:LOAD,trip_id:1,root_key:ROOT_CODE,gross_weight_kg:1,departed_at:'2026-10-15T12:00:00Z',time_status:'UTC'}],next_after:null,limit:50};
 else if(p==='/api/store-app/deliveries/lookup')data={store_id:'QA',load_operation_id:LOAD,scanned_code:url.searchParams.get('code')};
 else if(p.startsWith('/api/store-app/deliveries/'))data={load_operation_id:LOAD,store_address:'QA store',root:ROOT_CODE,root_scan_identifier:ROOT_CODE,composition_signature:'A'.repeat(64),mode:'BARCODE',shipping_gross_weight_kg:'1',shipping_weight_tolerance_kg:'0',requires_marked_recipient_flow:false,already_received:false,snapshot:{nodes:[]}};
 else{unexpected.push(p);return route.fulfill({status:404,json:{detail:'unmocked'}});}return route.fulfill({status:200,json:data});});
 await page.goto(ORIGIN+'/store/');await page.locator('input[autocomplete="username"]').fill('receiver');await page.locator('input[type="password"]').fill('TEST');await page.getByRole('button',{name:'Войти',exact:true}).click();
 await page.getByRole('button',{name:'Сканировать поставку',exact:true}).click();assert.equal(await page.getByLabel('Идентификатор паллеты или места',{exact:true}).inputValue(),'');await page.getByRole('button',{name:'Камера',exact:true}).click();
 await page.waitForFunction(()=>window.cameraProof.streams.length===1);
 if(decode){await page.getByLabel('Идентификатор паллеты или места',{exact:true}).filter({visible:true}).waitFor();await page.waitForFunction(code=>Array.from(document.querySelectorAll('input')).some(x=>x.value===code),CODE);
  assert.equal(await page.getByRole('dialog',{name:'Сканирование кода',exact:true}).count(),0);assert.equal(await page.getByLabel('Идентификатор паллеты или места',{exact:true}).inputValue(),CODE);
  await page.getByRole('button',{name:'Открыть поставку',exact:true}).click();await page.getByRole('heading',{name:'Приёмка',exact:true}).waitFor();assert.ok(requests.some(r=>r.path.endsWith('/lookup')&&r.code===CODE));
  if(FORMAT==='GS1128'){
   const input=page.getByLabel('Идентификатор паллеты или места',{exact:true});assert.equal(await input.inputValue(),CODE);
   await page.getByRole('checkbox',{name:'Место перед камерами наблюдения',exact:true}).check();
   const next=page.getByRole('button',{name:'Продолжить',exact:true});assert(await next.isEnabled(),'GS1 AI00 must match current SSCC');
   await input.fill('OTHER');assert(!(await next.isEnabled()));await input.fill(CODE);assert(await next.isEnabled());
   await next.click();await page.getByRole('button',{name:'Продолжить',exact:true}).click();
   await page.getByRole('button',{name:'Подтвердить приёмку',exact:true}).click();
   const retry=page.locator('[data-help-id="receipt.retry"]');await retry.waitFor();
   await page.waitForFunction(()=>!document.querySelector('[data-help-id="receipt.retry"]')?.disabled);
   assert.equal(mockPosts.length,1);assert.equal(JSON.parse(mockPosts[0]).scan_place,ROOT_CODE);
   await retry.click();await page.waitForFunction(()=>!document.querySelector('[data-help-id="receipt.retry"]')?.disabled);
   assert.equal(mockPosts.length,2);assert.equal(mockPosts[1],mockPosts[0],'Retry must preserve original frozen bytes/operation');
   if(RUN==='messages'){const text=await page.locator('.store-app-recovery').innerText();assert(!/Error:|\/api\/|HTTP\s*\d{3}/.test(text));assert(text.includes('Повторите сохранённую операцию.'));}
  }
 }else{await page.waitForFunction(()=>{const v=document.querySelector('video');return v&&v.readyState>=2&&v.videoWidth>0;});await page.screenshot({path:path.join(out,`camera-open-${width}.png`)});await page.getByRole('dialog',{name:'Сканирование кода',exact:true}).getByRole('button',{name:'Закрыть',exact:true}).click();}
 await page.waitForFunction(()=>window.cameraProof.streams.every(s=>s.getTracks().every(t=>t.readyState==='ended')));
 const proof=await page.evaluate(()=>({calls:window.cameraProof.streams.length,constraints:window.cameraProof.constraints,frames:window.cameraProof.frames,tracks:window.cameraProof.streams.flatMap(s=>s.getTracks().map(t=>({kind:t.kind,state:t.readyState,settings:t.getSettings()})))}));
 assert.ok(proof.frames.some(f=>f.width===640&&f.height===480&&f.readyState>=2));
 assert.equal(proof.calls,1);assert.ok(proof.tracks.length>0);assert.ok(proof.tracks.every(t=>t.kind==='video'&&t.state==='ended'));assert.ok(requests.every(r=>r.method==='GET'||(FORMAT==='GS1128'&&r.path==='/api/delivery/store-receipts/confirm')));assert.deepEqual(errors,[]);assert.deepEqual(unexpected,[]);
 await page.screenshot({path:path.join(out,`camera-result-${width}.png`),fullPage:true});await ctx.close();return{width,status:'PASS',case:decode?`native_mediaStream_video_frame_ZXing_${FORMAT}_accept_lookup_and_stop`:'blank_live_video_manual_close_stops_tracks',proof,requests,mocked_receipt_posts:mockPosts.length,exact_frozen_retry:FORMAT==='GS1128'};
}finally{await browser.close();}}
(async()=>{fs.mkdirSync(out,{recursive:true});assert(!fs.existsSync(path.join(out,'camera-stream-mock.json')),'Preserve existing accepted evidence');
 const video=videoFile(FORMAT.toLowerCase()+'-software-camera.y4m',CODE),blank=FORMAT==='QR'?videoFile('blank-software-camera.y4m',null):null,results=[];
 results.push(await run(video,390,true));if(blank){results.push(await run(blank,360,false));results.push(await run(blank,1440,false));}
 const entry=fs.readFileSync(path.join(dist,'store/index.html'),'utf8'),assets=[...entry.matchAll(/(?:src|href)="([^\"]+\.(?:js|css))"/g)].map(m=>({file:m[1],sha256:sha(fs.readFileSync(path.join(dist,m[1])))}));
 fs.writeFileSync(path.join(out,'camera-stream-mock.json'),JSON.stringify({status:'PASS',kind:'CHROMIUM_FAKE_VIDEO_REAL_GET_USER_MEDIA_AND_ZXING',format:FORMAT,physical_camera:false,physical_hardware:false,actual_api_calls:0,actual_business_writes:0,all_network_intercepted:true,code:CODE,video,blank,assets,results},null,2));console.log(results.map(r=>({width:r.width,case:r.case,status:r.status})));
})().catch(e=>{console.error(e);process.exitCode=1;});
