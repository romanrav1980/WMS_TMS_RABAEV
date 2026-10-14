const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const listeners={},nodes={};
function node(){return{value:'',textContent:'',disabled:false,children:[],dataset:{},appendChild(n){this.children.push(n)},replaceChildren(...n){this.children=n},addEventListener(type,fn){this[type]=fn}};}
for(const key of ['input','p','.nearest-resource-results','[data-action="candidates"]','[data-action="dispatch-nearest"]'])nodes[key]=node();
nodes['[data-action="candidates"]'].dataset.action='candidates';nodes['[data-action="dispatch-nearest"]'].dataset.action='dispatch-nearest';
const panel=node();panel.querySelector=s=>nodes[s];panel.querySelectorAll=()=>[nodes['[data-action="candidates"]'],nodes['[data-action="dispatch-nearest"]']];
const candidate={assigned_to:'<img src=x onerror=bad>',resource_id:7,equipment_id:8,last_cell:'A01',distance:'0.000000001',last_position_at:'2026-10-13T12:00:00+03:00'};
const context={document:{createElement:type=>type==='section'?panel:node(),querySelector:()=>({prepend(){}})},window:{wmsAdminAuth:{state:{apiBase:'http://local',user:{username:'actor'}},hasPermission:()=>true,headers:()=>({})},addEventListener:(type,fn)=>listeners[type]=fn},fetch:async(_url,opts)=>({ok:true,json:async()=>opts.method==='POST'?{task_id:4,status:'ASSIGNED',...candidate}:[candidate]}),loadWarehouseTasks:async()=>listeners['warehouse-task-selected']({detail:{task_id:4,status:'ASSIGNED'}})};
vm.runInNewContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/resource-nearest.js','utf8'),context);
(async()=>{
 listeners['warehouse-task-selected']({detail:{task_id:4,status:'ASSIGNED'}});
 assert.equal(nodes['[data-action="dispatch-nearest"]'].disabled,true);
 listeners['warehouse-task-selected']({detail:{task_id:4,status:'PLANNED'}});
 assert.equal(nodes['[data-action="dispatch-nearest"]'].disabled,false);
 await nodes['[data-action="dispatch-nearest"]'].click();
 const table=nodes['.nearest-resource-results'].children[0];
 assert(table&&table.children.length===2);
 assert.equal(table.children[1].children[0].children[0].textContent,candidate.assigned_to);
 assert.equal(table.children[1].children[0].children[4].textContent,'0.000000001');
 assert.equal(nodes['[data-action="dispatch-nearest"]'].disabled,true);
 assert.match(nodes.p.textContent,/подтверждено сервером/);
 console.log('838 PASS current ASSIGNED dispatch disabled; confirmed result survives refresh; candidate text escaped/no distance rounding');
})().catch(error=>{console.error(error);process.exitCode=1});
