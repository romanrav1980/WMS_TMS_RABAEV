const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const nodes={},events={},dispatched=[],requests=[];
function element(){return {value:'',textContent:'',children:[],dataset:{},disabled:false,hidden:false,handlers:{},
 addEventListener(type,fn){this.handlers[type]=fn;},appendChild(n){n.parent=this;this.children.push(n);return n;},contains(n){return n===this||this.children.some(child=>child.contains(n));},closest(){return this.dataset.receiptSelectable?this:this.parent?.closest();},
 replaceChildren(...list){this.children=list;for(const n of list)n.parent=this;},get firstElementChild(){return this.children[0];},focus(){}};}
function node(id){return nodes[id]??=(element());}
const source={order_id:'SOURCE',order_number:'ERP',ware_id:1,receipt_allowed:true,lines:[
 {line_number:'1',articul:'SKU',name:'Product',planned_qty:'3',accepted_qty:'3',remaining_qty:'0',suggested_pallet_quantity:'0'},
 {line_number:'2',articul:'SKU',name:'Product',planned_qty:'3',accepted_qty:'0',remaining_qty:'3',suggested_pallet_quantity:'3'}]};
const policy={configured:true,marking_required:true,profiles:[{system_code:'CRPT',profile_code:'TOBACCO',scan_mode:'UNIT'}]};
let delayed=null;
const window={wmsAdminAuth:{state:{apiBase:'http://local',user:{username:'a'}},headers:()=>({}),hasPermission:()=>true},
 wmsReceiptIntent:{scope:()=> 'a',pending:()=>[],damaged:()=>[]},addEventListener:(t,f)=>events[t]=f,
 dispatchEvent:e=>dispatched.push(e)};
const context={document:{getElementById:node,createElement:element},window,
 location:{search:'?order_id=SOURCE&line_number=2'},URLSearchParams,Map,crypto:{randomUUID:()=> 'op'},
 CustomEvent:class{constructor(type,options={}){this.type=type;this.detail=options.detail;}},
 fetch:async(url)=>{requests.push(url);let body;if(url.endsWith('receiving-policy'))body=delayed?await delayed:policy;
 else if(url.endsWith('/SOURCE'))body=source;else body=[source];return {ok:true,status:200,json:async()=>body};}};
source.receipt_allowed=false;source.lines[0].line_number=1;source.lines[1].line_number=2;
vm.createContext(context);vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/receiving.js','utf8'),context);
const flush=()=>new Promise(r=>setImmediate(r));
async function clickLine(index){const row=node('receiptLines').children[index];const button=row.children.at(-1).children[0];node('receiptLines').handlers.click({type:'click',target:button});await flush();}
(async()=>{
 await flush();await flush();await flush();
 assert.equal(dispatched.filter(e=>e.type==='wms-receipt-line-selected').at(-1).detail.line_number,2);
 assert.equal(node('receiptLines').children[1].dataset.selected,'true');
 assert.equal(node('receiptConfirm').disabled,true);
 assert.equal(node('receiptIssueLabel').disabled,true);
 assert.match(node('receiptMessage').textContent,/Основание закрыто/);
 assert.equal(requests.filter(r=>r.includes('/pallets')||r.includes('/labels')).length,0);
 console.log('PASS1036 alias/explicitnumericline/stringdataset/currentpolicy/closedreceipt+labeldisabled/no writes');
})().catch(e=>{console.error(e);process.exitCode=1;});
