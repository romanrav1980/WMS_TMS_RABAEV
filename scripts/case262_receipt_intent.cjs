const fs=require('fs'),vm=require('vm'),assert=require('assert');
const values=new Map();
const storage={get length(){return values.size},key(i){return [...values.keys()][i]??null},
  getItem(k){return values.get(k)??null},setItem(k,v){values.set(k,v)},removeItem(k){values.delete(k)}};
function boot(actor='admin',base='http://127.0.0.1:8088',store=storage){
 const context={localStorage:store,CustomEvent:class{constructor(name){this.type=name}},
  window:{wmsAdminAuth:{state:{user:{username:actor},apiBase:base}},dispatchEvent(){}},console};
 vm.runInNewContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/receiving-intent.js','utf8'),context);
 return context.window.wmsReceiptIntent;
}
const api=boot(),path='/api/receiving/supply-orders/own262/pallets';
const body={operation_id:'OWN262.A',sscc:'internal262',quantity:'3',supplier_batch:'B1',expiry_date:'2027-01-01',
 units:[{unit_id:'u1',codes:[{system:'CRPT',code:'unique-code'}]}]};
const first=api.prepare(path,body);assert.equal(api.pending().length,1);
api.settle(first,503,{detail:{outcome_confirmed:false,retry_same_operation_id:true}});
assert.equal(api.pending().length,1);
const resumed=boot().prepare(path,{...body,operation_id:'NEW_AFTER_RELOAD'});
assert.equal(resumed.body.operation_id,'OWN262.A');assert.equal(resumed.attempt_count,2);
assert.throws(()=>api.prepare(path,{...body,quantity:'4'}));
api.settle(resumed,403,{detail:{outcome_confirmed:true}});assert.equal(api.pending().length,1);
api.settle(resumed,422,{});assert.equal(api.pending().length,1);
assert.equal(boot('other').pending().length,0);assert.equal(boot('admin','http://other').pending().length,0);
const second=api.prepare(path,{...body,operation_id:'OWN262.B',sscc:'second262'});
assert.equal(api.pending().length,2);
api.settle(resumed,201,{pallet_identifier:'internal262',quantity:'3',task_id:1});
assert.equal(api.pending().length,1);
api.settle(second,409,{detail:{outcome_confirmed:true,operation_id_conflict:true}});
assert.equal(api.pending().length,1);
api.settle(second,409,{detail:{outcome_confirmed:true,retry_same_operation_id:false}});
assert.equal(api.pending().length,0);
const bad=api.prepare(path,{...body,operation_id:'OWN262.INVALID'});api.settle(bad,422,{});
assert.equal(api.pending().length,0);
assert.throws(()=>boot('admin','http://127.0.0.1:8088',{...storage,setItem(){throw new Error('quota')}}).prepare(path,body));
console.log('PASS262 persistedbeforefetch/reloadsameIDandcodes/changedbodydenied/503-403-old422retained/scopes-separated/multiplepending/clearonlyexactconfirmed/new422/quota-before-send');
