import { assemblyAuthHeader } from "../assembly/api";
import type { AssemblyCredentials } from "../assembly/contracts";
import type { Intent } from "./contracts";
export async function request(path:string,credentials:AssemblyCredentials,signal:AbortSignal,i?:Intent):Promise<unknown>{
 const abort=new AbortController(),stop=()=>abort.abort();signal.addEventListener("abort",stop,{once:true});if(signal.aborted)stop();
 const timer=window.setTimeout(stop,30000);
 try{const r=await fetch("/api/resources/picker-time"+path,{method:i?"POST":"GET",signal:abort.signal,cache:"no-store",headers:{Authorization:assemblyAuthHeader(credentials),...(i?{"Content-Type":"application/json"}:{})},body:i?.wire});
 const data:unknown=await r.json();if(r.status===200||(i&&r.status===409))return data;
 throw new Error(r.status===404?"Квитанция пока не найдена. Исходный запрос сохранён.":r.status===401||r.status===403?"Нет текущего доступа. Исходный запрос сохранён.":"Ответ времени не подтверждён. Исходный запрос сохранён.");
 }finally{clearTimeout(timer);signal.removeEventListener("abort",stop);}
}
