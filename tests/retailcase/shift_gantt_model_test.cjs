const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'../..'),ts=require(path.join(root,'admin/wms_admin_frontend/node_modules/typescript'));
const base=path.join(root,'admin/wms_admin_frontend/src/features/platform/workspaces'),cache={};
function load(rel){if(cache[rel])return cache[rel];const exports={};cache[rel]=exports;vm.runInNewContext(ts.transpileModule(fs.readFileSync(path.join(base,rel),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,jsx:ts.JsxEmit.ReactJSX}}).outputText,{exports,require:id=>id==='./executionState'?load('shift/executionState.ts'):{},Set,Map,Date,Intl,Number});return exports;}
const state=load('shift/executionState.ts'),risk=load('shift/risks.ts'),flow=load('shift/WaveFlowScene.tsx'),model=load('resources/timelineModel.ts');
let count=0;function check(name,run){run();console.log('PASS',name);count++;}
const complete=()=>({wave_id:1,readiness:{data:{blockers:[]},error:''},pick:{data:{released_at:'2026-10-15T10:00:00Z',tasks:[]},error:''},time:{data:{plan_status:'APPROVED'},error:''},replenishment:{data:[],error:''}});
check('all actual open CASE states stay visible',()=>{for(const s of ['NEW','ASSIGNED','IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT','PICKED'])assert.equal(state.isOpenCase(s),true,s);});
check('terminal and invented statuses not counted as current CASE',()=>{for(const s of ['CLOSED','CANCELLED','SHIPPED','CLAIMED','STARTED'])assert.equal(state.isOpenCase(s),false,s);});
check('native shortage decision states become risks',()=>{for(const status of ['CREATED','PENDING_APPROVAL'])assert.equal(risk.executionRisks([],[{status,case_pick_short_id:3,pick_wave_id:1,case_pick_task_id:2,articul:'SKU',short_qty:1}]).length,1);});
check('resolved or unrelated statuses do not become pending shortage risks',()=>{for(const status of ['APPROVED','REJECTED','CANCELLED','NEW','OPEN'])assert.equal(risk.executionRisks([],[{status}]).length,0);});
check('successful empty sources are a complete preparation read',()=>assert.equal(state.preparationComplete(complete()),true));
check('each missing/failed preparation source prevents green CLEAR',()=>{for(const source of ['readiness','pick','time','replenishment']){for(const bad of [{data:null,error:''},{data:[],error:'NO_ACCESS'}]){const d=complete();d[source]=bad;assert.equal(state.preparationComplete(d),false);assert.equal(flow.stageOf({status:'LAUNCHED'},d),'UNREAD');assert.ok(risk.waveRisks({pick_wave_id:1,status:'LAUNCHED'},d).some(r=>r.key.includes('UNKNOWN')));}}});
check('complete empty blockers allow CLEAR not a launch command',()=>assert.equal(flow.stageOf({status:'LAUNCHED'},complete()),'CLEAR'));
check('future PREVIEW remains preparation even before source read',()=>assert.equal(flow.stageOf({status:'PREVIEW'},undefined),'PREP'));
check('unknown detail never clears',()=>assert.equal(flow.stageOf({status:'LAUNCHED'},undefined),'UNREAD'));
check('Gantt quantities never sum unlike SKU and bindings do not duplicate event count',()=>{const a={event_id:'A',quantity:{value:'9007199254740993',uom:'EA'}},b={event_id:'B',quantity:{value:'1',uom:'EA'}};const r={bars:[{event:a},{event:b}],conflicts:0};const s=model.summarize({events:[a,b]},[r,r]);assert.equal(s.events,2);assert.equal(s.quantifiedEvents,2);assert.equal(s.qty,undefined);});
check('real adapter retains all four resource families without fabricating quantity',()=>{
 const adapter=load('resources/timelineAdapter.ts');
 const t=adapter.adaptTimeline({warehouse_id:1,start_at:'2026-10-15T00:00:00Z',finish_at:'2026-10-16T00:00:00Z',observed_at:'2026-10-15T10:00:00Z',warehouse_time_zone:null,
 resources:['REACHTRUCK','CASE_PICKER','DOCK','VEHICLE'].map((kind,i)=>({resource_id:String(i),kind,label:kind,warehouse_id:1,source_state:null,availability:'UNKNOWN'})),events:[],unscheduled:[],assignments:[],sources:[],overlap_candidates:[]});
 assert.deepEqual(Array.from(t.resources,r=>r.resource_type),['REACH_TRUCK','PICKER','DOCK','VEHICLE']);
 assert.ok(t.resources.every(r=>r.availability.length===0&&r.last_signal===null));
});
console.log(count+' shift/Gantt source-model checks PASS');
