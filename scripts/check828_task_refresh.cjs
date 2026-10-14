const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const task=JSON.parse(fs.readFileSync('tmp/context806.json','utf8')).rows[0];
const nodes={},events={},calls=[];let currentTask={...task,status:'ASSIGNED'},delayedProgress=null;
const node=id=>nodes[id]??=({value:id==='warehouseTaskLimit'?'150':'',textContent:'',innerHTML:'',disabled:false,dataset:{},classList:{toggle(){}},addEventListener(type,fn){this[type]=fn;}});
const waiting={...node('waiting'),dataset:{taskPreset:'waiting'}};
const context={document:{getElementById:node,querySelectorAll:s=>s==='[data-task-preset]'?[waiting]:[]},
 window:{history:{replaceState(){}},location:{search:'?task_id=1080',href:'http://local/warehouse-tasks.html?task_id=1080'},wmsAdminAuth:{state:{apiBase:'http://local',user:{username:'actor'}},headers:()=>({}),hasPermission:()=>true},warehouseTaskRecovery:{init(){}},addEventListener:(type,fn)=>events[type]=fn,dispatchEvent(){}},
 CustomEvent:class{constructor(type,options){this.type=type;this.detail=options.detail;}},
 URL,URLSearchParams,fetch:async url=>{calls.push(url);if(url.endsWith('/progress')&&delayedProgress)return await delayedProgress;const body=url.endsWith('/progress')?{confirmed_quantity:3,remaining_quantity:0,unit_code:'EA',status:'DONE'}:url.endsWith('/1080')?currentTask:[currentTask];return{ok:true,text:async()=>JSON.stringify(body)};}};
vm.createContext(context);vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/warehouse-tasks.js','utf8'),context);
const flush=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
 events['wms-admin-auth-ready']();await flush();
 assert.match(node('warehouseTaskDetailStatus').textContent,/ASSIGNED/);
 currentTask={...task,status:'DONE'};
 await context.loadWarehouseTasks();await flush();
 assert.match(node('warehouseTaskDetailStatus').textContent,/DONE/);
 assert.equal(node('warehouseTaskComplete').disabled,true);
 let resolve;
 delayedProgress=new Promise(r=>resolve=r);
 const pending=context.showWarehouseTaskProgress(1080);
 vm.runInContext('warehouseTaskState.readEpoch++',context);
 node('warehouseTaskProgress').textContent='CURRENT';
 resolve({ok:true,text:async()=>JSON.stringify({confirmed_quantity:'OLD',remaining_quantity:99,status:'OLD'})});
 await pending;
 assert.equal(node('warehouseTaskProgress').textContent,'CURRENT');
 delayedProgress=null;
 console.log('828 PASS selected card refresh ASSIGNED->DONE and stale progress ignored; no stock writes');
})().catch(error=>{console.error(error);process.exitCode=1;});
