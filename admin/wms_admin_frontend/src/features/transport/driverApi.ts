export interface DriverCredentials {username:string;password:string;driverId:number}
export interface DriverTrip {task_id:number;shipment_date:string;num_plat:string;transport_type:string;condition:string;note:string;price:number;st_count:number;weight_kg:number;loaded_weight_kg:string|null}
export interface DriverStop {st_number:string;addr:string;ord:number;time_from:string;time_to:string;load_type:string;pallet_count:number}
export interface DriverOperation {op_id:number;operation_code:string;ord:number;plan_start:string;plan_end:string;fact_start:string;fact_end:string;note:string;status:"pending"|"in_progress"|"done"}
export const driverApiBase=()=>String(import.meta.env.VITE_API_BASE||"http://127.0.0.1:8088").replace(/\/$/,"");
export class DriverApiError extends Error {constructor(message:string,public status:number){super(message);}}
export async function driverRequest<T>(credentials:DriverCredentials,path:string,action=false):Promise<T>{
 const response=await fetch(driverApiBase()+"/api/driver"+path,{method:action?"POST":"GET",cache:"no-store",
  headers:{Authorization:"Basic "+btoa(credentials.username+":"+credentials.password)}});
 const type=response.headers.get("content-type")||"";
 if(!type.includes("application/json"))throw new DriverApiError("Сервер вернул неверный формат ответа. Проверьте адрес API.",response.status);
 const body=await response.json();
 if(!response.ok)throw new DriverApiError(body.detail?.message||body.detail||"Ошибка запроса",response.status);
 return body as T;
}
