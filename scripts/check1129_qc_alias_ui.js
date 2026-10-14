const fs=require('fs'),vm=require('vm'),assert=require('assert');
const nodes=new Map(),requests=[];class E{
 constructor(){this.value='';this.textContent='';this.children=[];this.disabled=false;this.events={};}
 append(...v){this.children.push(...v);}prepend(...v){this.children.unshift(...v);}appendChild(v){this.append(v);}insertBefore(v){this.append(v);}replaceChildren(...v){this.children=v;}
 querySelector(s){if(!nodes.has(s))nodes.set(s,new E());return nodes.get(s);}querySelectorAll(){return[...nodes.values()];}addEventListener(n,f){this.events[n]=f;}}
const main=new E(),el=k=>main.querySelector('[data-'+k+']'),storage=new Map();
const ctx=vm.createContext({window:{location:{search:'?qc_shipment=CP:own'},wmsAdminAuth:{state:{apiBase:'http://own',user:{username:'admin'}},headers:()=>({}),hasPermission:()=>true},addEventListener:()=>{}},
 document:{querySelector:()=>main,createElement:()=>new E(),body:main},TextEncoder,URLSearchParams,Option:class extends E{},
 crypto:{randomUUID:()=> 'own'},localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},console,
 fetch:(url,options)=>new Promise(resolve=>requests.push({url,options,resolve}))});
for(const f of ['wave-command-intent.js','outgoing-quality-intent.js','outgoing-quality-scan-view.js','outgoing-quality.js'])vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/'+f,'utf8'),ctx);
const status={shipment_identifier:'CASE.QC.ST:own',requested_identifier:'CP:own',composition_signature:'A'.repeat(64),case_content_version:20,ready:false,mark_profiles:[],final_scale_required:false};
const flush=()=>new Promise(r=>setImmediate(r)),answer=v=>requests.at(-1).resolve({ok:true,json:async()=>v});
(async()=>{
 assert.equal(requests.length,1);assert(requests[0].url.endsWith('CP%3Aown'));answer(status);await flush();
 assert.equal(el('id').value,'CASE.QC.ST:own');assert.equal(requests.length,1);
 el('load').onclick();assert(requests.at(-1).url.endsWith('CASE.QC.ST%3Aown'));answer(status);await flush();
 const post=requests.at(-1);assert.equal(post.options.method,'POST');assert(post.url.endsWith('CASE.QC.ST%3Aown/plan'));
 const body=post.options.body,saved=JSON.parse(storage.values().next().value);assert.equal(saved.identifier,'CASE.QC.ST:own');
 post.resolve({ok:false,json:async()=>({detail:'unknown'})});await flush();
 el('load').onclick();assert.equal(requests.at(-1).options.body,body);assert(requests.at(-1).url.endsWith('CASE.QC.ST%3Aown/plan'));
 console.log('PASS1129 physical linked GET adopts canonical; PLAN/retry freeze canonical source; no autoPLAN');
})().catch(e=>{console.error(e);process.exitCode=1;});
