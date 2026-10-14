const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('wiki-raw/wms_admin_ui_reference/st-deferral.js','utf8');
function setup(raw,fetcher){
 const nodes={},storage=new Map(),events={};
 const el=id=>nodes[id]??=( {value:'',textContent:'',disabled:false,hidden:false,
  replaceChildren(){},append(){},addEventListener(type,fn){this[type]=fn;}});
 const key='wms-st-deferral:'+JSON.stringify(['http://local','actor']);
 if(raw!==null)storage.set(key,raw);
 const auth={state:{apiBase:'http://local',user:{username:'actor'}},headers:()=>({})};
 const localStorage={getItem:k=>storage.get(k)??null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)};
 vm.runInNewContext(source,{window:{wmsAdminAuth:auth,addEventListener:(type,fn)=>events[type]=fn,dispatchEvent(){}},
  document:{getElementById:el,createElement:()=>({append(){}})},localStorage,fetch:fetcher,URLSearchParams,
  crypto:{randomUUID:()=> 'test-id'},CustomEvent:class{constructor(type,options){this.type=type;this.detail=options.detail;}}});
 return {el,storage,key,events};
}
(async()=>{
 let calls=0;
 const malformed=setup('{',async()=>{calls++;throw Error('unreachable');});
 assert.equal(malformed.el('sdSave').disabled,true);
 await malformed.el('sdRetry').click();
 assert.equal(calls,0);assert.equal(malformed.storage.get(malformed.key),'{');
 malformed.el('sdSt').value='ST-OWN';malformed.el('sdSt').input();
 const context={st_number:'ST-OWN',warehouse_id:1,source_trip_id:10,source_trip:{shipment_date:'2026-10-14'},members:[],version:1,source_hash:'a'.repeat(64)};
 const recovery=setup('{',async()=>({ok:true,text:async()=>JSON.stringify(context)}));
 recovery.el('sdSt').value='ST-OWN';recovery.el('sdSt').input();
 await recovery.el('sdRecover').click();
 assert.equal(recovery.storage.has(recovery.key),false);
 assert.equal([...recovery.storage].find(([k])=>k.includes(':archive:'))[1],'{');
 const cmd={operation_id:'STDEFER:test',st_number:'ST-OWN',target_trip_id:11,expected_version:1,source_hash:'a'.repeat(64),reason:'reason test',reference:'reference test'};
 const unchanged=JSON.stringify(cmd);let current;
 current=setup(unchanged,async()=>{current.storage.set(current.key,'other-tab-command');return {ok:true,text:async()=>JSON.stringify({operation_id:cmd.operation_id,stock_changed:false})};});
 await current.el('sdRetry').click();
 assert.equal(current.storage.get(current.key),'other-tab-command');
 assert.match(current.el('sdMessage').textContent,/другой вкладке/);
 console.log('800 PASS malformed blocks send; archive+authorised reread; other-tab command preserved');
})().catch(error=>{console.error(error);process.exitCode=1;});
