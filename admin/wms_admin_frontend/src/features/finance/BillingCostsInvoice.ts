import {useCallback,useEffect,useRef,useState} from "react";
import {apiFetch} from "../../api";
import {readError} from "./BillingCostsCommon";

// Чтение расшифровки счёта (только GET): три существующих источника, независимые состояния.
// Ответ, пришедший после смены счёта, отбрасывается (epoch).

export type CostLine={operation_id:string;tt_id:number;ware_id:number;load_operation_id:string;cost_code:string;currency:string;quantity:number|string;rate_value:string;amount:string;version_no:number;basis:string;rate_date?:string|null;period_mode?:string|null;period_time_zone?:string|null;period_policy_version?:number|null;components?:{picking_rate:string;common_work_rate:string;month:string}|null};
export type CostGroup={ware_id:number;rate_date:string|null;period_mode:string|null;period_time_zone:string|null;period_policy_version:number|null;cost_code:string;currency:string;basis:string;version_no:number;rate_value:string;quantity:string;amount:string;source_count:number;trips:number[]};
export type WarehouseSummary={invoice_id:number;lines:CostLine[];groups:CostGroup[];currency_totals:{currency:string;original_amount:string}[];visible_warehouses?:number[];scope:"VISIBLE_WAREHOUSES";basis:"ORIGINAL_RECOGNIZED_COSTS";includes_corrections?:boolean;includes_extra_expenses?:boolean};

export type TransportNorm={version:number;currency?:string;effective_from?:string;vehicle_type?:string;vehicle_size_class?:string;unload_charge_basis?:string|null;source?:{price_name?:string;company?:string}};
export type TransportItem={operation_id:string;trip_id:number;warehouse_id:number;total:string|null;confirmed_total:string|null;currency:string;norm:TransportNorm;
 lines:Array<{cost_code:string;quantity:number;rate:string;amount:string;basis:string}>;departure?:{departure_operation_id?:string;departed_at_instant?:string;vehicle_number?:string}|null;
 missing?:unknown[];complete?:boolean;amount_rounding?:string;load_count?:number;destination_count?:number};
export type TransportResult={invoice_id:number;sources:Array<{trip:number;warehouse:number}>;items:TransportItem[];currency_totals:Array<{currency:string;amount:string;confirmed_amount:string}>};

export type Expense={operation_id:string;article_name:string;tt_id:number;amount:string;currency:string;document_reference:string;finance_outcome:"APPROVE"|"REJECT"|null;allocation_operation_id:string|null;distribution_basis:string|null;goods_lines:number;cost_correction_of_op:string|null;correction_of_op:string|null}&Partial<ExpenseBasisFields>;
// K-0007: прямое основание строки расхода. Поля необязательны: старый сервер их не возвращает, это обрабатывается явно.
export type ExpenseBasisFields={ware_id:number;expense_date:string|null;reporter:string|null;article_code:string;expected_confirmed_total:string|null;confirmed_total:string|null;
 logist_operation_id:string|null;logist_outcome:"APPROVE"|"REJECT"|null;logist_actor:string|null;logist_decision_reference:string|null;
 finance_operation_id:string|null;finance_actor:string|null;finance_decision_reference:string|null};
export const hasDirectBasis=(e:Expense):e is Expense&ExpenseBasisFields=>typeof e.ware_id==="number";

export type Part<T>={data:T|null;error:string;loading:boolean};
const idle=<T,>():Part<T>=>({data:null,error:"",loading:true});

export function useInvoiceCosts(invoiceId:number){
 const epoch=useRef(0);
 const [warehouse,setWarehouse]=useState<Part<WarehouseSummary>>(idle);
 const [transport,setTransport]=useState<Part<TransportResult>>(idle);
 const [expenses,setExpenses]=useState<Part<Expense[]>>(idle);
 const [readAt,setReadAt]=useState<Date|null>(null);

 const load=useCallback(()=>{
  const current=++epoch.current;
  setWarehouse(idle());setTransport(idle());setExpenses(idle());setReadAt(null);
  const run=<T,>(path:string,what:string,set:(p:Part<T>)=>void)=>apiFetch<T>(path)
   .then(data=>{if(current===epoch.current)set({data,error:"",loading:false});})
   .catch(e=>{if(current===epoch.current)set({data:null,error:readError(e,what),loading:false});});
  void Promise.all([
   run<WarehouseSummary>("/api/finance/logistics-costs/billing-orders/"+invoiceId+"/summary","складских начислений",setWarehouse),
   run<TransportResult>("/api/finance/logistics-costs/billing-orders/"+invoiceId+"/transport-costs","транспортных начислений",setTransport),
   run<Expense[]>("/api/finance/expense-allocation/billing-orders/"+invoiceId,"дополнительных расходов",setExpenses)
  ]).then(()=>{if(current===epoch.current)setReadAt(new Date());});
 },[invoiceId]);

 useEffect(()=>{load();return()=>{epoch.current++;};},[load]);

 // Защита от показа ответа другого счёта, если он всё же пришёл.
 const own=<T extends {invoice_id:number}>(p:Part<T>):Part<T>=>p.data&&p.data.invoice_id!==invoiceId?{...p,data:null}:p;
 return {warehouse:own(warehouse),transport:own(transport),expenses,readAt,reload:load};
}
