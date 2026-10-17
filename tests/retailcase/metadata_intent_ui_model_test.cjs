// Pure frontend contract/storage checks: no browser, API or Oracle calls.
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm"),{webcrypto}=require("node:crypto");
const root=path.resolve(__dirname,"../.."),ts=require(path.join(root,"terminal/wms_terminal_web/node_modules/typescript"));
const cache=new Map(),store=new Map();let quota=false;
const storage={getItem:key=>store.get(key)??null,setItem:(key,value)=>{if(quota)throw new Error("quota");store.set(key,value);}};
function load(file){file=path.resolve(file);if(cache.has(file))return cache.get(file);const out={};cache.set(file,out);
 const src=fs.readFileSync(file,"utf8"),js=ts.transpileModule(src,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
 vm.runInNewContext(js,{exports:out,require:name=>load(path.resolve(path.dirname(file),name+".ts")),crypto:webcrypto,TextEncoder,localStorage:storage,console});return out;}
const base=path.join(root,"terminal/wms_terminal_web/src/features/inventory/resource-intents"),c=load(path.join(base,"contracts.ts")),j=load(path.join(base,"controlJournal.ts"));
let count=0;async function check(name,run){await run();count++;console.log("PASS",name);}
async function original(domain="CASE"){
 const body=domain==="CASE"?{operation_id:"ORIGINAL:1",action:"START",expected_assignment_version:2,resource_session_id:3,resource_id:4,equipment_id:null,reason:"explicit original reason"}
  :{operation_id:"ORIGINAL:2",action:"ASSIGN",target:"worker",expected_assignment_version:2,expected_task_signature:"A".repeat(64),resource_session_id:3,resource_id:4,equipment_id:null};
 const wire=c.canonical(body);return{domain,task_id:7,actor:"worker",server:"http://127.0.0.1:8088",operation_id:body.operation_id,action:body.action,target:"worker",wire,request_sha256:await c.hash(wire),expected_assignment_version:2};}
function proof(o,control){return{status:"ABANDONED",operation_id:control.body.operation_id,domain:o.domain,task_id:o.task_id,actor:o.actor,action:o.action,target:o.target,original_operation_id:o.operation_id,original_wire:o.wire,original_request_sha256:o.request_sha256,control_request_sha256:control.sha256,original_expected_assignment_version:2,assignment_version_at_abandon:4,outcome_confirmed:true,stock_posted:false};}
(async()=>{
 const o=await original();
 await check("CASE and TASK original identity/hash validated",async()=>{await c.validateOriginal(o);await c.validateOriginal(await original("TASK"));});
 await check("altered original bytes refused",async()=>{await assert.rejects(()=>c.validateOriginal({...o,wire:o.wire+" "}));});
 await check("canonical control uses native alphabetical JSON keys",()=>assert.equal(c.canonical({task_id:7,reason:"reason",domain:"CASE",original_wire:"{}",operation_id:"X"}),'{"domain":"CASE","operation_id":"X","original_wire":"{}","reason":"reason","task_id":7}'));
 let control;
 await check("control persisted and reread before returning sendable bytes",async()=>{control=await j.saveControl(o,"explicit abandonment reason");assert.equal((await j.readControl(o)).wire,control.wire);assert.equal(store.size,1);});
 await check("retry preserves operation and reason exactly",async()=>{const next=await j.saveControl(o,"changed reason must not replace saved bytes");assert.equal(next.wire,control.wire);assert.equal(next.body.operation_id,control.body.operation_id);});
 await check("wrong actor/domain/task/wire/hash/stock proof refused",()=>{const valid=proof(o,control);for(const delta of [{actor:"other"},{domain:"TASK"},{task_id:8},{original_wire:"{}"},{original_request_sha256:"0".repeat(64)},{control_request_sha256:"0".repeat(64)},{stock_posted:true},{outcome_confirmed:false}])assert.throws(()=>c.validateAbandoned({...valid,...delta},o,control));});
 await check("ABANDONED resolution is not RECORDED",()=>{const value=c.validateResolution({domain:o.domain,task_id:7,actor:o.actor,original_operation_id:o.operation_id,original_request_sha256:o.request_sha256,status:"ABANDONED",original_receipt:null,abandonment:proof(o,control)},o);assert.equal(value.status,"ABANDONED");});
 await check("RECORDED resolution binds original operation and target",()=>{const task={...o,domain:"TASK",action:"ASSIGN"};const envelope={domain:"TASK",task_id:7,actor:o.actor,original_operation_id:o.operation_id,original_request_sha256:o.request_sha256,status:"RECORDED",abandonment:null,original_receipt:{operation_id:o.operation_id,task_id:7,actor:o.actor,action:"ASSIGN",target:"worker",request_sha256:o.request_sha256,outcome_confirmed:true,stock_posted:false,outcome:"REJECTED"}};assert.equal(c.validateResolution(envelope,task).status,"RECORDED");assert.throws(()=>c.validateResolution({...envelope,original_receipt:{...envelope.original_receipt,target:"other"}},task));});
 await check("terminal proof retained separately from original request",async()=>{await j.saveProof(o,{status:"ABANDONED",abandonment:proof(o,control)});assert.equal((await j.readControl(o)).proof.status,"ABANDONED");assert.equal((await j.readControl(o)).body.original_wire,o.wire);});
 await check("conflicting terminal proof cannot overwrite history",async()=>{const changed={...proof(o,control),operation_id:"OTHER.CONTROL"};await assert.rejects(()=>j.saveProof(o,{status:"ABANDONED",abandonment:changed}));});
 await check("damaged local control remains untouched and blocks",async()=>{const [key]=store.keys();store.set(key,"{damaged");await assert.rejects(()=>j.readControl(o),j.ControlJournalError);assert.equal(store.get(key),"{damaged");store.clear();});
 await check("storage quota refuses creation before any sender can run",async()=>{quota=true;await assert.rejects(()=>j.saveControl(o,"explicit abandonment reason"),j.ControlJournalError);assert.equal(store.size,0);quota=false;});
 await check("invalid reason never writes control",async()=>{await assert.rejects(()=>j.saveControl(o,"bad"),j.ControlJournalError);assert.equal(store.size,0);});
 await check("same original server actor isolated by key",async()=>{await j.saveControl(o,"explicit abandonment reason");assert.equal(await j.readControl({...o,server:"http://different"}),null);assert.equal(await j.readControl({...o,actor:"other",target:"other"}),null);});
 console.log(count+" metadata recovery model checks PASS");
})().catch(error=>{console.error(error);process.exitCode=1;});
