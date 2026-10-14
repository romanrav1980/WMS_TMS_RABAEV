import { useEffect,useRef,useState } from "react";
import { listPhotos,photoContent,uploadPhoto } from "./photoApi";
import type { ReceiptPhoto } from "./photoApi";
import type { ReceiptCredentials,StorePreview } from "./contracts";

const views:Record<string,string>={FRONT:"Спереди",LEFT:"Слева",RIGHT:"Справа",BACK:"Сзади",TOP:"Сверху"};

export function StorePhotoPanel({preview,credentials,onEvidence}:{preview:StorePreview;credentials:ReceiptCredentials;onEvidence?:(ids:string[])=>void}) {
 const [photos,setPhotos]=useState<ReceiptPhoto[]>([]),[file,setFile]=useState<File|null>(null),[view,setView]=useState("FRONT");
 const [evidence,setEvidence]=useState<string[]>([]);const fileInput=useRef<HTMLInputElement>(null);
 const [busy,setBusy]=useState(false),[message,setMessage]=useState("");
 const scope=preview.load_operation_id+":"+preview.store_address+":"+credentials.username.toLowerCase();
 const current=useRef(scope);current.current=scope;
 useEffect(()=>{current.current=scope;setPhotos([]);setEvidence([]);setFile(null);setMessage("");return()=>{current.current="";};},[scope]);
 function choose(data:ReceiptPhoto[]) {
  const seenViews=new Set<string>(),seenAssets=new Set<string>(),ids:string[]=[];
  for(const photo of [...data].reverse()){
   if(seenViews.has(photo.view)||seenAssets.has(photo.sha256))continue;
   seenViews.add(photo.view);seenAssets.add(photo.sha256);ids.push(photo.photo_id);
  }
  setEvidence(ids);onEvidence?.(ids);
 }
 function select(id:string,checked:boolean) {
  const next=checked?[...evidence,id]:evidence.filter(item=>item!==id);setEvidence(next);onEvidence?.(next);
 }
 async function refresh() {
  if(busy)return;const captured=scope;setBusy(true);
  try {const data=await listPhotos(preview.load_operation_id,preview.store_address,credentials);if(current.current===captured){setPhotos(data);choose(data);}}
  catch(error){if(current.current===captured)setMessage(String(error));}
  finally {setBusy(false);}
 }
 async function upload() {
  if(busy||!file)return;
  if(!["image/jpeg","image/png"].includes(file.type)||file.size>4*1024*1024){setMessage("Выберите фотографию JPEG/PNG размером до 4 МиБ.");return;}
  const captured=scope;setBusy(true);
  try {
   await uploadPhoto(preview.load_operation_id,preview.store_address,view,file,credentials);
   const data=await listPhotos(preview.load_operation_id,preview.store_address,credentials);
   if(current.current===captured){setPhotos(data);choose(data);setFile(null);if(fileInput.current)fileInput.current.value="";setMessage("Оригинал фотографии сохранён.");}
  }catch(error){if(current.current===captured)setMessage(String(error)+" При отсутствии подтверждения повторите тот же файл и сторону.");}
  finally {setBusy(false);}
 }
 async function download(photo:ReceiptPhoto) {
  if(busy)return;const captured=scope;setBusy(true);
  try {
   const blob=await photoContent(photo,credentials);
   if(current.current!==captured)return;
   const url=URL.createObjectURL(blob),link=document.createElement("a");
   link.href=url;link.download="photo-"+photo.view+"-"+photo.photo_id.slice(0,8)+(photo.mime_type==="image/png"?".png":".jpg");
   link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }catch(error){if(current.current===captured)setMessage(String(error));}
  finally {setBusy(false);}
 }
 return <section>
  <h3>Фотоархив грузового места</h3>
  <fieldset disabled={busy}>
   <label>Сторона<select value={view} onChange={event=>setView(event.target.value)}>
    {Object.entries(views).map(([code,label])=><option value={code} key={code}>{label}</option>)}
   </select></label>
   <input ref={fileInput} type="file" accept="image/jpeg,image/png" capture="environment" onChange={event=>setFile(event.target.files?.[0]||null)}/>
   <button disabled={!file} onClick={()=>void upload()}>Сохранить фотографию</button>
   <button onClick={()=>void refresh()}>Показать фотоархив</button>
   {photos.map(photo=><p key={photo.photo_id}>{onEvidence&&<label><input type="checkbox" checked={evidence.includes(photo.photo_id)} onChange={event=>select(photo.photo_id,event.target.checked)}/>Включить в подтверждение</label>}{views[photo.view]||photo.view} · {new Date(photo.recorded_at).toLocaleString()}
    <button onClick={()=>void download(photo)}>Скачать оригинал</button></p>)}
  </fieldset><p role="status">{message}</p>
 </section>;
}
