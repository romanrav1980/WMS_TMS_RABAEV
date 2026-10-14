const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const fixture=JSON.parse(fs.readFileSync('tmp/context908.json','utf8'));
const saved=new Map();const storage={get length(){return saved.size;},key:i=>[...saved.keys()][i],getItem:k=>saved.get(k)??null,setItem:(k,v)=>saved.set(k,v),removeItem:k=>saved.delete(k)};
const window={wmsAdminAuth:{state:{apiBase:'local',user:{username:'a'}}},dispatchEvent(){}};
const c={window,localStorage:storage,CustomEvent:class{constructor(type){this.type=type;}},Date};vm.createContext(c);vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/receiving-intent.js','utf8'),c);
const body={...fixture.body,sscc:fixture.uid};delete body.pallet_identifier;
const path='/api/receiving/supply-orders/'+fixture.order_id+'/pallets',api=window.wmsReceiptIntent;
let intent=api.prepare(path,body);
for(const wrong of[{operation_id:'OTHER'},{line_number:'2'},{pallet_identifier:'OTHER'},{quantity:'4'},{status:'PLANNED'},{task_id:0}]){
 assert.throws(()=>api.settle(intent,201,{...fixture.receipt,...wrong}),/Ответ не соответствует/);
 assert.equal(saved.size,1,'Uncorrelated response must preserve original receipt');
}
api.settle(intent,201,{...fixture.receipt,quantity:'3.000000'});
assert.equal(saved.size,0);
intent=api.prepare(path,body);
const changed=JSON.parse(storage.getItem(intent.storage_key));changed.body.quantity='4';storage.setItem(intent.storage_key,JSON.stringify(changed));
assert.throws(()=>api.settle(intent,201,fixture.receipt),/другой вкладке/);assert.equal(saved.size,1);
console.log('931 PASS original real-shaped receipt correlation OP/line/pallet/exact quantity/status/task; malformed success retains request; another tab cannot erase changed receipt; no stock writes');
