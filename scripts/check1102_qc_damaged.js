const fs=require('fs'),vm=require('vm'),assert=require('assert');
function setup(pendingRaw,draftRaw){
 const map=new Map(),requests=[],storage=new Map(),events={},key='wms-outgoing-quality:http://own:admin';
 class Element{
  constructor(){this.value='';this.children=[];this.events={};this.textContent='';this.disabled=false;}
  append(...v){this.children.push(...v);}prepend(...v){this.children.unshift(...v);}insertBefore(x){this.append(x);}appendChild(x){this.append(x);}replaceChildren(...v){this.children=v;}
  querySelector(s){if(!map.has(s))map.set(s,new Element());return map.get(s);}
  querySelectorAll(){return [...map.values()];}addEventListener(n,f){this.events[n]=f;}focus(){}
 }
 if(pendingRaw!==undefined)storage.set(key,pendingRaw);if(draftRaw!==undefined)storage.set(key+':scans',draftRaw);
 const main=new Element(),auth={state:{apiBase:'http://own',user:{username:'admin'}},headers:()=>({}),hasPermission:()=>true};
 const ctx=vm.createContext({window:{wmsAdminAuth:auth,location:{search:'?qc_shipment=ST:own'},addEventListener:(n,f)=>events[n]=f},
  document:{createElement:()=>new Element(),querySelector:()=>main,body:main},URLSearchParams,TextEncoder,Option:class extends Element{},
  crypto:{randomUUID:()=> 'archive-own'},console,
  localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},
  fetch:(url,options)=>new Promise(resolve=>requests.push({url,options,resolve}))});
 for(const file of ['wave-command-intent.js','outgoing-quality-intent.js','outgoing-quality-scan-view.js','outgoing-quality.js'])vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/'+file,'utf8'),ctx);
 return{ctx,storage,requests,key,auth,events,el:n=>main.querySelector('[data-'+n+']')};
}
const status={shipment_identifier:'ST:own',composition_signature:'A'.repeat(64),ready:false,case_content_version:20,mark_profiles:[],final_scale_required:false};
const flush=()=>new Promise(r=>setImmediate(r));
function answer(s,data=status,ok=true){s.requests.at(-1).resolve({ok,json:async()=>data});}
(async()=>{
 const s=setup('{broken','{"entries":"broken"}');answer(s);await flush();
 assert(s.el('load').disabled&&s.el('scan').disabled&&s.el('weight').disabled);assert(!s.el('recover').hidden);
 assert.equal(s.storage.get(s.key),'{broken');
 s.el('recover').onclick();assert.equal(s.storage.get(s.key),'{broken');answer(s,{detail:'read denied'},false);await flush();
 assert.equal(s.storage.get(s.key),'{broken');assert(s.el('load').disabled);
 s.el('recover').onclick();answer(s);await flush();
 assert(!s.storage.has(s.key)&&!s.storage.has(s.key+':scans'));
 assert.equal(s.storage.get(s.key+':damaged:archive-own'),'{broken');
 assert.equal(s.storage.get(s.key+':scans:damaged:archive-own'),'{"entries":"broken"}');
 assert(!s.el('load').disabled);assert(s.requests.every(x=>!x.options.method));
 const other=setup('{old');answer(other);await flush();other.el('recover').onclick();
 other.storage.set(other.key,'{newer');answer(other);await flush();assert.equal(other.storage.get(other.key),'{newer');assert(other.el('load').disabled);
 const late=setup('{old');answer(late);await flush();late.el('recover').onclick();late.auth.state.user={username:'other'};answer(late);await flush();
 assert.equal(late.storage.get(late.key),'{old');
 const scans=setup();answer(scans);await flush();scans.el('item-code').value='EAN:own';scans.el('add-item').onclick();
 assert.equal(JSON.parse(scans.storage.get(scans.key+':scans')).entries.length,1);
 function button(node){if(node.textContent==='Удалить')return node;for(const child of node.children){const found=button(child);if(found)return found;}return null;}
 button(scans.el('scan-list')).events.click();assert.equal(JSON.parse(scans.storage.get(scans.key+':scans')).entries.length,0);
 scans.el('item-code').value='EAN:own';scans.el('add-item').onclick();scans.el('errors').value='0';scans.el('scan').onclick();
 const frozen=scans.requests.at(-1).options.body,originalScans=scans.storage.get(scans.key+':scans');assert.equal(JSON.parse(frozen).item_scans.length,1);
 answer(scans,{detail:'unknown'},false);await flush();const remove=button(scans.el('scan-list'));assert(remove.disabled);
 remove.events.click();assert.equal(scans.storage.get(scans.key+':scans'),originalScans);
 scans.el('load').onclick();assert.equal(scans.requests.at(-1).options.body,frozen);
 answer(scans,{detail:'unknown'},false);await flush();
 const current=setup();answer(current);await flush();current.el('load').onclick();answer(current);await flush();
 const planned=JSON.parse(current.requests.at(-1).options.body);
 answer(current,{operation_id:planned.operation_id,control_status:status});await flush();
 assert(!current.requests.at(-1).options.method);assert(!current.storage.has(current.key));
 answer(current,{...status,case_content_version:21,composition_signature:'B'.repeat(64)});await flush();
 assert(current.el('summary').textContent.includes('v21'));
 const v=s.ctx.window.wmsQualityIntent,good={identifier:'ST:own',kind:'plan',body:{operation_id:'QC:1',expected_composition_signature:'A'.repeat(64),note:null}};
 assert(v.valid(good));assert(!v.valid({...good,foreign:true}));assert(!v.valid({...good,body:{...good.body,quality_kind:'SCAN'}}));
 assert(!v.validDraft({identifier:'ST:own',signature:'A'.repeat(64),entries:[{kind:'mark',value:{system_code:'CRPT',profile_code:'я'.repeat(41),code:'own'}}]}));
 console.log('PASS1102 bad pending+draft blocked/archive after authorisedGET/no POST/denied GET/cross-tab/late actor/strict contract');
})().catch(e=>{console.error(e);process.exitCode=1;});
