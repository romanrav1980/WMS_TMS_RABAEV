// C-0032: сохранённая команда утверждения времени рейса. Одна запись на apiBase+actor; команда
// повторяется точно (тот же operation_id/version/hash), удаляется только после подтверждённого результата.
export type TimeApprovalIntent = {operation_id:string;trip_id:number;expected_version:number;
  source_hash:string;time_zone:string;reason:string;approval_phase?:"AFTER_LOADING_REVIEW"};
export type PendingState =
  | {kind:"none"}
  | {kind:"valid";intent:TimeApprovalIntent;raw:string}
  | {kind:"damaged";raw:string};

export const pendingKey=(apiBase:string,actor:string)=>"retailcase.trip.time.pending:"+JSON.stringify([apiBase,actor]);

function isIntent(v:unknown):v is TimeApprovalIntent {
  if(!v||typeof v!=="object"||Array.isArray(v))return false;
  const x=v as Record<string,unknown>;
  return typeof x.operation_id==="string"&&/^[A-Za-z0-9_.:-]{1,100}$/.test(x.operation_id)
    &&Number.isSafeInteger(x.trip_id)&&(x.trip_id as number)>0&&Number.isSafeInteger(x.expected_version)
    &&typeof x.source_hash==="string"&&x.source_hash.length>0&&typeof x.time_zone==="string"&&x.time_zone.length>0
    &&typeof x.reason==="string"&&(x.approval_phase===undefined||x.approval_phase==="AFTER_LOADING_REVIEW");
}

export function readPending(key:string):PendingState {
  let raw:string|null;
  try{raw=localStorage.getItem(key);}catch{return {kind:"damaged",raw:""};}
  if(raw===null)return {kind:"none"};
  try{const v:unknown=JSON.parse(raw);if(isIntent(v))return {kind:"valid",intent:v,raw};}catch{/* повреждённая запись */}
  return {kind:"damaged",raw};
}

// Запись с проверкой чтением: без надёжного сохранения команда не отправляется.
export function savePending(key:string,intent:TimeApprovalIntent):string {
  const raw=JSON.stringify(intent);
  try{localStorage.setItem(key,raw);if(localStorage.getItem(key)===raw)return raw;}catch{/* ниже */}
  throw new Error("Не удалось надёжно сохранить команду утверждения — она не отправлена.");
}

// Удаляет запись, только если она не изменилась (другая вкладка могла заменить команду).
export function settlePending(key:string,raw:string):boolean {
  try{if(localStorage.getItem(key)!==raw)return false;localStorage.removeItem(key);return localStorage.getItem(key)===null;}catch{return false;}
}

// Повреждённую запись не удаляем молча: переносим в архив для разбора и только потом освобождаем ключ.
export function archiveDamaged(key:string,raw:string):boolean {
  try{
    if(localStorage.getItem(key)!==raw)return false;
    const archive=key+":damaged:"+crypto.randomUUID();localStorage.setItem(archive,raw);
    if(localStorage.getItem(archive)!==raw)return false;
    localStorage.removeItem(key);return localStorage.getItem(key)===null;
  }catch{return false;}
}

export const phaseLabel=(i:TimeApprovalIntent)=>i.approval_phase==="AFTER_LOADING_REVIEW"?"после полной подтверждённой погрузки":"плановое утверждение";
