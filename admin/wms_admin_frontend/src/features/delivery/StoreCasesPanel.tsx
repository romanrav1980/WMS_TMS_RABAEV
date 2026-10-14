import { useRef, useState } from "react";
type CaseItem={case_id:string;store_addr:string;status:string;reason_text:string;reported_by:string};
type CaseLine={line_no:number;lot_uid:string;article:string;base_uom:string;shipped_base_qty:string;accepted_base_qty:string;missing_base_qty:string;refused_base_qty:string;damaged_base_qty:string;reported_extra_base_qty:string};
type Obligation={line_no:number;kind:string;base_qty:string;base_uom:string;status:string};
type Dossier=CaseItem&{lines:CaseLine[];obligations:Obligation[];weight?:{shipping_gross_kg:string;observed_gross_kg:string;tolerance_kg:string;delta_kg:string;act_confirmed:number}|null};
const names:Record<string,string>={MISSING_INVESTIGATION:"Расследовать недостачу",REFUSED_RETURN_DECISION:"Решить возврат отказа",DAMAGED_RETURN_DECISION:"Решить возврат повреждённого",EXCESS_REVIEW:"Разобрать излишек"};
export function StoreCasesPanel({request}:{request:<T>(path:string)=>Promise<T>}) {
 const [address,setAddress]=useState(""),[cases,setCases]=useState<CaseItem[]>([]),[next,setNext]=useState<string|null>(null);
 const [dossier,setDossier]=useState<Dossier|null>(null),[busy,setBusy]=useState(false),[message,setMessage]=useState("");
 const scope=useRef(address);scope.current=address;
 async function load(after="") {
  const current=address;if(busy||!current)return;setBusy(true);setMessage("");
  try {const data=await request<{items:CaseItem[];next_after:string|null}>("/api/delivery/store-receipts/cases?store_address="+encodeURIComponent(current)+"&after="+encodeURIComponent(after));
   if(scope.current===current){setCases(data.items);setNext(data.next_after);setDossier(null);}
  }catch(error){if(scope.current===current)setMessage(String(error));}finally{setBusy(false);}
 }
 async function show(id:string) {
  const current=address;if(busy)return;setBusy(true);setMessage("");
  try {const data=await request<Dossier>("/api/delivery/store-receipts/cases/"+encodeURIComponent(id));if(scope.current===current)setDossier(data);}
  catch(error){if(scope.current===current)setMessage(String(error));}finally{setBusy(false);}
 }
 return <details><summary>Расхождения при приёмке магазинами</summary>
  <label>Адрес магазина<input value={address} onChange={event=>{setAddress(event.target.value);setCases([]);setNext(null);setDossier(null);}}/></label>
  <button disabled={busy||!address} onClick={()=>void load()}>Показать разбирательства</button>
  {cases.map(item=><p key={item.case_id}><button disabled={busy} onClick={()=>void show(item.case_id)}>{item.case_id} · {item.status} · {item.reason_text}</button></p>)}
  {next&&<button disabled={busy} onClick={()=>void load(next)}>Следующая страница</button>}
  {dossier&&<><p>{dossier.reason_text} · получатель: {dossier.reported_by}</p>
   {dossier.weight&&<p>Отгрузочное брутто {dossier.weight.shipping_gross_kg} кг; фактическое {dossier.weight.observed_gross_kg} кг; отклонение {dossier.weight.delta_kg} кг; допуск ±{dossier.weight.tolerance_kg} кг; акт {dossier.weight.act_confirmed?"подтверждён представителем":"не требуется"}.</p>}
   <table><thead><tr>{["Товар / паллета","ЕИ","Отправлено","Принято","Недостача","Отказ","Повреждено","Излишек"].map(name=><th key={name}>{name}</th>)}</tr></thead>
    <tbody>{dossier.lines.map(line=><tr key={line.line_no}><td>{line.article} / {line.lot_uid}</td><td>{line.base_uom}</td><td>{line.shipped_base_qty}</td><td>{line.accepted_base_qty}</td><td>{line.missing_base_qty}</td><td>{line.refused_base_qty}</td><td>{line.damaged_base_qty}</td><td>{line.reported_extra_base_qty}</td></tr>)}</tbody></table>
   <ul>{dossier.obligations.map(row=><li key={row.line_no+":"+row.kind}>{names[row.kind]||row.kind}: {row.base_qty} {row.base_uom}, строка {row.line_no}, {row.status}</li>)}</ul>
   <p>Разбирательство не разрешает возврат автоматически. Для изменения складского запаса требуется отдельное подтверждённое складское действие.</p>
  </>}
  <p role="status">{message}</p>
 </details>;
}
