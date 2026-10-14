import { useEffect, useState } from "react";
import { receiptBase } from "./api";
import type { StoreMarkControl, StoreUnitScan, ReturnMarkEvidence } from "./contracts";
const empty=():ReturnMarkEvidence=>({scans:[],aggregation_scans:[]});

export function ReturnMarkPanel({control,scope,username,disabled,onChange}:{control?:StoreMarkControl|null;scope:string;username:string;disabled:boolean;onChange:(value:ReturnMarkEvidence,ready:boolean)=>void}) {
 const profiles=control?.profiles||[];
 const [draft,setDraft]=useState<ReturnMarkEvidence>(empty),[selected,setSelected]=useState("0"),[kind,setKind]=useState("UNIT"),[code,setCode]=useState(""),[message,setMessage]=useState("");
 const key="return-mark:"+receiptBase()+":"+username+":"+scope+":"+JSON.stringify(control);
 function ready(value:ReturnMarkEvidence) {
  if(!control)return true;
  if(!control.supported||profiles.some(p=>!["UNIT","BOX","PALLET","UNIT_OR_AGGREGATION"].includes(p.scan_mode)))return false;
  return profiles.every(p=>{
   const units=value.scans.filter(x=>x.system_code===p.system_code&&x.profile_code===p.profile_code).length;
   const boxes=value.aggregation_scans.filter(x=>x.system_code===p.system_code&&x.profile_code===p.profile_code&&(p.scan_mode==="UNIT_OR_AGGREGATION"||x.level===p.scan_mode)).length;
   const expected=(control.units||[]).filter(u=>u.profiles?.some(x=>x.system_code===p.system_code&&x.profile_code===p.profile_code)).length||control.physical_unit_count||0;
   return ["BOX","PALLET"].includes(p.scan_mode)?boxes>0:units===expected||(p.scan_mode==="UNIT_OR_AGGREGATION"&&boxes>0);
  });
 }
 useEffect(()=>{
  let restored=empty();let warning="";
  try {
   const value:unknown=JSON.parse(localStorage.getItem(key)||"null");
   if(value!==null){
    const item=value as ReturnMarkEvidence;
    const valid=(x:StoreUnitScan)=>typeof x?.code==="string"&&x.code.length>0&&x.code.length<=4000&&profiles.some(p=>p.system_code===x.system_code&&p.profile_code===x.profile_code);
    if(!Array.isArray(item.scans)||!Array.isArray(item.aggregation_scans)||item.scans.length>20000||item.aggregation_scans.length>1000||!item.scans.every(x=>valid(x)&&profiles.some(p=>p.system_code===x.system_code&&p.profile_code===x.profile_code&&["UNIT","UNIT_OR_AGGREGATION"].includes(p.scan_mode)))||!item.aggregation_scans.every(x=>valid(x)&&["BOX","PALLET"].includes(x.level)&&profiles.some(p=>p.system_code===x.system_code&&p.profile_code===x.profile_code&&(p.scan_mode===x.level||p.scan_mode==="UNIT_OR_AGGREGATION"))))throw Error("invalid");
    restored=item;
   }
  }catch{warning="Черновик сканов повреждён. Сканируйте состав заново.";}
  setDraft(restored);setCode("");setMessage(warning);onChange(restored,ready(restored));
  // Scope binds API, actor, original return and current mandatory profiles.
  // eslint-disable-next-line react-hooks/exhaustive-deps
 },[key]);
 function save(value:ReturnMarkEvidence){try{localStorage.setItem(key,JSON.stringify(value));setDraft(value);onChange(value,ready(value));setMessage("");return true;}catch{setMessage("Не удалось сохранить сканы. Передача не отправлена.");return false;}}
 const profile=profiles[Number(selected)];
 const mode=profile?.scan_mode;
 const effectiveKind=mode==="BOX"||mode==="PALLET"?mode:mode==="UNIT"?"UNIT":kind;
 function add(){
  if(disabled||!profile||!code||code.length>4000)return;
  const values=effectiveKind!=="UNIT"?draft.aggregation_scans:draft.scans;
  if(values.some(x=>x.system_code===profile.system_code&&x.profile_code===profile.profile_code&&x.code===code)){setMessage("Этот код уже добавлен.");return;}
  if(values.length>=(effectiveKind!=="UNIT"?1000:20000)){setMessage("Превышен допустимый размер состава.");return;}
  const scan={system_code:profile.system_code,profile_code:profile.profile_code,code};
  if(save(effectiveKind!=="UNIT"?{...draft,aggregation_scans:[...draft.aggregation_scans,{...scan,level:effectiveKind as "BOX"|"PALLET"}]}:{...draft,scans:[...draft.scans,scan]}))setCode("");
 }
 function removeLast(){
  if(!profile||disabled)return;
  const field=effectiveKind==="UNIT"?"scans":"aggregation_scans";
  const list=draft[field];let index=-1;
  for(let i=list.length-1;i>=0;i--){const item=list[i];if(item.system_code===profile.system_code&&item.profile_code===profile.profile_code&&(effectiveKind==="UNIT"||("level"in item&&item.level===effectiveKind))){index=i;break;}}
  if(index>=0)save({...draft,[field]:list.filter((_,i)=>i!==index)});
 }
 if(!control)return null;
 if(!control.supported)return <p>Состав возврата недоступен для сверки: {control.reason}</p>;

 return <fieldset disabled={disabled}><legend>Маркировка возврата</legend>
  <p>Для агрегации PALLET сохраните исходный идентификатор и полный неизменённый состав паллеты.</p>
  <p>QR единиц: {draft.scans.length}. Коды коробок: {draft.aggregation_scans.length}. Сервер проверит полный состав и действительность агрегации.</p>
  <label>Система и профиль<select value={selected} onChange={e=>setSelected(e.target.value)}>{profiles.map((p,i)=><option key={p.system_code+":"+p.profile_code} value={i}>{p.system_code} / {p.profile_code} · {p.scan_mode}</option>)}</select></label>
  {mode==="UNIT_OR_AGGREGATION"&&<label>Способ сверки<select value={kind} onChange={e=>setKind(e.target.value)}><option value="UNIT">QR единицы</option><option value="BOX">Агрегация коробки</option><option value="PALLET">Агрегация исходной паллеты</option></select></label>}
  <label>{effectiveKind==="PALLET"?"Код агрегации исходной паллеты":effectiveKind==="BOX"?"Код агрегации коробки":"QR единицы"}<input autoComplete="off" value={code} onChange={e=>setCode(e.target.value)} onKeyDown={e=>{if(e.key==="Enter"){e.preventDefault();add();}}}/></label>
  <button type="button" onClick={add}>Добавить код</button><button type="button" onClick={removeLast}>Убрать последний скан в выбранном режиме</button><button type="button" onClick={()=>save(empty())}>Очистить сканы</button><p role="status">{message}</p>
 </fieldset>;
}
