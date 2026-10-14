import { useState } from "react";
import { ReturnMarkPanel } from "./ReturnMarkPanel";
import type { ReturnMarkEvidence, StoreUnitScan } from "./contracts";
import { useReturnCustody } from "./useReturnCustody";
import type { ReturnStorePlace,ReturnDriverPlace } from "./custodyApi";

function StoreHandover({row,confirm,disabled,username}:{username:string;row:ReturnStorePlace;confirm:(body:{scans?:StoreUnitScan[];transport_operation_id:string;pallet_identifier:string;quantity:string;base_uom:string;gross_weight_kg:string;physical_places:number})=>Promise<void>;disabled:boolean}){
 const [scan,setScan]=useState(""),[mass,setMass]=useState(""),[quantity,setQuantity]=useState("");
 const [evidence,setEvidence]=useState<ReturnMarkEvidence>({scans:[],aggregation_scans:[]}),[markReady,setMarkReady]=useState(!row.marked_unit_control);
 const control=row.marked_unit_control;
 return <fieldset disabled={disabled}><p>{row.article} · {row.quantity} {row.base_uom} · рейс {row.tt_id} · план {row.planned_gross_weight_kg} кг / {row.physical_places} мест</p>
  <label>Идентификатор паллеты<input autoComplete="off" value={scan} onChange={event=>setScan(event.target.value)}/></label>
  <label>Фактически переданное количество, {row.base_uom}<input inputMode="decimal" value={quantity} onChange={event=>setQuantity(event.target.value)}/></label>
  <label>Фактическая масса брутто, кг<input inputMode="decimal" value={mass} onChange={event=>setMass(event.target.value)}/></label>
  <ReturnMarkPanel username={username} disabled={disabled} control={control} scope={"HANDOVER:"+row.transport_operation_id} onChange={(value,ready)=>{setEvidence(value);setMarkReady(ready);}}/>
  <button disabled={!markReady||!scan||!mass||!quantity} onClick={()=>void confirm({transport_operation_id:row.transport_operation_id,pallet_identifier:scan,quantity,base_uom:row.base_uom,gross_weight_kg:mass,physical_places:row.physical_places,...(control?evidence:{})})}>Магазин передал возврат</button>
 </fieldset>;
}

function DriverPickup({row,confirm,disabled,username}:{username:string;row:ReturnDriverPlace;confirm:(body:{scans?:StoreUnitScan[];handover_operation_id:string;scan_vehicle:string;scan_pallet:string})=>Promise<void>;disabled:boolean}){
 const [vehicle,setVehicle]=useState(""),[scan,setScan]=useState("");
 const [evidence,setEvidence]=useState<ReturnMarkEvidence>({scans:[],aggregation_scans:[]}),[markReady,setMarkReady]=useState(!row.marked_unit_control);
 const control=row.marked_unit_control;
 return <fieldset disabled={disabled}><p>{row.store_addr} · {row.pallet_identifier} · {row.gross_weight_kg} кг · передал {row.handed_by}</p>
  <label>Скан машины<input autoComplete="off" value={vehicle} onChange={event=>setVehicle(event.target.value)}/></label>
  <label>Скан паллеты возврата<input autoComplete="off" value={scan} onChange={event=>setScan(event.target.value)}/></label>
  <ReturnMarkPanel username={username} disabled={disabled} control={control} scope={"PICKUP:"+row.handover_operation_id} onChange={(value,ready)=>{setEvidence(value);setMarkReady(ready);}}/>
  <button disabled={!markReady||!vehicle||!scan} onClick={()=>void confirm({handover_operation_id:row.handover_operation_id,scan_vehicle:vehicle,scan_pallet:scan,...(control?evidence:{})})}>Водитель принял возврат</button>
 </fieldset>;
}

export function ReturnCustodyPanel({tripId,addresses}:{tripId:number;addresses:string[]}){
 const [mode,setMode]=useState<"store"|"driver">("store"),[address,setAddress]=useState(addresses[0]||"");
 const [username,setUsername]=useState(""),[password,setPassword]=useState("");
 const flow=useReturnCustody(tripId,address,mode,{username,password});
 const scope=mode+":"+address+":"+username;
 return <section className="driver-st-card"><h2>Возврат магазина</h2><p>Магазин и водитель отдельно подтверждают передачу согласованного возврата.</p>
  <fieldset disabled={flow.busy}>
   <label>Кто подтверждает<select value={mode} onChange={event=>setMode(event.target.value as "store"|"driver")}><option value="store">Получатель магазина</option><option value="driver">Водитель</option></select></label>
   {mode==="store"&&<label>Магазин<select value={address} onChange={event=>setAddress(event.target.value)}>{addresses.map(item=><option key={item}>{item}</option>)}</select></label>}
   <label>Учётная запись<input autoComplete="username" value={username} onChange={event=>setUsername(event.target.value)}/></label>
   <label>Пароль<input type="password" autoComplete="current-password" value={password} onChange={event=>setPassword(event.target.value)}/></label>
   <button disabled={!!flow.pending||flow.corrupt||!username||!password||(mode==="store"&&!address)} onClick={()=>void flow.load()}>Показать возвраты этого рейса</button>
  </fieldset>
  {flow.storeRows.map(row=><StoreHandover key={scope+":"+row.transport_operation_id} row={row} username={username} disabled={flow.busy||!!flow.pending||flow.corrupt} confirm={body=>flow.confirm("/handover",body)}/>)}
  {flow.driverRows.map(row=><DriverPickup key={scope+":"+row.handover_operation_id} row={row} username={username} disabled={flow.busy||!!flow.pending||flow.corrupt} confirm={body=>flow.confirm("/pickup",body)}/>)}
  {flow.corrupt&&<button disabled={flow.busy||!username||!password||(mode==="store"&&!address)} onClick={()=>void flow.recoverCorrupt()}>Сохранить повреждённый черновик и перечитать передачи</button>}
  {flow.pending&&<button disabled={flow.busy} onClick={()=>void flow.retry()}>Повторить сохранённую передачу</button>}
  {flow.pending?.confirmedRejection&&<button disabled={flow.busy} onClick={flow.restart}>Исправить подтверждённый отказ</button>}
  <p role="status">{flow.message}</p>
 </section>;
}
