export type Action = "ACTUAL_SHIFT_START" | "ACTUAL_SHIFT_FINISH" | "WORK_START" | "PAUSE" | "RESUME" | "WORK_FINISH";
export type Command = { operation_id:string; action:Action; expected_version:number; resource_session_id:number; source_kind:"CASE_PICK_TASK"|"WAREHOUSE_TASK"|null; source_id:number|null; reason:string };
export type State = { operator_id:string; stream_version:number; shift_state:"OFF"|"OPEN"; work_state:"IDLE"|"WORK"|"PAUSED";
 warehouse_id:number|null; resource_session_id:number|null; resource_id:number|null; source_kind:Command["source_kind"]; source_id:number|null;
 shift_started_at:string|null; work_started_at:string|null; pause_started_at:string|null; last_event_at:string|null; work_coverage_certified:false; source_mode:"MANUAL_CONFIRMED" };
export type Intent = { server:string; actor:string; body:Command; wire:string; request_sha256:string };
export type Ack = { operation_id:string; actor:string; action:Action; resource_session_id:number; warehouse_id:number; request_sha256:string;
 outcome:"APPLIED"|"REJECTED"; outcome_confirmed:true; changed:boolean; may_create_corrected_operation:boolean; error_code:string|null;
 stock_posted:false; event_at:string|null; before_version:number; after_version:number; state:State };
