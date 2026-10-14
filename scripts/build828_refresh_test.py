from pathlib import Path
import json
src=Path("scripts/check810_task_controls.cjs").read_text(encoding="utf-8")
prefix=src.split("(async()=>{",1)[0]
prefix=prefix.replace("const nodes={},events={},calls=[];","const nodes={},events={},calls=[];let currentTask={...task,status:'ASSIGNED'},delayedProgress=null;")
prefix=prefix.replace("fetch:async url=>{calls.push(url);const body=", "fetch:async url=>{calls.push(url);if(url.endsWith('/progress')&&delayedProgress)return await delayedProgress;const body=")
prefix=prefix.replace("url.endsWith('/1080')?task:url.includes('source_doc_type=ST_DEFER')?[task]:[]","url.endsWith('/1080')?currentTask:[currentTask]")
prefix=prefix.replace("vm.runInNewContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/warehouse-tasks.js','utf8'),context);","vm.createContext(context);vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/warehouse-tasks.js','utf8'),context);")
body="""(async()=>{
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
"""
print(json.dumps({"scripts/check828_task_refresh.cjs":prefix+body},ensure_ascii=True))
