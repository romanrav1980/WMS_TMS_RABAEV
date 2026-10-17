import {ack,check,intent} from "./contracts";
import type {Journal} from "./contracts";
export const key=(actor:string)=>"wms.picker-time.journal.v1:"+location.origin+":"+encodeURIComponent(actor);
export async function read(actor:string):Promise<{journal:Journal;raw:string|null}>{
 const raw=localStorage.getItem(key(actor));if(raw===null)return{raw,journal:{schema:1,pending:null,last:null}};
 let v;try{v=JSON.parse(raw);}catch{throw new Error("Журнал времени повреждён. Новые действия запрещены; обратитесь к старшему смены.");}
 check(v&&Object.keys(v).sort().join()==="last,pending,schema"&&v.schema===1);
 const pending=v.pending===null?null:await intent(v.pending);let last:Journal["last"]=null;
 if(v.last!==null){check(v.last&&Object.keys(v.last).sort().join()==="ack,intent");const i=await intent(v.last.intent);last={intent:i,ack:ack(v.last.ack,i)};}
 for(const i of [pending,last?.intent])if(i)check(i.actor===actor&&i.server===location.origin);
 return{raw,journal:{schema:1,pending,last}};
}
export function save(actor:string,journal:Journal,raw:string|null):void{
 check(localStorage.getItem(key(actor))===raw);const text=JSON.stringify(journal);localStorage.setItem(key(actor),text);check(localStorage.getItem(key(actor))===text);
}
export async function lock<T>(actor:string,run:()=>Promise<T>):Promise<T>{
 if(!navigator.locks)throw new Error("Без безопасной блокировки журнала новые действия недоступны. Используйте актуальный Chrome или Edge.");
 return navigator.locks.request(key(actor),{mode:"exclusive"},run);
}
