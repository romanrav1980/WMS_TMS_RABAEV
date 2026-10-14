import {useEffect,useRef,useState} from "react";
import "./VehiclePhysicalProfile.css";
import {VehicleTareVariants,type FloorVariant,type TareType} from "./VehicleTareVariants";
import {apiFetch,apiOperationScope,ApiRequestError} from "../../api";
type Fields={vehicle_size_class:string;cargo_length_mm:string;cargo_width_mm:string;cargo_height_mm:string;reason:string;evidence_reference:string;temp_min_c:string;temp_max_c:string};
type Profile={vehicle_id:number;version:number;state:"READY"|"NOT_CONFIGURED"|"BASE_CHANGED";base_hash:string;base:{vehicle_number:string;vehicle_type:string;pallet_capacity:string;max_weight_kg:string};profile?:{vehicle_size_class:string;cargo_length_mm:number;cargo_width_mm:number;cargo_height_mm:number;version:number;actor:string;evidence_reference:string;temperature_capability?:{temp_min_c:string;temp_max_c:string;measurement_verified:false};floor_capacity?:{variants:FloorVariant[];basis:string;evidence_reference:string}}};
type Body={operation_id:string;vehicle_id:number;vehicle_size_class:string;cargo_length_mm:number;cargo_width_mm:number;cargo_height_mm:number;expected_version:number;expected_source_hash:string;reason:string;evidence_reference:string;temp_min_c?:string;temp_max_c?:string;floor_variants?:FloorVariant[]};
type Pending={body:Body;rejected?:boolean};
const labels:Record<keyof Fields,string>={vehicle_size_class:"Код класса машины",cargo_length_mm:"Длина отсека, мм",cargo_width_mm:"Ширина отсека, мм",cargo_height_mm:"Высота отсека, мм",reason:"Причина настройки",evidence_reference:"Основание габаритов и температурного диапазона",temp_min_c:"Минимум температуры машины, °C",temp_max_c:"Максимум температуры машины, °C"};
export function VehiclePhysicalProfile({vehicle,onClose}:{vehicle:number;onClose:()=>void}){
 const scope="vehicle-profile:"+apiOperationScope()+":"+vehicle;
 const current=useRef(scope);current.current=scope;const running=useRef(false);
 const [profile,setProfile]=useState<Profile|null>(null),[pending,setPending]=useState<Pending|null>(null),[busy,setBusy]=useState(false),[blocked,setBlocked]=useState(false),[message,setMessage]=useState("");
 const [variants,setVariants]=useState<FloorVariant[]>([]),[tareTypes,setTareTypes]=useState<TareType[]>([]);
 const [fields,setFields]=useState<Fields>({vehicle_size_class:"",cargo_length_mm:"",cargo_width_mm:"",cargo_height_mm:"",reason:"",evidence_reference:"",temp_min_c:"",temp_max_c:""});
 useEffect(()=>{
  setProfile(null);setMessage("");setPending(null);setBlocked(false);setVariants([]);setTareTypes([]);
  try{const saved=JSON.parse(localStorage.getItem(scope)||"null")as Pending|null;
   if(saved!==null&&(!saved.body||saved.body.vehicle_id!==vehicle||typeof saved.body.operation_id!=="string"||! /^[A-Za-z0-9_.:-]{1,100}$/.test(saved.body.operation_id)||! /^[0-9A-F]{64}$/.test(saved.body.expected_source_hash)||(saved.rejected!==undefined&&typeof saved.rejected!=="boolean")))throw new Error("Повреждена сохранённая настройка; новая операция заблокирована.");
   setPending(saved);
  }catch(e){setBlocked(true);setMessage(String(e));}
  return()=>{current.current="";};
 },[scope]);
 async function fetchProfile(){
  const [value,types]=await Promise.all([apiFetch<Profile>("/api/admin/transport/vehicles/"+vehicle+"/profile"),apiFetch<TareType[]>("/api/admin/transport/vehicle-profiles/tare-types")]);
  if(current.current===scope){setProfile(value);setTareTypes(types);setVariants(value.profile?.floor_capacity?.variants??[]);setFields(v=>({...v,vehicle_size_class:value.profile?.vehicle_size_class||"",cargo_length_mm:value.profile?String(value.profile.cargo_length_mm):"",cargo_width_mm:value.profile?String(value.profile.cargo_width_mm):"",cargo_height_mm:value.profile?String(value.profile.cargo_height_mm):"",temp_min_c:value.profile?.temperature_capability?.temp_min_c??"",temp_max_c:value.profile?.temperature_capability?.temp_max_c??""}));}
  return value;
 }
 async function read(){
  if(running.current)return;running.current=true;setBusy(true);
  try{await fetchProfile();}catch(e){if(current.current===scope)setMessage(String(e));}
  finally{running.current=false;if(current.current===scope)setBusy(false);}
 }
 async function send(intent:Pending){
  if(running.current||blocked)return;
  const raw=localStorage.getItem(scope);
  if(current.current!==scope||raw!==JSON.stringify(intent)){setBlocked(true);setMessage("Сохранённая операция изменилась. Отправка остановлена; перечитайте карточку.");return;}
  running.current=true;setBusy(true);const key=scope;
  try{
   const result=await apiFetch<{version:number}>("/api/admin/transport/vehicle-profiles",{method:"POST",body:JSON.stringify(intent.body)});
   if(current.current!==key||localStorage.getItem(key)!==raw)return;
   localStorage.removeItem(key);
   if(current.current===key){setPending(null);setMessage("Профиль сохранён, версия "+result.version+".");try{await fetchProfile();}catch(e){if(current.current===key)setMessage("Версия "+result.version+" сохранена; обновить карточку не удалось: "+String(e));}}
  }catch(e){if(current.current===key&&localStorage.getItem(key)===raw){
   const saved={...intent,rejected:e instanceof ApiRequestError&&e.confirmedRejection};setPending(saved);
   try{localStorage.setItem(key,JSON.stringify(saved));}catch{setBlocked(true);}
   setMessage(String(e)+(saved.rejected?" Сервер подтвердил отказ.":" Результат не подтверждён; повторите ту же операцию."));
  }}finally{running.current=false;if(current.current===key)setBusy(false);}
 }
 async function save(event:React.FormEvent){
  event.preventDefault();if(!profile||busy||running.current||pending||blocked)return;
  const dimensions=[fields.cargo_length_mm,fields.cargo_width_mm,fields.cargo_height_mm];
  if(dimensions.some(v=>! /^[0-9]{1,7}$/.test(v)||Number(v)<1||Number(v)>1000000)){setMessage("Укажите целые положительные габариты в миллиметрах.");return;}
  const hasTemperature=fields.temp_min_c!==""||fields.temp_max_c!=="";
  if(hasTemperature&&(!/^-?[0-9]{1,6}(\.[0-9]{1,3})?$/.test(fields.temp_min_c)||!/^-?[0-9]{1,6}(\.[0-9]{1,3})?$/.test(fields.temp_max_c)||Number(fields.temp_min_c)>Number(fields.temp_max_c))){
   setMessage("Укажите оба температурных предела в °C, до трёх знаков после точки.");return;
  }
  if(variants.length>20||new Set(variants.map(v=>v.code)).size!==variants.length||variants.some(v=>! /^[A-Za-z0-9_.:-]{1,40}$/.test(v.code)||!v.limits.length||v.limits.length>8||new Set(v.limits.map(l=>l.pallet_type_id)).size!==v.limits.length||v.limits.some(l=>!Number.isInteger(l.max_places)||l.max_places<1||l.max_places>1000||!tareTypes.some(t=>t.id===l.pallet_type_id)))){
   setMessage("Укажите разные коды вариантов и активные типы тары с целым количеством1–1000.");return;
  }
  const intent:Pending={body:{operation_id:"VEHICLE.PROFILE:"+crypto.randomUUID(),vehicle_id:vehicle,vehicle_size_class:fields.vehicle_size_class,
   cargo_length_mm:Number(fields.cargo_length_mm),cargo_width_mm:Number(fields.cargo_width_mm),cargo_height_mm:Number(fields.cargo_height_mm),
   expected_version:profile.version,expected_source_hash:profile.base_hash,reason:fields.reason,evidence_reference:fields.evidence_reference,...(hasTemperature?{temp_min_c:fields.temp_min_c,temp_max_c:fields.temp_max_c}:{}),...(variants.length?{floor_variants:variants}:{})}};
  try{localStorage.setItem(scope,JSON.stringify(intent));setPending(intent);await send(intent);}catch(e){setMessage("Не удалось сохранить операцию до отправки: "+String(e));}
 }
 async function reset(){
  if(running.current||!pending?.rejected)return;running.current=true;setBusy(true);
  try{await fetchProfile();if(current.current===scope){localStorage.removeItem(scope);setPending(null);setMessage("Карточка обновлена. Исправьте поля новой операции.");}}
  catch(e){if(current.current===scope)setMessage(String(e));}
  finally{running.current=false;if(current.current===scope)setBusy(false);}
 }
 return <section className="vehicle-profile-card" aria-label="Физический класс автомобиля"><h3>Класс, грузовой отсек, температура и тара</h3>
  <button type="button" title="Прочитать текущую карточку автомобиля и версию габаритов" disabled={busy} onClick={()=>void read()}>Показать текущую карточку</button>
  <button type="button" title="Закрыть карточку; неподтверждённая операция сохранится для точного повтора" disabled={busy} onClick={onClose}>Закрыть</button>
  {profile&&<p>{profile.base.vehicle_number} · тип {profile.base.vehicle_type} · {profile.base.pallet_capacity} паллет · {profile.base.max_weight_kg} кг. Версия {profile.version}. {profile.state==="READY"?"Профиль соответствует карточке.":profile.state==="BASE_CHANGED"?"Карточка изменилась; требуется подтверждение нового профиля.":"Габариты и класс ещё не настроены."}</p>}
  <form onSubmit={e=>void save(e)}><fieldset disabled={busy||!!pending||blocked||!profile}>
   {(Object.keys(labels)as Array<keyof Fields>).map(k=><label key={k}>{labels[k]}<input title={labels[k]+" для подтверждённой версии профиля"} required={!k.startsWith("temp_")} value={fields[k]} maxLength={k==="reason"?500:k==="evidence_reference"?100:k==="vehicle_size_class"?40:k.startsWith("temp_")?11:7} inputMode={k.startsWith("cargo_")?"numeric":k.startsWith("temp_")?"decimal":"text"} onChange={e=>setFields(v=>({...v,[k]:e.target.value}))}/></label>)}
   <VehicleTareVariants value={variants} types={tareTypes} onChange={setVariants}/>
   <button type="submit" title="Сохранить новую версию класса и габаритов с проверкой текущей карточки автомобиля">Сохранить профиль</button>
  </fieldset></form>
  {pending&&<><p>Сохранённая операция: {pending.body.operation_id}.</p><button type="button" title="Повторить неизменённый запрос с прежним идентификатором" disabled={busy||blocked} onClick={()=>void send(pending)}>Повторить сохранённую операцию</button></>}
  {pending?.rejected&&<button type="button" title="Обновить карточку после подтверждённого отказа и разрешить новую редакцию" disabled={busy} onClick={()=>void reset()}>Исправить после отказа</button>}
  <p>Температурные пределы задаются парой по подтверждённым возможностям машины. Пустые поля означают отсутствие подтверждённого диапазона; измерением температуры они не являются.</p>
  <p>Профиль фиксируется в источнике нового выезда. История завершённых рейсов сохраняется.</p>
  {message&&<p className="vehicle-profile-status" role="status">{message}</p>}
 </section>;
}
