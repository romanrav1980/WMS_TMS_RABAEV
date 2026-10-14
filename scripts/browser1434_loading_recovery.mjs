import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const b=await chromium.launch({headless:true});
try {
 const p=await b.newPage({viewport:{width:1250,height:950}}), errors=[],posts=[];
 p.on('pageerror',e=>errors.push(e.message));
 await p.goto('http://127.0.0.1:8088/wms-admin/transport-loading.html?trip_id=33571');
 const live=p.waitForResponse(r=>r.url().includes('/33571/status'));
 await p.locator('#adminLoginForm button[type=submit]').click();
 if((await live).status()!==200)throw Error('Live trip failed');
 const key=await p.evaluate(()=> 'wms-physical-load:'+window.wmsAdminAuth.state.apiBase.replace(/\/$/,'')+':'+window.wmsAdminAuth.state.user.username);
 const saved={body:{operation_id:'TEST1433.DEPART'},path:'/api/transport/loading/33571/depart',trip_id:33571};
 let mode='wrong';
 await p.route('**/api/transport/loading/33571/depart',r=>{posts.push(r.request().postData());return r.fulfill({status:mode==='lost'?503:200,contentType:'application/json',body:JSON.stringify(mode==='lost'?{detail:'lost response'}:{operation_id:mode==='wrong'?'OTHER':saved.body.operation_id})});});
 await p.evaluate(({key,saved})=>localStorage.setItem(key,JSON.stringify(saved)),{key,saved});await p.reload();
 await p.locator('#loadRetry').click();await p.locator('#loadStatus').filter({hasText:'Ответ не подтверждает'}).waitFor();
 if(!await p.evaluate(key=>localStorage.getItem(key),key))throw Error('Wrong result cleared intent');
 mode='lost';await p.locator('#loadRetry').click();await p.locator('#loadStatus').filter({hasText:'Повтор сохраняет'}).waitFor();
 await p.reload();mode='ok';await p.locator('#loadRetry').click();await p.locator('#loadStatus').filter({hasText:'Подтверждено.'}).waitFor();
 if(await p.evaluate(key=>localStorage.getItem(key),key)!==null||new Set(posts).size!==1)throw Error('Replay changed command');
 await p.evaluate(key=>localStorage.setItem(key,'{damaged'),key);await p.reload();
 await p.locator('#loadArchive').waitFor();if(!await p.locator('#loadConfirm').isDisabled())throw Error('Damaged intent permits loading');
 await p.locator('#loadArchive').click();await p.locator('#loadStatus').filter({hasText:'Исходный текст сохранён'}).waitFor();
 const archived=await p.evaluate(key=>Object.keys(localStorage).some(k=>k.startsWith(key+':damaged:')&&localStorage.getItem(k)==='{damaged'),key);
 if(!archived)throw Error('Archive lost');
 await p.locator('main').screenshot({path:'reports/nicora/2026-10-13/screenshots/111-ni052-loading-recovery.png'});
 if(errors.length)throw Error(JSON.stringify(errors));
 console.log(JSON.stringify({realStatus:200,modeledPosts:posts.length,realWrites:0,exactReplay:true,wrongResultRetained:true,damagedArchived:archived,errors}));
 fs.writeFileSync('tmp/result1434.json',JSON.stringify({realStatus:200,modeledPosts:posts.length,realWrites:0,exactReplay:true,damagedArchived:archived,errors},null,2));
} finally {await b.close();}


