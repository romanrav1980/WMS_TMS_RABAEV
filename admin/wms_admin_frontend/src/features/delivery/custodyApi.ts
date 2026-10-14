import type { ReceiptCredentials, StoreUnitScan, StoreMarkControl } from "./contracts";
import type { ReturnAggregateScan } from "./contracts";
import { receiptBase, ReceiptApiError } from "./api";

export type ReturnStorePlace={marked_unit_control?:StoreMarkControl|null;transport_operation_id:string;tt_id:number;vehicle_number:string;store_addr:string;quantity:string;base_uom:string;article:string;planned_gross_weight_kg:string;physical_places:number};
export type ReturnDriverPlace={marked_unit_control?:StoreMarkControl|null;handover_operation_id:string;tt_id:number;vehicle_number:string;store_addr:string;pallet_identifier:string;gross_weight_kg:string;physical_places:number;handed_by:string};
export type CustodyBody={scans?:StoreUnitScan[];aggregation_scans?:ReturnAggregateScan[];operation_id:string;transport_operation_id:string;pallet_identifier:string;quantity:string;base_uom:string;gross_weight_kg:string;physical_places:number}|{scans?:StoreUnitScan[];aggregation_scans?:ReturnAggregateScan[];operation_id:string;handover_operation_id:string;scan_vehicle:string;scan_pallet:string};
export type CustodyIntent={path:"/handover"|"/pickup";body:CustodyBody;confirmedRejection?:boolean};

const reasons:Record<string,string>={
 STORE_RETURN_CURRENT_CAPACITY_EXCEEDED:"Текущая вместимость машины не допускает этот возврат.",
 STORE_RETURN_CURRENT_DEPARTED_TRIP_REQUIRED:"Изменились рейс, водитель или машина. Обратитесь к логисту.",
 STORE_RETURN_DRIVER_VEHICLE_PALLET_SCAN_REQUIRED:"Скан машины или паллеты не соответствует переданному возврату.",
 STORE_RETURN_FULL_APPROVED_QUANTITY_REQUIRED:"Передайте всё согласованное количество в указанной основной единице.",
 STORE_RETURN_PHYSICAL_PLACE_OR_PLAN_MISMATCH:"Масса или число мест не соответствуют плану вывоза.",
 STORE_RETURN_BOUND_DRIVER_AND_HANDOVER_REQUIRED:"Учётная запись не привязана к водителю этого рейса.",
 STORE_RETURN_ALREADY_PICKED_UP:"Возврат уже принят водителем.",
 STORE_RETURN_ALREADY_HANDED_OVER:"Передача магазина уже подтверждена.",
 STORE_RETURN_MULTI_PLACE_MANIFEST_REQUIRED:"Для нескольких мест требуется отдельный подробный состав.",
 STORE_RETURN_SEPARATE_HANDOVER_AND_DRIVER_REQUIRED:"Магазин и водитель должны подтвердить передачу разными учётными записями."
};

export async function custodyRequest<T>(path:string,credentials:ReceiptCredentials,body?:CustodyBody):Promise<T>{
 const bytes=new TextEncoder().encode(credentials.username+":"+credentials.password);
 const response=await fetch(receiptBase()+"/api/delivery/store-return-custody"+path,{method:body?"POST":"GET",
  headers:{Authorization:"Basic "+btoa(String.fromCharCode(...bytes)),"Content-Type":"application/json"},...(body?{body:JSON.stringify(body)}:{})});
 const data=await response.json();
 if(!response.ok){
  const detail=data.detail,raw=typeof detail==="string"?detail:detail?.message||"Действие не подтверждено.";
  const message=Object.entries(reasons).find(([reason])=>raw.includes(reason))?.[1]||raw;
  throw new ReceiptApiError(message,response.status<500&&detail?.outcome_confirmed===true&&!!body&&detail?.operation_id===body.operation_id);
 }
 return data as T;
}

export type CustodyPayload=Omit<Extract<CustodyBody,{transport_operation_id:string}>,"operation_id">|Omit<Extract<CustodyBody,{handover_operation_id:string}>,"operation_id">;
