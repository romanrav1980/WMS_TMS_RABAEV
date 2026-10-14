const fs=require('fs'),vm=require('vm'),assert=require('assert');
const store=new Map(),nodes=new Map(),events=new Map(),posted=[];
function node(id){
 if(!nodes.has(id)) nodes.set(id,{value:'',textContent:'',disabled:false,listeners:{},children:[],
  addEventListener(type,fn){this.listeners[type]=fn},replaceChildren(...values){this.children=values},
  appendChild(child){this.children.push(child)},append(...children){this.children.push(...children)}});
 return nodes.get(id);
}
const auth={state:{apiBase:'http://own',user:{username:'admin'}},headers:()=>({}),hasPermission:()=>true};
const context={crypto:require('crypto'),URLSearchParams,location:{search:''},Date,console,
 localStorage:{get length(){return store.size},key(i){return [...store.keys()][i]??null},
 getItem:k=>store.get(k)??null,setItem:(k,v)=>store.set(k,v),removeItem:k=>store.delete(k)},
 CustomEvent:class{constructor(type,options){this.type=type;this.detail=options?.detail}},
 document:{getElementById:node,createElement:()=>node('created'+Math.random())},
 window:{wmsAdminAuth:auth,addEventListener(type,fn){events.set(type,[...(events.get(type)||[]),fn])},
 dispatchEvent(event){for(const fn of events.get(event.type)||[])fn(event)}},
 fetch:async(url,options)=>{
  let data,status=200;
  if(options.method==='POST'){
   posted.push(JSON.parse(options.body));status=201;data={pallet_identifier:'OWN262.UI',quantity:'3',task_id:999,receive_cell:'A',putaway_cell:'B'};
  }else data=url.endsWith('/supply-orders')?[]:{order_id:'own262',order_number:'OWN262',ware_id:1,lines:[]};
  return {ok:true,status,json:async()=>data};
 }};
vm.runInNewContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/receiving-intent.js','utf8'),context);
const body={operation_id:'OWN262.UI.ID',sscc:'OWN262.UI',quantity:'3',supplier_batch:'B',expiry_date:'2027-01-01',
 units:[{unit_id:'one',codes:[{system:'CRPT',profile:'TOBACCO',code:'raw-unique-code'}]}]};
context.window.wmsReceiptIntent.prepare('/api/receiving/supply-orders/own262/pallets',body);
auth.state.user=null;
vm.runInNewContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/receiving.js','utf8'),context);
auth.state.user={username:'admin'};node('receiptPendingSelect').value=body.operation_id;
(async()=>{
 await node('receiptRetryPending').listeners.click();
 assert.equal(posted.length,1);assert.deepEqual(posted[0],body);
 assert.equal(context.window.wmsReceiptIntent.pending().length,0);
 assert.ok(node('receiptMessage').textContent.includes('999'));
 console.log('PASS262 actualreceiving handler restores storedsameID/codes/body and clears onlyserverconfirmedresult; DOM/fetch doubles, OracleHTTP replay separately proved');
})().catch(e=>{console.error(e);process.exitCode=1});
