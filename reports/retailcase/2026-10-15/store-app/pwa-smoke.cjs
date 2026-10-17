const {chromium}=require('../../../../admin/wms_admin_frontend/node_modules/playwright');
const fs=require('fs'),path=require('path'),assert=require('assert');
(async()=>{const browser=await chromium.launch({headless:true});try{
 const context=await browser.newContext({viewport:{width:390,height:844}}),page=await context.newPage(),errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 const response=await page.goto('http://127.0.0.1:8088/store/');assert.equal(response.status(),200);
 await page.getByRole('button',{name:'Войти',exact:true}).waitFor();
 await page.evaluate(async()=>{await navigator.serviceWorker.ready;if(!navigator.serviceWorker.controller)await new Promise(resolve=>navigator.serviceWorker.addEventListener('controllerchange',resolve,{once:true}));});
 const info=await page.evaluate(async()=>{
  const registration=await navigator.serviceWorker.getRegistration('/store/');
  const manifest=await(await fetch('/store/manifest.webmanifest')).json();
  await caches.open('wms-terminal-shell-evidence');
  const cache=await caches.open('retailcase-store-shell-v3');
  const urls=(await cache.keys()).map(r=>new URL(r.url).pathname);
  return{scope:registration.scope,manifest,urls,keys:await caches.keys()};
 });
 assert(info.scope.endsWith('/store/'));assert.equal(info.manifest.display,'standalone');assert.equal(info.manifest.start_url,'/store/');assert(info.urls.some(url=>url.includes('/assets/store-')));assert(info.urls.some(url=>url.includes('/assets/client-')));assert(!info.urls.some(url=>url.startsWith('/api/')));
 const cdp=await context.newCDPSession(page);const installability=await cdp.send('Page.getInstallabilityErrors');
 await context.setOffline(true);await page.reload();await page.getByRole('button',{name:'Войти',exact:true}).waitFor();
 await page.screenshot({path:path.join(__dirname,'store-mobile-offline.png')});
 const keys=await page.evaluate(()=>caches.keys());assert(keys.includes('wms-terminal-shell-evidence'));assert.deepEqual(errors,[]);
 const output={status:'PASS',productionSameOrigin:true,scope:info.scope,offlineLoginShell:true,privateApiCached:false,otherApplicationCachePreserved:true,installabilityErrors:installability.installabilityErrors,physicalDeviceInstalled:false,pageErrors:errors};
 fs.writeFileSync(path.join(__dirname,'pwa.json'),JSON.stringify(output,null,2));console.log(JSON.stringify(output));await context.close();
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
