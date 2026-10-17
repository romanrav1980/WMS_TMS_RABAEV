const {chromium}=require('../../../../admin/wms_admin_frontend/node_modules/playwright');
const fs=require('fs');const path=require('path');
(async()=>{
 const basic=fs.readFileSync('front.bat','utf8').match(/VITE_ADMIN_BASIC_AUTH=([^"\r\n]+)/)[1];
 const browser=await chromium.launch({headless:true});
 try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 const login=async()=>{const split=basic.indexOf(':');await page.getByLabel('Пользователь',{exact:true}).fill(basic.slice(0,split));await page.getByLabel('Пароль',{exact:true}).fill(basic.slice(split+1));await page.getByRole('button',{name:'Войти',exact:true}).click();await page.getByRole('button',{name:'? Справка',exact:true}).waitFor();};
 await page.goto('http://127.0.0.1:3000/?page=transport&task_id=33641');await login();
 await page.waitForResponse(r=>r.url().includes('/tasks/33641/sts')&&r.status()===200);
 await page.waitForFunction(()=>Array.from(document.querySelectorAll('input')).some(n=>n.value==='33641')); 
 await page.screenshot({path:path.join(__dirname,'trip-link.png')});
 const deepLink=await page.locator('input').evaluateAll(nodes=>nodes.some(n=>n.value==='33641'));
 if(!deepLink)throw Error('Exact trip filter not selected');
 await page.route('**/api/admin/transport/tasks?*',r=>r.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'test unavailable'})}));
 await page.route('**/api/admin/transport/vehicles',r=>r.fulfill({status:503,contentType:'application/json',body:'{}'}));
 await page.goto('http://127.0.0.1:3000/?page=transport');await login();
 await page.locator('.dispatch-error').waitFor();
 const text=await page.locator('body').innerText();
 if(text.includes('Т368ХН')||text.includes('В703РО')||text.includes('Е152НХ'))throw Error('Demo fallback displayed');
 await page.screenshot({path:path.join(__dirname,'source-error.png')});
 const result={deepLink,source503NoDemo:true,pageErrors:errors};fs.writeFileSync(path.join(__dirname,'ui.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 if(errors.length)throw Error('Browser errors');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
