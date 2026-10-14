import type { ReceiptCredentials } from "./contracts";
import { humanReceiptMessage } from "./messages";
export const receiptBase = () => (import.meta.env.VITE_API_BASE || "http://127.0.0.1:8088").replace(/\/$/,"");
export class ReceiptApiError extends Error {
 constructor(message: string, public confirmed: boolean) {super(message);}
}
export async function receiptRequest<T>(path: string, credentials: ReceiptCredentials, body?: unknown): Promise<T> {
 const response=await fetch(receiptBase()+"/api/delivery/store-receipts"+path,{
  method:body?"POST":"GET",headers:{Authorization:"Basic "+btoa(credentials.username+":"+credentials.password),"Content-Type":"application/json"},
  ...(body?{body:JSON.stringify(body)}:{})
 });
 const data=await response.json();
 if(!response.ok){
  const detail=data.detail;
  throw new ReceiptApiError(humanReceiptMessage(typeof detail==="string"?detail:detail?.message||JSON.stringify(detail)),
   response.status<500&&detail?.outcome_confirmed===true&&!!body&&detail?.operation_id===(body as {operation_id?:string}).operation_id);
 }
 return data as T;
}
