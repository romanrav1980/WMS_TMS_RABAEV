const fs=require("fs"),vm=require("vm"),assert=require("assert");
class Element{constructor(){this.children=[];this.value="";this.textContent="";this.dataset={};this.disabled=false;}set innerHTML(value){this.children=[];this._html=value;}get innerHTML(){return this._html||"";}replaceChildren(...v){this.children=v;}appendChild(v){this.children.push(v);}addEventListener(){}setAttribute(){}}
const el=new Map(),requests=[],auth={state:{apiBase:"http://own",user:{username:"admin"}},headers:()=>({}),hasPermission:()=>false};
const document={getElementById:id=>{if(!el.has(id))el.set(id,new Element());return el.get(id);},createElement:()=>new Element()};
document.getElementById("orderLimit").value="2";
const window={wmsAdminAuth:auth,addEventListener(){},dispatchEvent(){},location:{search:"",hash:""}};
const ctx=vm.createContext({window,document,URLSearchParams,CustomEvent:class{},crypto:{randomUUID:()=>"own"},console,fetch:url=>new Promise(resolve=>requests.push({url,resolve}))});
vm.runInContext(fs.readFileSync("wiki-raw/wms_admin_ui_reference/customer-orders.js","utf8"),ctx);
const response=(ids,ok=true)=>({ok,text:async()=>JSON.stringify(ok?ids.map(id=>({customer_order_id:id,order_no:"Own"+id})):({detail:"Request failed"}))});
async function complete(action,ids,ok=true){const promise=action();requests.at(-1).resolve(response(ids,ok));await promise;}
(async()=>{
 await complete(()=>ctx.loadOrders(),[12,11]);
 assert(!document.getElementById("orderPageNext").disabled);
 await complete(()=>ctx.orderPage("next"),[10,9]);assert(requests.at(-1).url.includes("before_id=11"));
 await complete(()=>ctx.orderPage("previous"),[12,11]);assert(!requests.at(-1).url.includes("before_id="));
 await complete(()=>ctx.orderPage("next"),[],false);
 assert(document.getElementById("orderPageNext").disabled);
 assert(!document.getElementById("orderPagePrevious").disabled);
 await complete(()=>ctx.orderPage("previous"),[12,11]);
 document.getElementById("orderNo").value="Changed";
 await complete(()=>ctx.orderPage("next"),[8]);assert(!requests.at(-1).url.includes("before_id="));assert(document.getElementById("orderPageNext").disabled);
 const pending=ctx.loadOrders();auth.state.user={username:"other"};requests.at(-1).resolve(response([99]));await pending;
 assert(!document.getElementById("orderRows").children.length);
 console.log("PASS1048 actual JS paging/previous/filter reset/failure no stale rows/changedactor");
})().catch(e=>{console.error(e);process.exit(1);});
