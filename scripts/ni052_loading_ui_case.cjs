/* Target changed UI submission branches; no service or stock writes. */
const fs=require("node:fs"),vm=require("node:vm"),assert=require("node:assert/strict");
const nodes=new Map(),posted=[],storage=new Map();
function element(id){if(!nodes.has(id))nodes.set(id,{value:"",textContent:"",listeners:{},addEventListener(k,f){this.listeners[k]=f;},replaceChildren(){},append(){}});return nodes.get(id);}
const snapshot={root:"HU:OWN",nodes:[{kind:"CONTAINER",version:3}],cell:"OWN-CELL",leaf_count:1,top_place_count:1};
const context={document:{getElementById:element,querySelectorAll:()=>[],createElement:()=>({append(){}})},
 window:{wmsAdminAuth:{state:{apiBase:"http://own",user:{username:"admin"}},headers:()=>({})},addEventListener(){}},
 localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},
 crypto:require("node:crypto"),fetch:async(url,options)=>{
  let data;
  if(options.method==="POST"){posted.push({url,body:JSON.parse(options.body)});data={operation_id:posted.at(-1).body.operation_id};}
  else if(url.includes("/status"))data={trip:{id:9,transport:"TRUCK",dock:"DOCK",condition:"planned"},members:[],loaded_place_count:0,pending_st_ids:[]};
  else if(url.includes("reconciliation-preview"))data={snapshot,shipping_operation_id:"OLD.OP",composition_signature:"A".repeat(64),already_reconciled:false};
  else data={snapshot,shipment_identifier:"ST:OWN",composition_signature:"A".repeat(64)};
  return {ok:true,status:200,json:async()=>data};
 }};
vm.runInNewContext(fs.readFileSync("wiki-raw/wms_admin_ui_reference/load-box-weights.js","utf8"),context);
vm.runInNewContext(fs.readFileSync("wiki-raw/wms_admin_ui_reference/transport-loading.js","utf8"),context);
async function click(id){await element(id).listeners.click();}
(async()=>{
 element("tripId").value="9";await click("tripLoad");
 for(const [id,value] of Object.entries({loadScan:"HU:OWN",loadCell:"OWN-CELL",loadVehicle:"TRUCK",loadDock:"DOCK",loadGross:"10",loadWidth:"1",loadDepth:"1",loadHeight:"1"}))element(id).value=value;
 for(const [mode,input] of [["SINGLE","ST:OWN"],["RECONCILE","OLD.OP"]]){
  element("loadMode").value=mode;element(mode==="SINGLE"?"loadShipment":"loadOriginalOperation").value=input;
  await click("loadComposition");await click("loadConfirm");
  assert.equal(posted.at(-1).body.identifier,input,element("loadStatus").textContent);
  assert.equal(posted.at(-1).body.expected_composition_signature,"A".repeat(64));
  assert.ok(posted.at(-1).url.endsWith(mode==="SINGLE"?"/confirm-single":"/confirm-reconciliation"));
 }
 assert.equal(posted.length,2);
 assert.equal(storage.size,0);
 console.log("PASS actual UI handlers construct standalone/reconciliation frozen submissions and clear confirmed intent");
})().catch(error=>{console.error(error);process.exitCode=1;});
