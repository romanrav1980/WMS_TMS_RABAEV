// Execute the actual TS journal: logout and another tab must retain the original command.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const ts=require('../../admin/wms_admin_frontend/node_modules/typescript');
const source=fs.readFileSync('admin/wms_admin_frontend/src/features/platform/workspaces/paper/casePaper.ts','utf8');
const compiled=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText;
function fixture(){
 let scope='api:alice',calls=0,resolve;
 const rows=new Map(),exports={};
 const localStorage={getItem:k=>rows.get(k)??null,setItem:(k,v)=>rows.set(k,v),removeItem:k=>rows.delete(k)};
 const api={apiOperationScope:()=>{if(!scope)throw Error('No session');return scope;},
  apiFetch:()=>{calls++;return new Promise(r=>{resolve=r;});},ApiRequestError:class extends Error{}};
 vm.runInNewContext(compiled,{exports,require:()=>api,localStorage,crypto:{randomUUID:()=> 'one-operation'}});
 const intent=exports.saveCasePending(7,11,{fact_qty:'1',scan_cell:'own-cell',scan_container:'internal-case',scan_product:'own-sku',expected_case_signature:'A'.repeat(64)});
 return {rows,intent,exports,setScope:v=>{scope=v;},resolve:v=>resolve(v),calls:()=>calls};
}
(async()=>{
 let f=fixture();f.setScope(null);
 assert.equal((await f.exports.sendCasePending(f.intent)).kind,'foreign');assert.equal(f.calls(),0);assert.equal(f.rows.size,1);
 f=fixture();let response=f.exports.sendCasePending(f.intent);f.setScope(null);f.resolve({operation_id:f.intent.operation_id});
 assert.equal((await response).kind,'foreign');assert.equal(f.rows.size,1);
 f=fixture();response=f.exports.sendCasePending(f.intent);
 const key=[...f.rows.keys()][0],changed={...f.intent,wire:JSON.stringify({...JSON.parse(f.intent.wire),fact_qty:'2'})};
 f.rows.set(key,JSON.stringify(changed));f.resolve({operation_id:f.intent.operation_id});
 assert.equal((await response).kind,'foreign');assert.equal(f.rows.get(key),JSON.stringify(changed));
 console.log('PASS: no send after logout; late logout reply retained; changed journal not cleared');
})().catch(e=>{console.error(e);process.exitCode=1;});
