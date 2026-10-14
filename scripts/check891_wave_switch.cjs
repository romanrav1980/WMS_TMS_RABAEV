const fs=require('fs'),vm=require('vm'),assert=require('assert/strict'),events={},nodes=new Map();
function node(id){if(!nodes.has(id))nodes.set(id,{value:'',textContent:'',innerHTML:'',addEventListener(){}});return nodes.get(id);}
node('waveReplenishmentLimit').value='100';
let resolveA,holdA=false,saved=null;
const firstWave={pick_wave_id:1,wave_code:'A',ware_id:7},secondWave={pick_wave_id:2,wave_code:'B',ware_id:7};
const context={document:{getElementById:node,querySelectorAll:()=>[]},
 window:{location:{search:''},wmsAdminAuth:{state:{apiBase:'http://local',user:{username:'actor'}},headers:()=>({}),hasPermission:()=>true},
 wmsWavePickIntent:{read:()=>({value:saved})},addEventListener:(type,fn)=>events[type]=fn,dispatchEvent:event=>{if(events[event.type])events[event.type](event);}},
 location:{search:''},CustomEvent:class{constructor(type,args){this.type=type;this.detail=args.detail;}},URLSearchParams,
 fetch:async url=>{let body=[];
 if(url.endsWith('/1/header'))body=firstWave;if(url.endsWith('/2/header'))body=secondWave;
 if(url.includes('/1/replenishment-tasks')&&holdA)return await new Promise(resolve=>resolveA=resolve);
 if(url.includes('/2/replenishment-tasks'))body=[{pick_wave_replenish_task_id:22,status:'DONE',articul:'SKU-B',qty:'3'}];
 return{ok:true,text:async()=>JSON.stringify(body)};}};
vm.createContext(context);vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/wave-replenishment.js','utf8'),context);
const flush=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
 holdA=true;const old=context.selectWave(1);await flush();assert.ok(resolveA);
 await context.selectWave(2);
 assert.match(node('waveReplenishmentSelectionText').textContent,/Волна #2/);
 resolveA({ok:true,text:async()=>JSON.stringify([{pick_wave_replenish_task_id:11,status:'DONE',articul:'SKU-A',qty:'9'}])});await old;
 assert.match(node('waveReplenishmentTaskRows').innerHTML,/SKU-B/);
 assert.doesNotMatch(node('waveReplenishmentTaskRows').innerHTML,/SKU-A/);
 saved={wave:2};await context.selectWave(1);
 assert.match(node('waveReplenishmentStatusText').textContent,/решение волны 2/);
 assert.match(node('waveReplenishmentTaskRows').innerHTML,/SKU-B/);
 console.log('891 PASS deep header selection, delayed old wave ignored, existing pending wave blocks new choice; no stock writes');
})().catch(error=>{console.error(error);process.exitCode=1;});
