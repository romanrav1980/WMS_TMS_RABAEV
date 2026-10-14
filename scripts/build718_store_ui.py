from pathlib import Path
import json
out={}
p=Path("admin/wms_admin_frontend/src/features/delivery/contracts.ts");s=p.read_text(encoding="utf-8").replace('export interface ReturnAggregateScan','export interface StoreAggregateScan extends StoreUnitScan {level:"BOX"|"PALLET"}\nexport interface ReturnAggregateScan').replace('export interface ReceiptBody {','export interface ReceiptBody {\n aggregation_scans?:StoreAggregateScan[];');out[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/delivery/useStoreReceipt.ts");s=p.read_text(encoding="utf-8").replace("StoreUnitScan, UnloadingDetails","StoreUnitScan, StoreAggregateScan, UnloadingDetails").replace("unloading?: UnloadingDetails) {","unloading?: UnloadingDetails, aggregates?:StoreAggregateScan[]) {").replace("...(scans?.length?{scans}:{})","...(scans?.length?{scans}:{}),...(aggregates?.length?{aggregation_scans:aggregates}:{})");out[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/delivery/StoreReceiptPanel.tsx");s=p.read_text(encoding="utf-8").replace("confirm={(rows,note,evidence,scans)=>flow.confirm(scan,cameras,rows,note,evidence,scans,unloading)}","confirm={(rows,note,evidence,scans,aggregates)=>flow.confirm(scan,cameras,rows,note,evidence,scans,unloading,aggregates)}");out[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/delivery/StoreAdmissionPanel.tsx");s=p.read_text(encoding="utf-8").replace("WeightEvidence,StoreUnitScan","WeightEvidence,StoreUnitScan,StoreAggregateScan").replace("scans?:StoreUnitScan[])","scans?:StoreUnitScan[],aggregates?:StoreAggregateScan[])").replace('const [scans,setScans]=useState<StoreUnitScan[]>([]);','const [scans,setScans]=useState<StoreUnitScan[]>([]),[aggregates,setAggregates]=useState<StoreAggregateScan[]>([]),[scanValid,setScanValid]=useState(true);')
s=s.replace('const permitted=!disabled','const permitted=scanValid&&!disabled').replace('(preview.marked_partial_control?','(aggregates.length>0?true:preview.marked_partial_control?').replace('scans.length?scans:undefined);','scans.length?scans:undefined,aggregates.length?aggregates:undefined);').replace('onScans={setScans}/>', 'onScans={setScans} onAggregates={setAggregates} onValidity={setScanValid}/>');out[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/delivery/StoreMarkPanel.tsx")
out[str(p)]="""import {useEffect,useState} from "react";
import {StoreMarkMatrix} from "./StoreMarkMatrix";
import {receiptBase} from "./api";
import type {StorePreview,StoreUnitScan,StoreAggregateScan} from "./contracts";
type Draft={scans:StoreUnitScan[];aggregation_scans:StoreAggregateScan[]};
export function StoreMarkPanel({preview,username,disabled,onScans,onAggregates,onValidity}:{preview:Pick<StorePreview,'marked_unit_control'|'marked_partial_control'|'store_address'|'load_operation_id'|'composition_signature'|'requires_marked_recipient_flow'|'already_received'>;username:string;disabled:boolean;onScans:(v:StoreUnitScan[])=>void;onAggregates:(v:StoreAggregateScan[])=>void;onValidity:(v:boolean)=>void}) {
 const control=preview.marked_unit_control,profiles=control?.profiles||[];
 const [draft,setDraft]=useState<Draft>({scans:[],aggregation_scans:[]}),[selected,setSelected]=useState("0"),[kind,setKind]=useState("UNIT"),[code,setCode]=useState(""),[message,setMessage]=useState(""),[invalid,setInvalid]=useState(false);
 const [disposition,setDisposition]=useState<"ACCEPTED"|"REFUSED"|"DAMAGED">("ACCEPTED");
 const profile=profiles[Number(selected)],mode=profile?.scan_mode;
 const effective=mode==="UNIT_OR_AGGREGATION"?kind:mode;
 const oldKey="store-mark:"+username+":"+preview.store_address+":"+preview.load_operation_id+":"+preview.composition_signature+":"+JSON.stringify(profiles);
 const key=oldKey+":"+receiptBase();
 function notify(value:Draft){setDraft(value);onScans(value.scans);onAggregates(value.aggregation_scans);}
 useEffect(()=>{
  try {
   const raw=localStorage.getItem(key)??localStorage.getItem(oldKey),parsed:unknown=raw===null?{scans:[],aggregation_scans:[]}:JSON.parse(raw);
   const value=(Array.isArray(parsed)?{scans:parsed,aggregation_scans:[]}:parsed) as Draft;
   const valid=(x:StoreUnitScan)=>!!x&&typeof x.code==="string"&&new TextEncoder().encode(x.code).length<=4000&&x.code.length>0&&profiles.some(p=>p.system_code===x.system_code&&p.profile_code===x.profile_code)&&(!x.disposition||["ACCEPTED","REFUSED","DAMAGED"].includes(x.disposition));
   if(!value||!Array.isArray(value.scans)||!Array.isArray(value.aggregation_scans)||value.scans.length>20000||value.aggregation_scans.length>1000||!value.scans.every(valid)||!value.aggregation_scans.every(x=>valid(x)&&["BOX","PALLET"].includes(x.level)))throw Error("Invalid draft");
   notify(value);setInvalid(false);onValidity(true);setMessage("");
  }catch{notify({scans:[],aggregation_scans:[]});setInvalid(true);onValidity(false);setMessage("Сохранённый черновик повреждён. Новая отправка заблокирована; сохраните исходник и проверьте исход операции.");}
  // eslint-disable-next-line react-hooks/exhaustive-deps
 },[key]);
 function save(value:Draft){try{localStorage.setItem(key,JSON.stringify(value));notify(value);setMessage("");return true;}catch{setMessage("Не удалось сохранить сканы.");return false;}}
 function add(){
  if(disabled||invalid||!profile||!["UNIT","BOX","PALLET"].includes(effective||"")||!code)return;
  if(new TextEncoder().encode(code).length>4000){setMessage("Код превышает4000 байт.");return;}
  if([...draft.scans,...draft.aggregation_scans].some(x=>x.system_code===profile.system_code&&x.profile_code===profile.profile_code&&x.code===code)){setMessage("Этот код уже добавлен.");return;}
  const value={system_code:profile.system_code,profile_code:profile.profile_code,code,disposition};
  if(effective==="UNIT"){if(draft.scans.length>=20000)return;if(save({...draft,scans:[...draft.scans,value]}))setCode("");}
  else{if(draft.aggregation_scans.length>=1000)return;if(save({...draft,aggregation_scans:[...draft.aggregation_scans,{...value,level:effective as "BOX"|"PALLET"}]}))setCode("");}
 }
 if(!preview.requires_marked_recipient_flow||preview.already_received)return null;
 if(!control?.supported)return <p>Состав недоступен для сверки: {control?.reason}</p>;
 return <fieldset disabled={disabled||invalid}><legend>Сверка маркировки</legend>
  <StoreMarkMatrix control={control}/><p>QR: {draft.scans.length}. Агрегации: {draft.aggregation_scans.length}. Полноту состава и решение каждой штуки проверяет сервер.</p>
  <label>Профиль и разрешённый режим<select value={selected} onChange={e=>{setSelected(e.target.value);setCode("");}}>{profiles.map((p,i)=><option key={i} value={i}>{p.system_code} / {p.profile_code} · {p.profile_version} · {p.scan_mode}</option>)}</select></label>
  {mode==="UNIT_OR_AGGREGATION"&&<label>Способ сканирования<select value={kind} onChange={e=>{setKind(e.target.value);setCode("");}}><option value="UNIT">QR штуки</option><option value="BOX">Код коробки</option><option value="PALLET">Код исходной паллеты</option></select></label>}
  {preview.marked_partial_control&&<label>Решение для всего сканируемого состава<select value={disposition} onChange={e=>setDisposition(e.target.value as typeof disposition)}><option value="ACCEPTED">Принято</option><option value="REFUSED">Отказ</option><option value="DAMAGED">Повреждено</option></select></label>}
  <label>{effective==="UNIT"?"QR штуки":effective==="BOX"?"Код агрегации коробки":"Код агрегации исходной паллеты"}<input autoComplete="off" value={code} onChange={e=>setCode(e.target.value)} onKeyDown={e=>{if(e.key==="Enter"){e.preventDefault();add();}}}/></label>
  <button type="button" onClick={add}>Добавить</button><button type="button" onClick={()=>save({scans:[],aggregation_scans:[]})}>Очистить сканы</button><p role="status">{message}</p>
 </fieldset>;
}
"""
print(json.dumps(out,ensure_ascii=True))
