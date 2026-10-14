import type {PendingReceipt} from "./contracts";
const object=(v:unknown):v is Record<string,unknown>=>!!v&&typeof v==="object"&&!Array.isArray(v);
const text=(v:unknown,n:number):v is string=>typeof v==="string"&&v.length>0&&v.length<=n;
const decimal=(v:unknown)=>typeof v==="string"&&/^[0-9]{1,18}(\.[0-9]{1,9})?$/.test(v);
function scans(v:unknown,aggregate:boolean){
 return v===undefined||(Array.isArray(v)&&v.length<=(aggregate?1000:20000)&&v.every(x=>object(x)&&text(x.system_code,40)&&text(x.profile_code,80)&&new TextEncoder().encode(x.profile_code).length<=80&&text(x.code,4000)&&new TextEncoder().encode(x.code).length<=4000&&(!aggregate||["BOX","PALLET"].includes(String(x.level)))&&(x.disposition===undefined||["ACCEPTED","REFUSED","DAMAGED"].includes(String(x.disposition)))));
}
export function parseReceiptIntent(raw:string|null,address:string):PendingReceipt|null{
 if(raw===null)return null;
 const v:unknown=JSON.parse(raw);
 if(!object(v)||!object(v.body)||(v.confirmedRejection!==undefined&&typeof v.confirmedRejection!=="boolean"))throw Error("INVALID_RECEIPT_INTENT");
 const b=v.body;
 if(!text(b.operation_id,100)||!/^[A-Za-z0-9_.:-]+$/.test(b.operation_id)||!text(b.load_operation_id,100)||b.store_address!==address||!text(b.scan_place,200)||typeof b.expected_composition_signature!=="string"||!/^[A-F0-9]{64}$/.test(b.expected_composition_signature)||typeof b.before_cameras!=="boolean"||!scans(b.scans,false)||!scans(b.aggregation_scans,true))throw Error("INVALID_RECEIPT_INTENT");
 if(b.observations!==undefined&&(!Array.isArray(b.observations)||b.observations.length>200||!b.observations.every(x=>object(x)&&text(x.lot_uid,200)&&["accepted","missing","refused","damaged","extra"].every(k=>decimal(x[k]??"0")))))throw Error("INVALID_RECEIPT_INTENT");
 if(b.unloading!==undefined&&(!object(b.unloading)||!text(b.unloading.start_operation_id,100)||!["ROLL_CAGE","PALLET","MANUAL"].includes(String(b.unloading.method))||typeof b.unloading.rolling_difficult!=="boolean"||typeof b.unloading.loader_present!=="boolean"||!text(b.unloading.evidence_reference,100)))throw Error("INVALID_RECEIPT_INTENT");
 return v as unknown as PendingReceipt;
}
