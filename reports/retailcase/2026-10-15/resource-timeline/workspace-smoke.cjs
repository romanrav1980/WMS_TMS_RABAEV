const {chromium}=require('../../../../admin/wms_admin_frontend/node_modules/playwright');
const fs=require('fs'),path=require('path');
(async()=>{const basic=fs.readFileSync('front.bat','utf8').match(/VITE_ADMIN_BASIC_AUTH=([^"\r\n]+)/)[1];
 const browser=await chromium.launch({headless:true});try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('http://127.0.0.1:3000/?page=workspace&workspace=dispatcher');const sep=basic.indexOf(':');
 await page.getByLabel('Пользователь',{exact:true}).fill(basic.slice(0,sep));await page.getByLabel('Пароль',{exact:true}).fill(basic.slice(sep+1));
 await page.getByRole('button',{name:'Войти',exact:true}).click();await page.getByRole('tab',{name:'Диспетчер',exact:true}).waitFor();
 await page.getByRole('region',{name:'Схема ворот и двора'}).waitFor();
 await page.waitForFunction(()=>{const e=document.querySelector('.ops-kpi-value');return e&&e.textContent&&!e.textContent.includes('…');});
 await page.screenshot({path:path.join(__dirname,'workspace-desktop.png')});
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(__dirname,'workspace-mobile.png')});
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 const result={workspaceRoute:true,desktop:true,mobile:true,mobileOverflow:overflow,pageErrors:errors};
 fs.writeFileSync(path.join(__dirname,'workspace-ui.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 if(errors.length)throw Error('Browser page errors');if(overflow)throw Error('Mobile viewport overflow');
 }finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
