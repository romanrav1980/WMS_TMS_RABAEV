// Actual React hook, API shim only: scope switches must never render previous data.
const path=require('node:path'),fs=require('node:fs'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const esbuild=require('../../admin/wms_admin_frontend/node_modules/esbuild');
const root=path.resolve(__dirname,'../..'),hook=path.join(root,'admin/wms_admin_frontend/src/features/platform/access-admin/useApiRead.ts');
const out=path.join(root,'reports/retailcase/2026-10-15/queue-scoped-read/hook-browser.json');
const shim=`export class ApiRequestError extends Error { constructor(status){super('test');this.status=status;this.detail='TEST';} }
export function apiFetch(path,options){return new Promise((resolve,reject)=>{window.pending.push({path,signal:options.signal,resolve,reject});});}
window.resolveNext=(path,data)=>{const p=window.pending.find(p=>p.path===path&&!p.settled);p.settled=true;p.resolve(data);};
window.rejectNext=(path,status)=>{const p=window.pending.find(p=>p.path===path&&!p.settled);p.settled=true;p.reject(new ApiRequestError(status));};`;
const harness=`import React,{useState} from 'react';import {createRoot} from 'react-dom/client';import {useApiRead} from '${hook.replaceAll('\\','/')}';
window.pending=[];window.snapshots=[];
function App(){const[path,setPath]=useState('/A'),[reload,setReload]=useState(0);const read=useApiRead(path,reload);window.snapshots.push({path,data:read.data});
return <><button onClick={()=>setPath('/A')}>A</button><button onClick={()=>setPath('/B')}>B</button><button onClick={()=>setPath('/C')}>C</button><button onClick={()=>setPath(null)}>Off</button><button onClick={()=>setReload(x=>x+1)}>Reload</button><output>{JSON.stringify(read)}</output></>;}
createRoot(document.getElementById('app')).render(<App/>);`;
(async()=>{assert(!fs.existsSync(out),'Preserve accepted evidence');
 const built=await esbuild.build({stdin:{contents:harness,loader:'tsx',resolveDir:root},bundle:true,write:false,format:'iife',nodePaths:[path.join(root,'admin/wms_admin_frontend/node_modules')],plugins:[{name:'api-shim',setup(build){build.onResolve({filter:/^\.\.\/\.\.\/\.\.\/api$/},()=>({path:'api',namespace:'shim'}));build.onLoad({filter:/.*/,namespace:'shim'},()=>({contents:shim,loader:'js'}));}}]});
 const browser=await chromium.launch({headless:true});let checks=0;
 try{const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.setContent('<div id="app"></div>');await page.addScriptTag({content:built.outputFiles[0].text});
 const wait=p=>page.waitForFunction(path=>window.pending.some(p=>p.path===path&&!p.settled),p);
 const state=()=>page.locator('output').evaluate(n=>JSON.parse(n.textContent));
 await wait('/A');await page.evaluate(()=>window.resolveNext('/A',{name:'WARE_A'}));await page.waitForFunction(()=>document.querySelector('output').textContent.includes('WARE_A'));checks++;
 await page.getByRole('button',{name:'B',exact:true}).click();await wait('/B');assert.equal((await state()).data,null);checks++;
 await page.evaluate(()=>window.resolveNext('/B',{name:'WARE_B'}));await page.waitForFunction(()=>document.querySelector('output').textContent.includes('WARE_B'));
 await page.getByRole('button',{name:'Reload',exact:true}).click();await wait('/B');assert.equal((await state()).data.name,'WARE_B');
 await page.evaluate(()=>window.rejectNext('/B',503));await page.waitForFunction(()=>JSON.parse(document.querySelector('output').textContent).error);assert.equal((await state()).data.name,'WARE_B');checks++;
 await page.getByRole('button',{name:'C',exact:true}).click();await wait('/C');assert.equal((await state()).data,null);
 await page.evaluate(()=>window.rejectNext('/C',403));await page.waitForFunction(()=>JSON.parse(document.querySelector('output').textContent).error);assert.equal((await state()).data,null);checks++;
 await page.getByRole('button',{name:'A',exact:true}).click();await wait('/A');await page.getByRole('button',{name:'B',exact:true}).click();await wait('/B');
 await page.evaluate(()=>window.resolveNext('/A',{name:'LATE_FOREIGN'}));assert.equal((await state()).data,null);
 await page.evaluate(()=>window.resolveNext('/B',{name:'WARE_B2'}));await page.waitForFunction(()=>document.querySelector('output').textContent.includes('WARE_B2'));checks++;
 await page.getByRole('button',{name:'Off',exact:true}).click();assert.equal((await state()).data,null);checks++;
 const leaked=await page.evaluate(()=>window.snapshots.filter(s=>s.data&&((s.path==='/B'&&s.data.name==='WARE_A')||(s.path==='/C')||(s.data.name==='LATE_FOREIGN')||s.path===null)));
 assert.deepEqual(leaked,[]);assert.deepEqual(errors,[]);checks++;
 const report={status:'PASS',checks,kind:'ACTUAL_REACT_HOOK_API_SHIM',actual_api_calls:0,hardware:false,source_sha256:crypto.createHash('sha256').update(fs.readFileSync(hook)).digest('hex'),cases:['A→B hides A immediately','same-path reload may retain old own data with error','new path failure never retains foreign data','403 clears','cancelled late response ignored','null path clears','all render snapshots checked']};
 fs.writeFileSync(out,JSON.stringify(report,null,2));console.log(JSON.stringify(report));
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
