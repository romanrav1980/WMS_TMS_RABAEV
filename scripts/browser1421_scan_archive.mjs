import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const b=await chromium.launch({headless:true});try{
 const p=await b.newPage(),writes=[],errors=[];p.on('pageerror',e=>errors.push(e.message));p.on('request',r=>{if(r.method()==='POST'&&r.url().includes('/api/'))writes.push(r.url());});
 await p.goto('http://127.0.0.1:8088/wms-admin/warehouse-tasks.html?task_id=564#warehouseTaskScanPanel');await p.locator('#adminLoginForm button[type=submit]').click();await p.locator('#warehouseTaskSelectionText').filter({hasText:'Выбрано задание 564'}).waitFor();
 const key=await p.evaluate(()=>{const a=window.wmsAdminAuth;const key='wms.task.scans:'+a.state.apiBase+':'+a.state.user.username+':564';localStorage.setItem(key,'{damaged1421');return key;});
 await p.locator('#warehouseTaskScanPanel [data-action=load]').click();
 const archive=p.locator('#warehouseTaskScanPanel [data-action=archive]');await archive.waitFor();await archive.click();await p.locator('#warehouseTaskScanPanel p').filter({hasText:'Показан текущий серверный набор'}).waitFor();
 const preserved=await p.evaluate(k=>localStorage.getItem(k)===null&&Object.keys(localStorage).some(x=>x.startsWith(k+':damaged:')&&localStorage.getItem(x)==='{damaged1421'),key);
 if(!preserved||writes.length||errors.length)throw Error(JSON.stringify({preserved,writes,errors}));
 fs.writeFileSync('tmp/result1421.json',JSON.stringify({preserved,writes,errors},null,2));console.log(JSON.stringify({preserved,writes,errors}));
}finally{await b.close();}

