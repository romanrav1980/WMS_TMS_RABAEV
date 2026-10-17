// Focused real-hook browser test: identity cancellation while async journal verification settles.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const esbuild=require('../../admin/wms_admin_frontend/node_modules/esbuild');
const root=path.resolve(__dirname,'../..');
const fixture=`import React,{useState} from 'react';import {createRoot} from 'react-dom/client';
import {usePickerTime} from './src/features/inventory/picker-time/usePickerTime';
const w=window as any;w.t={posts:[],calls:[],hold:false};
const blank=(actor:string)=>({operator_id:actor,stream_version:0,shift_state:'OFF',work_state:'IDLE',warehouse_id:null,resource_session_id:null,resource_id:null,source_kind:null,source_id:null,shift_started_at:null,work_started_at:null,pause_started_at:null,last_event_at:null,work_coverage_certified:false,source_mode:'MANUAL_CONFIRMED'});
let digestCount=0;const original=crypto.subtle.digest.bind(crypto.subtle);
crypto.subtle.digest=(...args:any[])=>{digestCount++;if(digestCount===2){w.t.hold=true;return new Promise(resolve=>w.t.releaseHash=()=>original(...args as [any,any]).then(resolve));}return original(...args as [any,any]);};
w.fetch=async(path:string,options:any)=>{const actor=atob(options.headers.Authorization.slice(6)).split(':')[0];w.t.calls.push({actor,path});
 if(actor==='new'&&path.endsWith('/me/current'))return new Promise(resolve=>w.t.releaseNew=()=>resolve(new Response(JSON.stringify(blank('new')))));
 if(options.method==='POST'){const body=JSON.parse(options.body);w.t.posts.push(body);const at='2026-10-15T18:00:00Z';
 const bytes=await original('SHA-256',new TextEncoder().encode(options.body));const hash=Array.from(new Uint8Array(bytes),x=>x.toString(16).padStart(2,'0')).join('').toUpperCase();
 return new Response(JSON.stringify({operation_id:body.operation_id,actor,action:body.action,resource_session_id:3,warehouse_id:7,request_sha256:hash,outcome:'APPLIED',outcome_confirmed:true,changed:true,may_create_corrected_operation:false,error_code:null,stock_posted:false,event_at:at,before_version:0,after_version:1,state:{...blank(actor),stream_version:1,shift_state:'OPEN',warehouse_id:7,resource_id:4,resource_session_id:3,shift_started_at:at,last_event_at:at}}));}
 return new Response(JSON.stringify(blank(actor)));
};
function Harness(){const [actor,setActor]=useState('old'),time=usePickerTime({username:actor,password:'TEST'});w.t.time=time;w.t.actor=actor;w.t.switchActor=setActor;return <pre>{actor}:{String(time.busy)}</pre>;}
createRoot(document.getElementById('root')!).render(<Harness/>);`;
(async()=>{const result=await esbuild.build({stdin:{contents:fixture,resolveDir:path.join(root,'terminal/wms_terminal_web'),loader:'tsx'},bundle:true,write:false,format:'iife',platform:'browser',jsx:'automatic',define:{'import.meta.env':'{}'}});
 const browser=await chromium.launch({headless:true});try{const page=await browser.newPage();await page.route('**/*',route=>route.fulfill({contentType:'text/html',body:'<div id="root"></div>'}));await page.goto('http://127.0.0.1:8088/identity-test');await page.addScriptTag({content:result.outputFiles[0].text});
 await page.waitForFunction(()=>window.t?.time.current?.operator_id==='old'&&!window.t.time.busy);
 await page.evaluate(()=>void window.t.time.submit('ACTUAL_SHIFT_START',3,null,'Explicit old actor shift'));
 await page.waitForFunction(()=>window.t.hold);await page.evaluate(()=>window.t.switchActor('new'));
 await page.waitForFunction(()=>window.t.actor==='new'&&window.t.time.busy&&!!window.t.releaseNew);
 await page.evaluate(()=>window.t.releaseHash());await page.waitForTimeout(50);
 const before=await page.evaluate(()=>window.t.calls.length);await page.evaluate(()=>void window.t.time.submit('ACTUAL_SHIFT_START',3,null,'Explicit new actor shift'));
 await page.waitForTimeout(50);assert.equal(await page.evaluate(()=>window.t.calls.length),before,'old finally must not clear new identity running fence');
 const saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('wms.picker-time.journal.v1:'+location.origin+':old')));assert.ok(saved.pending,'identity cancellation during journal read must preserve old exact pending');assert.equal(saved.last,null);
 await page.evaluate(()=>window.t.releaseNew());await page.waitForFunction(()=>window.t.time.current?.operator_id==='new'&&!window.t.time.busy);
 assert.equal(await page.evaluate(()=>window.t.posts.length),1);
 const folder=path.join(root,'reports/retailcase/2026-10-15/picker-time-ui');fs.mkdirSync(folder,{recursive:true});
 fs.writeFileSync(path.join(folder,'identity-cancel-mock.json'),JSON.stringify({status:'PASS',kind:'FOCUSED_REAL_HOOK_BROWSER_MOCK',checks:['old finally cannot clear new identity busy fence','identity cancel during journal SHA preserves exact original pending'],actual_api_calls:0,oracle_writes:0,hardware:false,source:'terminal/wms_terminal_web/src/features/inventory/picker-time/usePickerTime.ts',source_sha256:require('node:crypto').createHash('sha256').update(fs.readFileSync(path.join(root,'terminal/wms_terminal_web/src/features/inventory/picker-time/usePickerTime.ts'))).digest('hex')},null,2));
 console.log('PASS identity switch keeps new busy fence and old exact pending after late journal hash');
 }finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
