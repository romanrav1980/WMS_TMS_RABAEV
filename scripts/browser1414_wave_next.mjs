import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const b=await chromium.launch({headless:true});
try{
 const p=await b.newPage({viewport:{width:1400,height:1050}}),writes=[],errors=[];
 p.on('pageerror',e=>errors.push(e.message));p.on('request',r=>{if(r.method()==='POST'&&r.url().includes('/api/'))writes.push(r.url());});
 await p.goto('http://127.0.0.1:8088/wms-admin/wave-replenishment.html?wave_id=560#waveExecution');await p.locator('#adminLoginForm button[type=submit]').click();
 const link=p.locator('#waveExecution a[href="case-pick-tsd.html?case_task_id=1134"]');await link.waitFor();
 await p.locator('#waveExecution').screenshot({path:'reports/retailcase/2026-10-13/screenshots/108-ni033-wave-picking-next.png'});
 const response=p.waitForResponse(r=>r.url().endsWith('/case-pick/tasks/1134'));await link.click();const task=await (await response).json();
 await p.locator('#cpTsdTaskId').filter({hasText:'1134'}).waitFor();
 if(task.case_pick_task_id!==1134)throw Error('Wrong case');
 // Recovery READY link: synthetic response, existing real task as target, no mutations.
 await p.route('**/api/inventory/recovery-shorts?limit=50',r=>r.fulfill({status:200,contentType:'application/json',body:JSON.stringify([{short_id:1414,case_pick_task_id:1134,recovery_state:'READY',cell:'TEST',article:'TEST',remaining_seconds:90,order_remaining_quantity:'2',restored_quantity:'1'}])}));
 await p.goto('http://127.0.0.1:8088/wms-admin/case-pick-management.html');
 const recovery=p.getByRole('link',{name:'Продолжить сборку #1134',exact:true});await recovery.waitFor();
 if(await recovery.getAttribute('href')!=='case-pick-tsd.html?case_task_id=1134')throw Error('Wrong continuation');
 if(writes.length||errors.length)throw Error(JSON.stringify({writes,errors}));
 fs.writeFileSync('tmp/result1414.json',JSON.stringify({wave:560,caseTask:task.case_pick_task_id,status:task.status,recoveryLinkSynthetic:true,writes,errors},null,2));console.log(JSON.stringify({wave:560,caseTask:task.case_pick_task_id,status:task.status,writes,errors}));
}finally{await b.close();}
