import { useState } from "react";
import type { StorePreview, StoreDisposition } from "./contracts";

const counters = [["accepted","Принято"],["missing","Недостача"],["refused","Отказ"],["damaged","Повреждено"],["extra","Излишек"]] as const;
export function StoreDispositionPanel({preview,disabled,confirm,forceCounts=false,allowDiscrepancy=true}:{preview:StorePreview;disabled:boolean;forceCounts?:boolean;allowDiscrepancy?:boolean;confirm:(rows?:StoreDisposition[],note?:string)=>Promise<void>}) {
 const leaves=preview.snapshot.nodes.filter(node=>node.kind==="STOCK");
 const [partial,setPartial]=useState(false),[note,setNote]=useState("");
 const [rows,setRows]=useState<StoreDisposition[]>(()=>leaves.map(node=>({lot_uid:node.uid,accepted:node.quantity||"0",missing:"0",refused:"0",damaged:"0",extra:"0"})));
 const enabled=partial||forceCounts;
 function change(index:number,field:keyof StoreDisposition,value:string) {setRows(current=>current.map((row,i)=>i===index?{...row,[field]:value}:row));}
 return <div>
  <label><input type="checkbox" checked={enabled} disabled={disabled||forceCounts||!allowDiscrepancy} onChange={event=>setPartial(event.target.checked)}/>Указать фактические количества и расхождения</label>
  {enabled&&<>
   <p>Количество в базовых единицах позиции. Принято + недостача + отказ + повреждено должно равняться отправленному. Излишек регистрируется отдельно для разбирательства.</p>
   {rows.map((row,index)=><fieldset key={row.lot_uid} disabled={disabled}>
    <legend>{leaves[index].article} · {row.lot_uid} · отправлено {leaves[index].quantity} {leaves[index].base_uom}</legend>
    {counters.map(([field,label])=><label key={field}>{label}<input inputMode="decimal" value={row[field]} onChange={event=>change(index,field,event.target.value)}/></label>)}
   </fieldset>)}
   <label>Причина расхождения<textarea maxLength={2000} disabled={disabled} value={note} onChange={event=>setNote(event.target.value)}/></label>
  </>}
  <button disabled={disabled} onClick={()=>void confirm(enabled?rows:undefined,enabled?note:undefined)}>Подтвердить {enabled?"фактическую приёмку":"полную приёмку"}</button>
 </div>;
}
