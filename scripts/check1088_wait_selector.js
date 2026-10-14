const fs=require('fs'),vm=require('vm'),assert=require('assert');
class Element{
 constructor(){this.children=[];this.value='';this.textContent='';this.disabled=false;this.events={};}
 appendChild(v){this.children.push(v);}get firstChild(){return this.children[0];}
 replaceChildren(...v){this.children=v;if(v.length===0)this.value='';}
 addEventListener(n,fn){this.events[n]=fn;}
}
const elements=new Map(),requests=[],storage=new Map(),events={};
const el=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
const auth={state:{apiBase:'http://own',user:{username:'admin'}},headers:()=>({})};
const window={wmsAdminAuth:auth,location:{search:'?decision_operation_id=DEC:own'},addEventListener:(n,f)=>events[n]=f};
const ctx=vm.createContext({window,document:{getElementById:el,createElement:()=>new Element()},URLSearchParams,crypto:{randomUUID:()=> 'own-new'},console,
 localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},
 fetch:(url,options)=>new Promise(resolve=>requests.push({url,options,resolve}))});
vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/st-waiting-tasks.js','utf8'),ctx);
const flush=()=>new Promise(r=>setImmediate(r));
const result={decision_operation_id:'DEC:own',warehouse_id:1,st_number:'ST:own',waiting_cell:'WAIT',tasks:[],next_after_task_id:null,selection_required:true,
 available_places:[{root_identifier:'HU:A',place_kind:'HU',cell:'C1',available:false,planned_task_id:12},{root_identifier:'CASE:1',place_kind:'CASE',cell:'C2',available:true,move_required:true}]};
function answer(value,ok=true){requests.at(-1).resolve({ok,text:async()=>JSON.stringify(value)});}
(async()=>{
 assert.equal(requests.length,1);assert(el('swPlan').disabled);
 answer(result);await flush();assert(el('swRoot').children[1].disabled);assert(el('swPlan').disabled);
 el('swRoot').value='CASE:1';el('swRoot').events.change();assert(!el('swPlan').disabled);
 el('swRead').events.click();assert(el('swPlan').disabled);answer({detail:{message:'read failed'}},false);await flush();assert(el('swPlan').disabled);
 el('swRead').events.click();answer(result);await flush();
 el('swRoot').value='CASE:1';el('swRoot').events.change();el('swPlan').events.click();
 const body=requests.at(-1).options.body;assert.equal(JSON.parse(body).root_identifier,'CASE:1');
 answer({detail:{code:'UNKNOWN'}},false);await flush();assert(el('swPlan').disabled);assert(!el('swRetry').disabled);
 el('swRoot').value='HU:changed';el('swRetry').events.click();assert.equal(requests.at(-1).options.body,body);
 answer({detail:{code:'UNKNOWN'}},false);await flush();assert(storage.size===1);
 events['wms-admin-auth-ready']();const old=requests.at(-1);auth.state.user={username:'other'};
 old.resolve({ok:true,text:async()=>JSON.stringify(result)});await flush();assert(el('swPlan').disabled);
 console.log('PASS1088 selector/fresh-read-only/disabled planned Root/original body-root retry/late actor');
})().catch(e=>{console.error(e);process.exitCode=1;});
