// Pure source-model checks. No browser, API, Oracle or business mutations.
const assert = require("node:assert/strict"), fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
const root = path.resolve(__dirname, "../.."), ts = require(path.join(root, "admin/wms_admin_frontend/node_modules/typescript"));
const source = fs.readFileSync(path.join(root, "admin/wms_admin_frontend/src/features/inventory/huTreeModel.ts"), "utf8");
const modelExports = {};
vm.runInNewContext(ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText, { exports: modelExports, Set, Map, Error, Number });
const { parseHuSnapshot: parse, massDescription: mass } = modelExports;
const fixture = () => ({ root: "INTERNAL-PALLET", warehouse: 1, cell: "A", ancestors: [], nodes: [
 {uid:"INTERNAL-PALLET",kind:"CONTAINER"}, {uid:"BOX",kind:"CONTAINER",type:"BOX"},
 {uid:"CASE:12",kind:"CASE",case_task_id:12,wave_id:3,status:"CLOSED"},
 {uid:"LOT",kind:"STOCK",article:"SKU",quantity:"0.000000000000001",base_uom:"EA"}],
 links:[{parent:"INTERNAL-PALLET",child:"BOX"},{parent:"BOX",child:"CASE:12"},{parent:"CASE:12",child:"LOT"}] });
let count=0;
function check(name, run) { run(); count++; console.log("PASS", name); }
check("generic pallet and CASE/BOX/STOCK preserve exact quantity",()=>assert.equal(parse(fixture()).nodes[3].quantity,"0.000000000000001"));
check("duplicate UID refused",()=>{const x=fixture();x.nodes.push(x.nodes[0]);assert.throws(()=>parse(x));});
check("multiple parents refused",()=>{const x=fixture();x.links.push({parent:x.root,child:"LOT"});assert.throws(()=>parse(x));});
check("cycle refused",()=>{const x=fixture();x.links=[{parent:"LOT",child:"BOX"},{parent:"BOX",child:"CASE:12"},{parent:"CASE:12",child:"LOT"}];assert.throws(()=>parse(x));});
check("missing child refused",()=>{const x=fixture();x.links[0].child="NO";assert.throws(()=>parse(x));});
check("disconnected node refused",()=>{const x=fixture();x.links.pop();assert.throws(()=>parse(x));});
check("missing root refused",()=>{const x=fixture();x.root="NO";assert.throws(()=>parse(x));});
check("depth 16 accepted and 17 refused",()=>{const x={root:"0",warehouse:1,cell:"A",ancestors:[],nodes:[],links:[]};for(let i=0;i<=16;i++){x.nodes.push({uid:String(i),kind:"CONTAINER"});if(i)x.links.push({parent:String(i-1),child:String(i)});}parse(x);x.nodes.push({uid:"17",kind:"STOCK"});x.links.push({parent:"16",child:"17"});assert.throws(()=>parse(x));});
check("more than 200 nodes refused",()=>{const x=fixture();x.nodes=Array.from({length:201},(_,i)=>({uid:String(i),kind:"STOCK"}));assert.throws(()=>parse(x));});
check("zero/foreign-format object IDs refused",()=>{for(const id of [0,-1,"12",1.1]){const x=fixture();x.nodes[2].case_task_id=id;assert.throws(()=>parse(x));}});
check("unsupported scale evidence shape refused",()=>{const x=fixture();x.nodes[2].scale_qc=[];assert.throws(()=>parse(x));});
check("GROSS without provenance stays unknown",()=>assert.equal(mass({uid:"x",kind:"CASE",gross_weight_kg:"10"}).value,"Неизвестна"));
check("master stock weight explicitly not observed",()=>assert.match(mass({uid:"x",kind:"STOCK",weight_kg:"10"}).basis,/учётных/));
check("scale_qc basis explicitly not outer GROSS",()=>assert.match(mass({uid:"x",kind:"CASE",gross_weight_kg:"10",scale_qc:{}}).basis,/не общий вес/));
check("historical flag preserved",()=>{const x=fixture();x.historical_composition=true;assert.equal(parse(x).historical_composition,true);});
check("malformed displayed scalar refused",()=>{const x=fixture();x.nodes[0].version={};assert.throws(()=>parse(x));});
check("physical unit bound refused",()=>{const x=fixture();x.physical_unit_count=10001;assert.throws(()=>parse(x));});
console.log(count+" pure HU model checks PASS");
