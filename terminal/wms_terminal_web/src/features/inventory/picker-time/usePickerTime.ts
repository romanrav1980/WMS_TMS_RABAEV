import {useCallback,useEffect,useRef,useState} from "react";
import type {AssemblyCredentials} from "../assembly/contracts";
import {ack,canonical,check,command,sha,state} from "./contracts";
import type {Action,Intent,Journal,State} from "./contracts";
import {request} from "./api";
import {key,lock,read,save} from "./journal";
type View={current:State|null;journal:Journal|null;busy:boolean;blocked:boolean;error:string};
const initial:View={current:null,journal:null,busy:false,blocked:true,error:""};
const message=(e:unknown)=>e instanceof Error?e.message:"Нет подтверждения. Запрос сохранён.";
async function resolve(i:Intent,c:AssemblyCredentials,signal:AbortSignal,post:boolean):Promise<Journal>{
 const value=await request(post?"/me/commands":"/commands/"+encodeURIComponent(i.body.operation_id),c,signal,post?i:undefined);
 if(signal.aborted)throw new Error("Чтение отменено. Запрос сохранён.");
 const receipt=ack(value,i),saved=await read(c.username);
 if(signal.aborted)throw new Error("Чтение отменено. Запрос сохранён.");
 if(saved.journal.pending?.wire!==i.wire)throw new Error("Журнал изменился в другой вкладке. Прочитайте исходный итог.");
 const next:Journal={schema:1,pending:null,last:{intent:i,ack:receipt}};save(c.username,next,saved.raw);return next;
}
export function usePickerTime(credentials:AssemblyCredentials){
 const [view,setView]=useState<View>(initial),[refresh,setRefresh]=useState(0);
 const epoch=useRef(0),running=useRef(false),controller=useRef<AbortController|null>(null);
 const actor=credentials.username;
 const publish=(v:number,patch:Partial<View>)=>{if(epoch.current===v&&!controller.current?.signal.aborted)setView(old=>({...old,...patch}));};
 useEffect(()=>{
  const v=++epoch.current,abort=new AbortController();controller.current=abort;running.current=true;setView({...initial,busy:true});
  void(async()=>{try{
   let saved;try{saved=await read(actor);}catch(e){publish(v,{error:message(e)});return;}
   publish(v,{journal:saved.journal,blocked:false});
   if(saved.journal.pending){try{const journal=await lock(actor,()=>resolve(saved.journal.pending!,credentials,abort.signal,false));publish(v,{journal});}catch(e){publish(v,{error:message(e)});}}
   const current=state(await request("/me/current",credentials,abort.signal),actor);publish(v,{current});
  }catch(e){publish(v,{error:message(e)});}finally{if(epoch.current===v){running.current=false;publish(v,{busy:false});}}})();
  const changed=(event:StorageEvent)=>{if(event.key===null||event.key===key(actor))setRefresh(x=>x+1);};window.addEventListener("storage",changed);
  return()=>{abort.abort();epoch.current++;running.current=false;window.removeEventListener("storage",changed);};
 },[actor,credentials.password,refresh]);
 const perform=useCallback(async(action:Action|null,session:number|null,source:number|null,reason:string,post:boolean)=>{
  if(running.current)return;running.current=true;const v=epoch.current,abort=controller.current;
  if(!abort){running.current=false;return;}publish(v,{busy:true,error:""});
  try{await lock(actor,async()=>{
   const saved=await read(actor);let i=saved.journal.pending;
   if(action){
    if(i)throw new Error("Сначала прочитайте итог сохранённого запроса.");
    const current=state(await request("/me/current",credentials,abort.signal),actor);
    check(view.current&&current.stream_version===view.current.stream_version);
    const body=command({operation_id:"TIME:"+crypto.randomUUID(),action,expected_version:current.stream_version,resource_session_id:session,
      source_kind:action.startsWith("ACTUAL_SHIFT_")?null:action==="WORK_START"?"CASE_PICK_TASK":current.source_kind,
      source_id:action.startsWith("ACTUAL_SHIFT_")?null:action==="WORK_START"?source:current.source_id,reason});
    const wire=canonical(body);i={server:location.origin,actor,body,wire,request_sha256:await sha(wire)};
    if(abort.signal.aborted||epoch.current!==v)return;
    const next:Journal={...saved.journal,pending:i};save(actor,next,saved.raw);publish(v,{journal:next});
   }
   if(!i)throw new Error("Нет сохранённого запроса.");
   const journal=await resolve(i,credentials,abort.signal,post);publish(v,{journal,current:null});
  });setRefresh(x=>x+1);
  }catch(e){publish(v,{error:message(e)});}finally{if(epoch.current===v){running.current=false;publish(v,{busy:false});}}
 },[actor,credentials.password,view.current]);
 return{...view,refresh:()=>setRefresh(x=>x+1),submit:(action:Action,session:number,source:number|null,reason:string)=>perform(action,session,source,reason,true),
 retry:()=>perform(null,null,null,"",true),readReceipt:()=>perform(null,null,null,"",false)};
}
