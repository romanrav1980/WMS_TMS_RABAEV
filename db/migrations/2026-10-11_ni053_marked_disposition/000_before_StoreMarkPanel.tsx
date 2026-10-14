import { useEffect, useState } from "react";
import type { StorePreview, StoreUnitScan } from "./contracts";

export function StoreMarkPanel({preview,username,disabled,onScans}:{preview:StorePreview;username:string;disabled:boolean;onScans:(scans:StoreUnitScan[])=>void}) {
 const control=preview.marked_unit_control,profiles=control?.profiles||[];
 const [scans,setScans]=useState<StoreUnitScan[]>([]),[profile,setProfile]=useState("0"),[code,setCode]=useState(""),[message,setMessage]=useState("");
 const draftKey="store-mark:"+username+":"+preview.store_address+":"+preview.load_operation_id+":"+preview.composition_signature+":"+JSON.stringify(profiles);
 useEffect(()=>{
  let restored:StoreUnitScan[]=[];
  try {const value:unknown=JSON.parse(localStorage.getItem(draftKey)||"[]");
   if(Array.isArray(value)&&value.length<=20000&&value.every(x=>typeof x?.code==="string"&&x.code.length>0&&x.code.length<=4000&&profiles.some(p=>p.system_code===x.system_code&&p.profile_code===x.profile_code)))restored=value as StoreUnitScan[];
  }catch{setMessage("Не удалось восстановить черновик сканов.");}
  setScans(restored);onScans(restored);
  // Key includes the source identity and mandatory profile version snapshot.
  // eslint-disable-next-line react-hooks/exhaustive-deps
 },[draftKey]);
 function save(next:StoreUnitScan[]) {
  try {localStorage.setItem(draftKey,JSON.stringify(next));setScans(next);onScans(next);setMessage("");return true;}
  catch {setMessage("Не удалось сохранить сканы. Освободите место в браузере.");return false;}
 }
 function add() {
  if(disabled)return;const selected=profiles[Number(profile)];
  if(!selected||!code){setMessage("Выберите профиль и сканируйте QR.");return;}
  if(code.length>4000||scans.length>=20000){setMessage("Превышен допустимый размер сканов.");return;}
  if(scans.some(x=>x.system_code===selected.system_code&&x.profile_code===selected.profile_code&&x.code===code)){setMessage("Этот QR уже добавлен.");return;}
  if(save([...scans,{system_code:selected.system_code,profile_code:selected.profile_code,code}]))setCode("");
 }
 if(!preview.requires_marked_recipient_flow||preview.already_received)return null;
 if(!control?.supported)return <p>Для этого состава требуется другой способ сверки маркировки. {control?.reason}</p>;
 return <fieldset disabled={disabled}>
  <legend>Сверка уникальных кодов товара</legend>
  <p>Физических единиц: {control.physical_unit_count}. Сканов обязательных профилей: {scans.length} из {control.expected_scan_count}. Несколько кодов одной штуки не увеличивают количество товара.</p>
  <label>Система и профиль<select value={profile} onChange={e=>setProfile(e.target.value)}>{profiles.map((p,i)=><option key={p.system_code+":"+p.profile_code} value={i}>{p.system_code} / {p.profile_code}</option>)}</select></label>
  <label>QR единицы<input autoComplete="off" value={code} onChange={e=>setCode(e.target.value)} onKeyDown={e=>{if(e.key==="Enter"){e.preventDefault();add();}}}/></label>
  <button type="button" onClick={add}>Добавить скан</button><button type="button" onClick={()=>save([])}>Очистить сканы</button>
  <p role="status">{message}</p>
 </fieldset>;
}
