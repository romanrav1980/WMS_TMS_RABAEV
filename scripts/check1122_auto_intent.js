const fs=require('fs'),vm=require('vm'),assert=require('assert');
function setup(raw){
 const nodes=new Map(),storage=new Map(),requests=[],events={};
 class Element{constructor(){this.value='';this.events={};this.children=[];this.disabled=false;this.textContent='';}
 append(...v){this.children.push(...v);}replaceChildren(...v){this.children=v;}addEventListener(n,f){this.events[n]=f;}}
 const el=id=>{if(!nodes.has(id))nodes.set(id,new Element());return nodes.get(id);};
 const key='sap-auto-preparation:http://own:admin';
 if(raw!==undefined)storage.set(key,raw);
 const auth={state:{apiBase:'http://own',user:{username:'admin'}},headers:()=>({})};
 const ctx=vm.createContext({window:{wmsAdminAuth:auth,wmsCommandIntent:null,addEventListener:(n,f)=>events[n]=f,dispatchEvent:()=>{}},
  document:{getElementById:el,createElement:()=>new Element()},localStorage:{getItem:k=>storage.get(k)??null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},
  crypto:{randomUUID:()=> 'own-op'},location:{search:'',hash:''},URLSearchParams,Event:class{},requestAnimationFrame:f=>f(),
  fetch:(url,options)=>new Promise(resolve=>requests.push({url,options,resolve})),console});
 for(const f of ['wave-command-intent.js','sap-automatic-preparation.js'])vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/'+f,'utf8'),ctx);
 el('sapAutoOrder').value='2135';el('sapAutoMass').value='16';el('sapAutoVolume').value='0.096';el('sapAutoCount').value='100';
 return{el,storage,key,auth,requests,events};
}
const flush=()=>new Promise(r=>setImmediate(r));
function answer(s,value,ok=true){s.requests.at(-1).resolve({ok,json:async()=>value});}
const preview={customer_order_id:2135,source_signature:'a'.repeat(64),pallets:[{lines:[{articul:'A',quantity:'6'}]}],
 pallet_statistics:[{assembly_group:1,goods_weight_kg:'4',goods_volume_m3:'0.024'}]};
(async()=>{
 const s=setup();s.el('sapAutoRead').events.click();answer(s,preview);await flush();assert(!s.el('sapAutoSave').disabled);
 s.el('sapAutoSave').events.click();const body=s.requests.at(-1).options.body;
 assert(s.storage.has(s.key));answer(s,{detail:'unknown'},false);await flush();assert(s.storage.has(s.key));
 s.el('sapAutoMass').value='99';s.el('sapAutoMass').events.input();
 s.el('sapAutoRetry').events.click();assert.equal(s.requests.at(-1).options.body,body);
 const command=JSON.parse(body),result={customer_order_id:2135,status:'ST_PREPARED',st_number:'SAP_2135',pallet_identifiers:['OP_1'],auto_request:command};
 s.storage.set(s.key,'{other-tab');answer(s,result);await flush();assert.equal(s.storage.get(s.key),'{other-tab');
 const damaged=setup('{broken');assert(damaged.el('sapAutoSave').disabled&&!damaged.el('sapAutoRecover').hidden);
 damaged.el('sapAutoRecover').events.click();assert.equal(damaged.requests.at(-1).options.method,'GET');
 answer(damaged,{detail:'denied'},false);await flush();assert.equal(damaged.storage.get(damaged.key),'{broken');
 damaged.el('sapAutoRecover').events.click();answer(damaged,{customer_order_id:2135});await flush();
 assert.equal(damaged.storage.get(damaged.key+':damaged:own-op'),'{broken');assert(!damaged.storage.has(damaged.key));
 const late=setup('{broken');late.el('sapAutoRecover').events.click();late.auth.state.user.username='other';answer(late,{customer_order_id:2135});await flush();assert(late.storage.has(late.key));
 console.log('PASS1122 save-before-send/exact-repeat/cross-tab preservation/damaged-denied/GET archive/late-actor');
})();