export type Journal = { schema:1; pending:Intent|null; last:{intent:Intent;ack:Ack}|null };
export const object=(v:unknown):v is Record<string,unknown>=>!!v&&typeof v==="object"&&!Array.isArray(v);
const id=(v:unknown):v is number=>Number.isSafeInteger(v)&&Number(v)>0;
const version=(v:unknown):v is number=>Number.isSafeInteger(v)&&Number(v)>=0;
const nullableId=(v:unknown)=>v===null||id(v);
const aware=(v:unknown)=>{
 if(typeof v!=="string")return false;
 const m=v.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d{1,9})?(Z|[+-]\d{2}:\d{2})$/);if(!m)return false;
 const [year,month,day,hour,minute,second]=m.slice(1,7).map(Number);
 const d=new Date(0);d.setUTCFullYear(year,month-1,day);d.setUTCHours(hour,minute,second,0);
 const valid=d.getUTCFullYear()===year&&d.getUTCMonth()===month-1&&d.getUTCDate()===day&&hour<24&&minute<60&&second<60;
 const offset=m[7]==="Z"||Number(m[7].slice(1,3))<24&&Number(m[7].slice(4))<60;
 return valid&&offset&&Number.isFinite(Date.parse(v));
};
export function check(ok:unknown):asserts ok {if(!ok)throw new Error("Ответ или журнал времени не соответствует исходной операции. Запрос сохранён.");}
export const canonical=(v:Command)=>JSON.stringify(Object.fromEntries(Object.keys(v).sort().map(k=>[k,v[k as keyof Command]])));
export async function sha(wire:string):Promise<string>{return Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",new TextEncoder().encode(wire))),v=>v.toString(16).padStart(2,"0")).join("").toUpperCase();}
export function command(v:unknown):Command {
 check(object(v)&&Object.keys(v).sort().join() === "action,expected_version,operation_id,reason,resource_session_id,source_id,source_kind");
 check(typeof v.operation_id==="string"&&/^[A-Za-z0-9_.:-]{1,100}$/.test(v.operation_id)&&version(v.expected_version)&&id(v.resource_session_id));
 check(["ACTUAL_SHIFT_START","ACTUAL_SHIFT_FINISH","WORK_START","PAUSE","RESUME","WORK_FINISH"].includes(String(v.action)));
 check(typeof v.reason==="string"&&Array.from(v.reason.trim()).length>=8&&Array.from(v.reason).length<=500);
 const shift=String(v.action).startsWith("ACTUAL_SHIFT_");
 check(shift?v.source_kind===null&&v.source_id===null:["CASE_PICK_TASK","WAREHOUSE_TASK"].includes(String(v.source_kind))&&id(v.source_id));return v as Command;
}
export function state(v:unknown,actor:string):State {
 check(object(v)&&v.operator_id===actor&&version(v.stream_version)&&["OFF","OPEN"].includes(String(v.shift_state))&&["IDLE","WORK","PAUSED"].includes(String(v.work_state)));
 check(v.source_mode==="MANUAL_CONFIRMED"&&v.work_coverage_certified===false&&[v.warehouse_id,v.resource_session_id,v.resource_id,v.source_id].every(nullableId));
 for(const key of ["shift_started_at","work_started_at","pause_started_at","last_event_at"])check(v[key]===null||aware(v[key]));
 check((v.stream_version===0)===(v.last_event_at===null));
 if(v.shift_state==="OFF")check(v.work_state==="IDLE"&&v.warehouse_id===null&&v.resource_session_id===null&&v.resource_id===null&&v.shift_started_at===null);
 else check(id(v.warehouse_id)&&id(v.resource_session_id)&&id(v.resource_id)&&aware(v.shift_started_at));
 if(v.work_state==="IDLE")check(v.source_kind===null&&v.source_id===null&&v.work_started_at===null&&v.pause_started_at===null);
 else check(["CASE_PICK_TASK","WAREHOUSE_TASK"].includes(String(v.source_kind))&&id(v.source_id)&&aware(v.work_started_at));
 check((v.work_state==="PAUSED")===(v.pause_started_at!==null));
 const times=[v.shift_started_at,v.work_started_at,v.pause_started_at,v.last_event_at].filter(x=>x!==null).map(x=>Date.parse(String(x)));
 check(times.every((t,i)=>i===0||t>=times[i-1]));return v as State;
}
export async function intent(v:unknown):Promise<Intent>{check(object(v)&&typeof v.server==="string"&&typeof v.actor==="string"&&v.actor.length>0);const body=command(v.body);check(v.wire===canonical(body)&&v.request_sha256===await sha(String(v.wire)));return v as Intent;}
export function ack(v:unknown,i:Intent):Ack {
 check(object(v)&&v.operation_id===i.body.operation_id&&v.actor===i.actor&&v.action===i.body.action&&v.resource_session_id===i.body.resource_session_id);
 check(id(v.warehouse_id)&&v.request_sha256===i.request_sha256&&v.outcome_confirmed===true&&v.stock_posted===false&&version(v.before_version)&&version(v.after_version));
 const s=state(v.state,i.actor);check(s.stream_version===v.after_version);
 if(v.outcome==="APPLIED"){
 check(v.before_version===i.body.expected_version&&v.changed===true&&v.may_create_corrected_operation===false&&v.error_code===null&&aware(v.event_at)&&v.event_at===s.last_event_at&&v.after_version===Number(v.before_version)+1);
 const expected:Record<Action,[State["shift_state"],State["work_state"]]>={ACTUAL_SHIFT_START:["OPEN","IDLE"],ACTUAL_SHIFT_FINISH:["OFF","IDLE"],WORK_START:["OPEN","WORK"],PAUSE:["OPEN","PAUSED"],RESUME:["OPEN","WORK"],WORK_FINISH:["OPEN","IDLE"]};
 const next=expected[i.body.action];check(s.shift_state===next[0]&&s.work_state===next[1]);
 if(s.shift_state==="OPEN")check(s.resource_session_id===i.body.resource_session_id&&s.warehouse_id===v.warehouse_id);
 if(s.work_state!=="IDLE")check(s.source_kind===i.body.source_kind&&s.source_id===i.body.source_id);
 }else check(v.outcome==="REJECTED"&&v.changed===false&&v.may_create_corrected_operation===true&&typeof v.error_code==="string"&&v.error_code.trim().length>0&&v.event_at===null&&v.after_version===v.before_version);
 return v as Ack;
}
