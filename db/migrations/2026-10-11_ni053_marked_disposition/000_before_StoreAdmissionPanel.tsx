import { StoreMarkPanel } from "./StoreMarkPanel";
import { StoreBoxMassPanel } from "./StoreBoxMassPanel";
import { useState } from "react";
import { StorePhotoPanel } from "./StorePhotoPanel";
import { StoreScalePanel } from "./StoreScalePanel";
import { StoreDispositionPanel } from "./StoreDispositionPanel";
import type { ReceiptCredentials,StorePreview,StoreDisposition,WeightEvidence,StoreUnitScan } from "./contracts";

export function StoreAdmissionPanel({preview,credentials,disabled,confirm}:{preview:StorePreview;credentials:ReceiptCredentials;disabled:boolean;confirm:(rows?:StoreDisposition[],note?:string,evidence?:WeightEvidence,scans?:StoreUnitScan[])=>Promise<void>}) {
 const [capture,setCapture]=useState(""),[photos,setPhotos]=useState<string[]>([]),[act,setAct]=useState(false);
 const [scans,setScans]=useState<StoreUnitScan[]>([]);
 const weight=preview.mode==="WEIGHT_PHOTO";
 const permitted=!disabled&&!preview.already_received&&(!preview.requires_marked_recipient_flow||(preview.marked_unit_control?.supported&&scans.length===preview.marked_unit_control.expected_scan_count))&&
  (!weight||(!!capture&&photos.length>=3&&!!preview.shipping_weight_tolerance_kg));
 function send(rows?:StoreDisposition[],note?:string) {
  return confirm(rows,note,weight?{scale_capture_key:capture,photo_ids:photos,...(act?{weight_act_confirmed:true}:{})}:undefined,scans.length?scans:undefined);
 }
 return <>
  <StoreMarkPanel preview={preview} username={credentials.username} disabled={disabled} onScans={setScans}/>
  <StoreBoxMassPanel preview={preview}/>
  <StorePhotoPanel preview={preview} credentials={credentials} onEvidence={setPhotos}/>
  <StoreScalePanel preview={preview} credentials={credentials} selected={capture} onSelect={setCapture}/>
  {weight&&<>
   <p>Отгрузочное брутто: {preview.shipping_gross_weight_kg} кг. Допуск по самой лёгкой физической коробке: ±{preview.shipping_weight_tolerance_kg||"не подтверждён"} кг. Нужны показание шлюза и фотографии минимум с трёх разных сторон.</p>
   {!preview.shipping_weight_tolerance_kg&&<p>Отгрузочные измерения физических коробок отсутствуют. Требуется разбирательство логистики; приёмка по штрихкоду не заменяет весовой режим.</p>}
   <label><input type="checkbox" checked={act} disabled={disabled} onChange={event=>setAct(event.target.checked)}/>Принимаю по акту как уполномоченный представитель</label>
   {act&&<p>Укажите проверенные количества и причину. Право представителя проверяет сервер; расхождение веса само по себе не определяет количество недостачи.</p>}
  </>}
  <StoreDispositionPanel preview={preview} disabled={!permitted} allowDiscrepancy={!preview.requires_marked_recipient_flow} forceCounts={weight&&act} confirm={send}/>
 </>;
}
