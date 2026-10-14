const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const data=new Map(),context={window:{wmsAdminAuth:{state:{apiBase:'http://local',user:{username:'admin'}}}},
 localStorage:{getItem:k=>data.has(k)?data.get(k):null,setItem:(k,v)=>data.set(k,v),removeItem:k=>data.delete(k)},
 crypto:{randomUUID:()=> 'archive-one'}};
vm.createContext(context);vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/wave-command-intent.js','utf8'),context);vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/wave-execution-intent.js','utf8'),context);
const api=context.window.wmsWaveExecutionIntent;
assert.equal(api.valid({wave:4,body:{operation_id:'op',disposition:'UNKNOWN',reason:'x'}}),false);
assert.equal(api.valid({wave:4,body:{operation_id:'op',extra:true}}),false);
const record=api.save({wave:4,body:{operation_id:'op',disposition:'RETURNED_TO_PLANNING',reason:'returned'}});
assert.equal(api.read().value.body.operation_id,'op');
assert.throws(()=>api.save({wave:5,body:{operation_id:'other'}}));
data.set(record.storageKey,'different-tab');assert.throws(()=>api.settle(record));assert.equal(data.get(record.storageKey),'different-tab');
const damaged=api.read();assert.equal(damaged.damaged,true);api.archiveDamaged(damaged);
assert.equal(data.get(record.storageKey+':damaged:archive-one'),'different-tab');assert.equal(api.read().value,null);
const next=api.save({wave:4,body:{operation_id:'original'}});
context.window.wmsAdminAuth.state.user.username='other';
assert.throws(()=>api.settle(next));assert.equal(data.get(next.storageKey),next.raw);
assert.equal(api.read().value,null);
console.log('861 PASS exact replay intent; malformed blocked; archive retained; cross-tab/context cannot erase original');
