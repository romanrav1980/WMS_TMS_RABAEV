export type Credentials={username:string;password:string};
export type Holder="WAREHOUSE"|"VEHICLE"|"STORE";
export type TareOffer={operation_id:string;owner_ware_id:number;pallet_type_id:number;condition_code:"GOOD"|"DAMAGED";from_kind:Holder;from_id:string;to_kind:Holder;to_id:string;quantity:string;offered_by:string;accept_operation_id:string|null;accepted_quantity:string|null;short_quantity:string|null;vehicle_number:string;damage_operation_id?:string|null;accepted_by?:string|null;cancel_reason?:string|null;cancel_operation_id?:string|null};
export type TareBody={operation_id:string;[key:string]:string|number};
export type TareIntent={path:"/offer"|"/accept"|"/damage"|"/writeoff"|"/loss-report";body:TareBody;confirmed?:boolean};
export const tareBase=()=>(import.meta.env.VITE_API_BASE||"http://127.0.0.1:8088").replace(/\/$/,"");
export class TareApiError extends Error{constructor(message:string,public confirmed:boolean){super(message);}}
export async function tareRequest<T>(path:string,credentials:Credentials,body?:TareBody):Promise<T>{
 const bytes=new TextEncoder().encode(credentials.username+":"+credentials.password);
 const response=await fetch(tareBase()+"/api/inventory/tare"+path,{method:body?"POST":"GET",headers:{Authorization:"Basic "+btoa(String.fromCharCode(...bytes)),"Content-Type":"application/json"},...(body?{body:JSON.stringify(body)}:{})});
 const data=await response.json();if(!response.ok){const detail=data.detail;const message=typeof detail==="string"?detail:detail?.message||"Действие не подтверждено.";throw new TareApiError(message==="TARE_RETURN_POLICY_REQUIRED"?"Для магазина не настроен срок возврата тары. Ответственный должен задать правило в разделе сроков возврата; затем исправьте подтверждённый отказ.":message,response.status<500&&detail?.outcome_confirmed===true&&detail?.operation_id===body?.operation_id);}return data as T;
}

export type TareContext={participant?:{warehouse_id:number|null;all_warehouses:boolean;trip_driver:boolean;stores:string[];stores_has_more?:boolean;can_offer:boolean;can_accept:boolean};permissions?:{can_damage:number;can_writeoff:number;can_loss_report:number};trip:{task_id:number;vehicle_id:number;vehicle_number:string};warehouses:{id:number;name:string}[];types:{pallet_type_id:number;pallet_type_name:string;pallet_type_code:string}[];stores:string[]};

export type TareDebt={owner_ware_id:number;pallet_type_id:number;condition_code:string;claim_key:string;accept_operation_id:string;store_addr:string;pallet_type_name:string;outstanding_quantity:string;debt_state:string;effective_due_at:string|null;timezone_region:string|null};
