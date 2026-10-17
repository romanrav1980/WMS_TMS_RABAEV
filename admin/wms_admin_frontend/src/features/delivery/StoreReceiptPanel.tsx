import {receiptBase} from "./api";
import {StoreReceiptAct} from "./StoreReceiptAct";
import {StoreUnloadingPanel} from "./StoreUnloadingPanel";
import type {UnloadingDetails} from "./contracts";
import { useEffect,useState } from "react";
import { useStoreReceipt } from "./useStoreReceipt";
import { StoreAdmissionPanel } from "./StoreAdmissionPanel";

export function StoreReceiptPanel({tripId,addresses}:{tripId:number;addresses:string[]}) {
 const [address,setAddress]=useState(addresses[0]||"");
 const [username,setUsername]=useState(""),[password,setPassword]=useState("");
 const [scan,setScan]=useState(""),[cameras,setCameras]=useState(false);
 const flow=useStoreReceipt(tripId,address,{username,password});
 const preview=flow.preview;
 const [unloading,setUnloading]=useState<UnloadingDetails|undefined>(),[unloadPending,setUnloadPending]=useState(false);
 useEffect(()=>{setScan('');setCameras(false);setUnloading(undefined);setUnloadPending(false);},[tripId,address,username,preview?.load_operation_id]);
 return <section className="driver-st-card">
  <h2>Приёмка магазина</h2><p>Подтверждение фактического состава получателем магазина.</p>
  <p><a href={receiptBase()+"/store/"} target="_blank" rel="noopener noreferrer" title="Открыть отдельное приложение приёмщика магазина со своим входом, поставками и стратегией приёмки" data-help-id="store.app.open" data-help-article="store-receiving-app">Открыть приложение магазина</a></p>
  <fieldset disabled={flow.busy}>
   {flow.corrupt&&<button onClick={()=>void flow.recover()}>Сохранить повреждённую операцию в архив и перечитать места</button>}
   <label>Адрес магазина<select value={address} onChange={event=>{setAddress(event.target.value);setScan("");setCameras(false);}}>
    <option value="">Выберите адрес</option>{addresses.map(item=><option key={item}>{item}</option>)}
   </select></label>
   <label>Пользователь получателя<input autoComplete="username" value={username} onChange={event=>setUsername(event.target.value)}/></label>
   <label>Пароль<input type="password" autoComplete="current-password" value={password} onChange={event=>setPassword(event.target.value)}/></label>
   <button onClick={()=>void flow.loadPlaces()} disabled={!address||!username||!password}>Показать доставленные места</button>
   {flow.places.map(place=><p key={place.load_operation_id}><button onClick={()=>void flow.show(place.load_operation_id)}>
    {place.root_key} · {place.receipt_state||"Ожидает приёмки"}</button></p>)}
   {flow.more&&<button onClick={()=>void flow.next()} disabled={flow.busy||flow.corrupt}>Следующие грузовые места</button>}
   {preview&&<>
    <p>Грузовое место: {preview.root_scan_identifier}; режим: {preview.mode==="BARCODE"?"по идентификатору":preview.mode==="PAPER_COUNT"?"пересчёт по бумаге":"вес и фотографии"}.</p>
    <ul>{preview.snapshot.nodes.filter(node=>node.kind==="STOCK").map(node=><li key={node.uid}>{node.article}: {node.quantity} {node.base_uom}</li>)}</ul>
    {preview.already_received&&<p>Это место уже принято.</p>}
    {preview.mode==="WEIGHT_PHOTO"&&<p>Для этого адреса обязательны весовой контроль и фотографии. Приёмка только по скану не разрешена.</p>}
    {preview.requires_marked_recipient_flow&&<p>Сверьте уникальные коды по обязательным профилям товара. Государственное подтверждение учитывается отдельно.</p>}
    {preview.mode==="PAPER_COUNT"?<p>Для пересчёта по бумаге откройте приложение магазина: оно сохраняет реквизит документа и фактическое количество каждой строки.</p>:<>
    <label>Идентификатор грузового места<input autoComplete="off" value={scan} onChange={event=>setScan(event.target.value)}/></label>
    <label><input type="checkbox" checked={cameras} onChange={event=>setCameras(event.target.checked)}/>Грузовое место установлено перед камерами</label>
    <StoreUnloadingPanel key={username+":"+preview.load_operation_id+":"+preview.store_address} preview={preview} credentials={{username,password}} scan={scan} cameras={cameras} disabled={flow.busy||!!flow.pending}
      onDetails={setUnloading} onPending={setUnloadPending} onStarted={()=>flow.show(preview.load_operation_id)}/>
    <StoreAdmissionPanel key={username+":"+preview.load_operation_id+":"+preview.store_address+":"+preview.composition_signature} preview={preview} credentials={{username,password}} disabled={flow.busy||flow.stalePreview||!scan||!cameras||!!flow.pending||unloadPending||(preview.unloading?.status==="STARTED"&&!unloading)} confirm={(rows,note,evidence,scans,aggregates)=>flow.confirm(scan,cameras,rows,note,evidence,scans,unloading,aggregates)}/>
    </>}
   </>}
   {flow.pending&&<button onClick={()=>void flow.retry()}>Повторить сохранённую операцию</button>}
   {flow.pending?.confirmedRejection&&<button onClick={()=>void flow.restart()}>Исправить данные после отказа</button>}
  </fieldset><p role="status">{flow.message}</p>{flow.lastReceipt&&<StoreReceiptAct result={flow.lastReceipt}/>}
 </section>;
}
