const fs=require("fs"),vm=require("vm"),ts=require("../admin/wms_admin_frontend/node_modules/typescript");
const source=fs.readFileSync("admin/wms_admin_frontend/src/features/delivery/receiptIntentValidation.ts","utf8");
const compiledExports={};vm.runInNewContext(ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText,{exports:compiledExports,TextEncoder});
const parse=compiledExports.parseReceiptIntent;
const body={operation_id:"STORE:727",load_operation_id:"LOAD:727",store_address:"OWN",scan_place:"legacy-pallet",expected_composition_signature:"A".repeat(64),before_cameras:true,aggregation_scans:[{system_code:"CRPT",profile_code:"TOBACCO",code:"original",level:"PALLET",disposition:"ACCEPTED"}]};
if(parse(JSON.stringify({body}),"OWN").body.operation_id!==body.operation_id)throw Error("Valid body");
for(const raw of ["{",JSON.stringify({body:{...body,store_address:"OTHER"}}),JSON.stringify({body:{...body,aggregation_scans:{}}}),JSON.stringify({body:{...body,aggregation_scans:[{...body.aggregation_scans[0],profile_code:"я".repeat(41)}]}}),JSON.stringify({body:{...body,before_cameras:"true"}})]){
 let refused=false;try{parse(raw,"OWN");}catch{refused=true;}if(!refused)throw Error("Malformed accepted");
}
console.log("PASS727 receipt intent original body/current address/array shape/80UTF8 bytes/strict bool preserved");
