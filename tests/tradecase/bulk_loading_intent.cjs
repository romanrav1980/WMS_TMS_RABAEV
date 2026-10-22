// Real loading journal: keep the exact bulk command through reload and scope changes.
const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const storage=new Map(),out='runtime/test-evidence/tradecase/2026-10-22/T07';
const localStorage={getItem:k=>storage.get(k)??null,setItem:(k,v)=>storage.set(k,String(v)),removeItem:k=>storage.delete(k)};
function boot(){
 const window={wmsAdminAuth:{state:{apiBase:'http://fixture',user:{username:'first'}}}};
 const context=vm.createContext({window,localStorage,crypto:crypto.webcrypto});
 for(const file of ['wave-command-intent.js','transport-loading-intent.js'])vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/'+file,'utf8'),context);
 return window;
}
let window=boot();const scope=()=>`load:${window.wmsAdminAuth.state.user.username}`;
let journal=window.wmsLoadingIntent.create(scope);
const original={path:'/api/transport/loading/confirm-bulk-box',trip_id:1,body:{operation_id:'BULK.ORIGINAL',transport_task_id:1,identifier:'BOX',measurements:{gross_weight_kg:'2.2'}}};
const saved=journal.save(original),wire=saved.raw;
window=boot();journal=window.wmsLoadingIntent.create(scope);
assert.equal(journal.read().raw,wire);assert.equal(journal.read().value.body.operation_id,'BULK.ORIGINAL');
assert.throws(()=>journal.save({...original,body:{...original.body,measurements:{gross_weight_kg:'100'}}}));assert.equal(journal.read().raw,wire);
assert.equal(window.wmsLoadingIntent.confirms(original,{operation_id:'OTHER'}),false);assert.equal(journal.read().raw,wire);
window.wmsAdminAuth.state.user.username='second';assert.equal(journal.read().value,null);assert.throws(()=>journal.settle(saved));
window.wmsAdminAuth.state.user.username='first';assert.equal(journal.read().raw,wire);
assert.equal(window.wmsLoadingIntent.confirms(original,{operation_id:'BULK.ORIGINAL'}),true);journal.settle(journal.read());assert.equal(journal.read().value,null);
const report={status:'PASS',checks:['bulk journal survives reload byte-for-byte','changed measurements cannot replace pending command','mismatched receipt retains command','other user cannot read or settle original command','return to original user restores exact command','matching receipt permits settlement'],business_writes:0};
fs.writeFileSync(out+'/bulk-intent.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));
