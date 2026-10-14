const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const records=new Map(),context={window:{wmsAdminAuth:{state:{apiBase:'http://local',user:{username:'actor'}}}},
 localStorage:{getItem:k=>records.has(k)?records.get(k):null,setItem:(k,v)=>records.set(k,v),removeItem:k=>records.delete(k)},crypto:{randomUUID:()=> 'archive'}};
vm.createContext(context);
for(const file of ['wave-command-intent.js','wave-pick-intent.js'])
 vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/'+file,'utf8'),context);
const intent=context.window.wmsWavePickIntent;
assert.equal(intent.valid({wave:1,body:{operation_id:'op',disposition:'RETURNED_TO_PLANNING'}}),false);
assert.equal(intent.valid({wave:1,body:{operation_id:'op space'}}),false);
const record=intent.save({wave:1,body:{operation_id:'WAVE.PICK:original'}});
assert.throws(()=>intent.save({wave:1,body:{operation_id:'different'}}));
context.window.wmsAdminAuth.state.apiBase='http://other';
assert.throws(()=>intent.settle(record));assert.equal(records.get(record.storageKey),record.raw);
context.window.wmsAdminAuth.state.apiBase='http://local';intent.settle(record);assert.equal(intent.read().value,null);
console.log('882 PASS readiness intent body whitelist, valid native operation ID, original retained across API context');
