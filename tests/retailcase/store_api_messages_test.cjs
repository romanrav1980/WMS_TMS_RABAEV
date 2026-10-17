// Exercise the actual request/error boundary, including correlation of confirmed refusals.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const ts=require('../../terminal/wms_terminal_web/node_modules/typescript');
const folder='terminal/wms_terminal_web/src/features/delivery/';
function load(name,extra={}){const source=fs.readFileSync(folder+name+'.ts','utf8').replace('import.meta.env.VITE_STORE_API_BASE_URL','undefined');
 const context={exports:{},TextEncoder,btoa,Response,...extra};vm.runInNewContext(ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText,context);return context;}
const messages=load('messages').exports,context=load('api',{require:name=>{assert.equal(name,'./messages');return messages;}}),api=context.exports;
const credentials={username:'TEST',password:'NOT_A_REAL_PASSWORD'},body={operation_id:'ORIGINAL'};
let count=0;
async function failure(status,payload,input=body){context.fetch=async()=>new Response(typeof payload==='string'?payload:JSON.stringify(payload),{status});
 try{await api.storeAppRequest('/api/technical/path',credentials,input);assert.fail('Expected failure');}
 catch(error){assert(error instanceof api.StoreAppApiError);assert(!/Error:|\/api\/|HTTP\s*\d{3}/.test(String(error)));count++;return error;}}
(async()=>{
 let e=await failure(503,'unavailable');assert.equal(e.confirmed,false);assert(String(e).includes('временно недоступен'));
 e=await failure(500,{detail:{outcome_confirmed:true,operation_id:'ORIGINAL',message:'Ошибка ORA-20000: internal'}});assert.equal(e.confirmed,false);
 e=await failure(409,{detail:{outcome_confirmed:true,operation_id:'OTHER',message:'OPERATION_CONFLICT'}});assert.equal(e.confirmed,false);
 e=await failure(409,{detail:{outcome_confirmed:true,operation_id:'ORIGINAL',code:'OPERATION_CONFLICT'}});assert.equal(e.confirmed,true);assert.equal(e.code,'OPERATION_CONFLICT');assert(String(e).includes('другими данными'));
 e=await failure(409,{detail:{outcome_confirmed:true,request_id:'REQUEST'}},{request_id:'REQUEST'});assert.equal(e.confirmed,true);
 for(const status of [401,403]){e=await failure(status,{});assert(api.isAuthError(e));assert.equal(e.confirmed,false);}
 e=await failure(200,'invalid JSON');assert.equal(e.status,200);assert.equal(e.confirmed,false);
 context.fetch=async()=>{throw new TypeError('fetch failed');};try{await api.storeAppRequest('/api/technical/path',credentials,body);assert.fail();}
 catch(error){assert.equal(error.status,0);assert.equal(error.confirmed,false);assert(String(error).includes('Нет связи'));count++;}
 for(const message of ['Ошибка /api/technical/path','Ошибка HTTP 503','Ошибка https://internal/path']){assert(!/\/api\/|HTTP|https:/.test(messages.humanStoreMessage(message)));count++;}
 assert.equal(messages.humanStoreMessage('Скан не соответствует месту.'),'Скан не соответствует месту.');count++;
 console.log(count+' store request/message boundary checks PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
