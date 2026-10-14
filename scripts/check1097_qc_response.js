const fs=require('fs'),vm=require('vm'),assert=require('assert');
const elements=new Map(),requests=[],storage=new Map(),events={};
class Element{
 constructor(){this.value='';this.children=[];this.disabled=false;this.events={};this.hidden=false;this.textContent='';}
 append(...x){this.children.push(...x);}prepend(...x){this.children.unshift(...x);}appendChild(x){this.append(x);}
 insertBefore(x){this.append(x);}replaceChildren(...x){this.children=x;}
 querySelector(s){if(!elements.has(s))elements.set(s,new Element());return elements.get(s);}
 querySelectorAll(){return [...elements.values()];}addEventListener(n,f){this.events[n]=f;}
}
const main=new Element(),el=k=>main.querySelector('[data-'+k+']');
const auth={state:{apiBase:'http://own',user:{username:'admin'}},headers:()=>({}),hasPermission:()=>true};
const window={wmsAdminAuth:auth,location:{search:'?qc_shipment=ST:own'},addEventListener:(n,f)=>events[n]=f};
const ctx=vm.createContext({window,document:{createElement:()=>new Element(),querySelector:()=>main,body:main},
 localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},
 URLSearchParams,TextEncoder,Option:class extends Element{constructor(t,v){super();this.textContent=t;this.value=v;}},crypto:{randomUUID:()=> 'one'},console,
 fetch:(url,options)=>new Promise(resolve=>requests.push({url,options,resolve}))});
const signature='A'.repeat(64),status={shipment_identifier:'ST:own',composition_signature:signature,ready:false,control_mode:'BOTH',case_content_version:20,mark_profiles:[],final_scale_required:false,reason:'SHIPMENT_FULL_COMPOSITION_SCAN_REQUIRED'};
function answer(value){requests.at(-1).resolve({ok:true,json:async()=>value});}
const flush=()=>new Promise(r=>setImmediate(r));
(async()=>{
 vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/wave-command-intent.js','utf8'),ctx);
 vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/outgoing-quality-intent.js','utf8'),ctx);
 vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/outgoing-quality-scan-view.js','utf8'),ctx);
 vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/outgoing-quality.js','utf8'),ctx);
 assert.equal(requests.length,1);assert(!requests[0].options.method);answer(status);await flush();
 assert(el('summary').textContent.includes('v20'));assert.equal(storage.size,0);assert.equal(requests.length,1);
 el('load').onclick();answer(status);await flush();
 const post=requests.at(-1),body=post.options.body;assert.equal(post.options.method,'POST');
 const savedKey='wms-outgoing-quality:http://own:admin';assert(storage.has(savedKey));
 answer({operation_id:'wrong',control_status:status});await flush();assert(storage.has(savedKey));
 el('load').onclick();assert.equal(requests.at(-1).options.body,body);
 storage.set(savedKey,'{"changed":true}');
 answer({operation_id:JSON.parse(body).operation_id,control_status:status});await flush();assert.equal(storage.get(savedKey),'{"changed":true}');
 storage.set(savedKey,JSON.stringify({identifier:'ST:own',kind:'plan',body:JSON.parse(body)}));
 el('load').onclick();const late=requests.at(-1);
 auth.state.user={username:'other'};events['wms-admin-auth-ready']();
 late.resolve({ok:true,json:async()=>({operation_id:JSON.parse(body).operation_id,control_status:status})});await flush();
 assert(storage.has(savedKey));assert(!storage.has('wms-outgoing-quality:http://own:other'));
 console.log('PASS1097 readonly linked GET/no autoPLAN/exact operation-root response/cross-tab/late actor retained');
})().catch(e=>{console.error(e);process.exitCode=1;});
