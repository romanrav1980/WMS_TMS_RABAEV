const fs=require("fs"),vm=require("vm"),assert=require("assert");
class Element{constructor(){this.children=[];this.textContent="";this.value="";this.dataset={};}replaceChildren(...v){this.children=v;}append(...v){this.children.push(...v);}appendChild(v){this.children.push(v);}addEventListener(){}setAttribute(){}}
const elements=new Map(),requests=[];
const document={getElementById:id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);},createElement:()=>new Element()};
const auth={state:{apiBase:"http://own",user:null},headers:()=>({}),hasPermission:()=>false};
const window={wmsAdminAuth:auth,addEventListener(){},dispatchEvent(){},location:{search:"",hash:""}};
const ctx=vm.createContext({window,document,CustomEvent:class{},URLSearchParams,crypto:{randomUUID:()=>"own"},console,fetch:(url)=>new Promise(resolve=>requests.push({url,resolve}))});
vm.runInContext(fs.readFileSync("wiki-raw/wms_admin_ui_reference/customer-orders.js","utf8"),ctx);
const response=id=>({ok:true,text:async()=>JSON.stringify({customer_order_id:id,order_no:"Own"+id,status:"OPEN",rows:[]})});
(async()=>{
auth.state.user={username:"admin"};
const first=ctx.loadOrderDetail(1),second=ctx.loadOrderDetail(2);
requests[1].resolve(response(2));await second;
assert.equal(vm.runInContext("orderState.detail.customer_order_id",ctx),2);
requests[0].resolve(response(1));await first;
assert.equal(vm.runInContext("orderState.detail.customer_order_id",ctx),2);
const third=ctx.loadOrderDetail(3);auth.state.user={username:"other"};
requests[2].resolve(response(3));await third;
assert.equal(vm.runInContext("orderState.detail",ctx),null);
assert(!document.getElementById("orderDetails").textContent.includes("Own3"));
console.log("PASS1024 oldorder late response/newcurrent order/authchange do not overwrite current detail");
})().catch(e=>{console.error(e);process.exit(1);});
