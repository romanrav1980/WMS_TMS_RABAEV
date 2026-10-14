import type { CustodyIntent } from "./custodyApi";
const object=(value:unknown):value is Record<string,unknown>=>!!value&&typeof value==="object"&&!Array.isArray(value);
const text=(value:unknown,max:number):value is string=>typeof value==="string"&&value.length>0&&value.length<=max;
const decimal=(value:unknown)=>typeof value==="string"&&/^[0-9]{1,18}(\.[0-9]{1,9})?$/.test(value);
function scans(value:unknown,aggregate:boolean):boolean {
 if(value===undefined)return true;
 return Array.isArray(value)&&value.length<=(aggregate?1000:20000)&&value.every(x=>object(x)&&
  text(x.system_code,40)&&text(x.profile_code,80)&&new TextEncoder().encode(x.profile_code).length<=80&&text(x.code,4000)&&
  (aggregate?["BOX","PALLET"].includes(String(x.level)):x.disposition===undefined||["ACCEPTED","REFUSED","DAMAGED"].includes(String(x.disposition))));
}
export function parseCustodyIntent(raw:string|null):CustodyIntent|null {
 if(raw===null)return null;
 const value:unknown=JSON.parse(raw);
 if(!object(value)||!["/handover","/pickup"].includes(String(value.path))||!object(value.body)||
  (value.confirmedRejection!==undefined&&typeof value.confirmedRejection!=="boolean"))throw Error("INVALID_SAVED_CUSTODY");
 const b=value.body;
 if(!text(b.operation_id,100)||!/^[A-Za-z0-9_.:-]+$/.test(b.operation_id)||
  !scans(b.scans,false)||!scans(b.aggregation_scans,true))throw Error("INVALID_SAVED_CUSTODY");
 if(value.path==="/handover"){
  if(!text(b.transport_operation_id,100)||!text(b.pallet_identifier,200)||!decimal(b.quantity)||
   !text(b.base_uom,20)||!decimal(b.gross_weight_kg)||typeof b.physical_places!=="number"||
   !Number.isInteger(b.physical_places)||b.physical_places<1||b.physical_places>200)throw Error("INVALID_SAVED_CUSTODY");
 }else if(!text(b.handover_operation_id,100)||!text(b.scan_vehicle,50)||!text(b.scan_pallet,200))throw Error("INVALID_SAVED_CUSTODY");
 return value as unknown as CustodyIntent;
}
