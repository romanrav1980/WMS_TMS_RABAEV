const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const task=JSON.parse(fs.readFileSync('tmp/context806.json','utf8')).rows[0];
const nodes={},events={},calls=[];
const node=id=>nodes[id]??=({value:id==='warehouseTaskLimit'?'150':'',textContent:'',innerHTML:'',disabled:false,dataset:{},classList:{toggle(){}},addEventListener(type,fn){this[type]=fn;}});
const waiting={...node('waiting'),dataset:{taskPreset:'waiting'}};
const context={document:{getElementById:node,querySelectorAll:s=>s==='[data-task-preset]'?[waiting]:[]},
 window:{history:{replaceState(){}},location:{search:'?task_id=1080',href:'http://local/warehouse-tasks.html?task_id=1080'},wmsAdminAuth:{state:{apiBase:'http://local',user:{username:'actor'}},headers:()=>({}),hasPermission:()=>true},warehouseTaskRecovery:{init(){}},addEventListener:(type,fn)=>events[type]=fn,dispatchEvent(){}},
 CustomEvent:class{constructor(type,options){this.type=type;this.detail=options.detail;}},
 URL,URLSearchParams,fetch:async url=>{calls.push(url);const body=url.endsWith('/progress')?{confirmed_quantity:3,remaining_quantity:0,unit_code:'EA',status:'DONE'}:url.endsWith('/1080')?task:url.includes('source_doc_type=ST_DEFER')?[task]:[];return{ok:true,text:async()=>JSON.stringify(body)};}};
vm.runInNewContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/warehouse-tasks.js','utf8'),context);
const flush=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
 assert.equal(typeof waiting.click,'function');
 assert.equal(context.formatQty('1000000000000.123456789','KG'),'1000000000000.123456789 KG');
 assert.equal(context.formatQty('0.000000001','KG'),'0.000000001 KG');events['wms-admin-auth-ready']();await flush();
 assert.match(node('warehouseTaskDetailStatus').textContent,/DONE/);
 assert.match(node('warehouseTaskDetailPallet').textContent,/LEGACY.SAP.688/);
 assert.equal(node('warehouseTaskComplete').disabled,true);
 waiting.click({preventDefault(){}});await flush();
 assert.equal(node('warehouseTaskDocType').value,'ST_DEFER');
 assert.equal(node('warehouseTaskType').value,'PUTAWAY');
 assert.equal(node('warehouseTaskSource').value,'MANUAL');
 assert(calls.some(url=>url.includes('source_doc_type=ST_DEFER')&&url.includes('task_type=PUTAWAY')));
 assert.match(node('warehouseTaskRows').innerHTML,/1080/);
 console.log('810 PASS real UI handler -> existing API filter; outside-page deep link; DONE cannot complete');
})().catch(error=>{console.error(error);process.exitCode=1;});
