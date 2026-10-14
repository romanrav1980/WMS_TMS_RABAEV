export type FloorLimit={pallet_type_id:number;max_places:number};
export type FloorVariant={code:string;limits:FloorLimit[]};
export type TareType={id:number;code:string;name:string};
export function VehicleTareVariants({value,types,onChange}:{value:FloorVariant[];types:TareType[];onChange:(value:FloorVariant[])=>void}){
 const update=(index:number,patch:Partial<FloorVariant>)=>onChange(value.map((v,i)=>i===index?{...v,...patch}:v));
 const add=()=>{
  let n=1;while(value.some(v=>v.code==="VARIANT"+n))n++;
  onChange([...value,{code:"VARIANT"+n,limits:[]}]);
 };
 return <section className="vehicle-tare-variants" aria-label="Нормативные варианты загрузки">
  <h4>Вместимость по типам тары</h4>
  <p>Каждая карточка — отдельное допустимое сочетание. Все указанные в ней типы могут ехать вместе в пределах заданных количеств. Типы вне карточки этим вариантом не разрешены.</p>
  {value.map((variant,index)=><article className="vehicle-tare-variant" key={index}>
   <div className="vehicle-tare-heading"><label>Код варианта<input value={variant.code} maxLength={40} required pattern="[A-Za-z0-9_.:-]{1,40}" onChange={e=>update(index,{code:e.target.value})}/></label>
    <button type="button" onClick={()=>onChange(value.filter((_,i)=>i!==index))}>Удалить вариант</button></div>
   {variant.limits.map((limit,row)=><div className="vehicle-tare-limit" key={row}>
    <label>Тип тары<select required value={limit.pallet_type_id||""} onChange={e=>update(index,{limits:variant.limits.map((v,i)=>i===row?{...v,pallet_type_id:Number(e.target.value)}:v)})}>
     <option value="">Выберите тип</option>{types.map(t=><option key={t.id} value={t.id} disabled={variant.limits.some((v,i)=>i!==row&&v.pallet_type_id===t.id)}>{t.name} · {t.code}</option>)}
    </select></label>
    <label>Максимум мест<input required type="number" min={1} max={1000} step={1} value={limit.max_places||""} onChange={e=>update(index,{limits:variant.limits.map((v,i)=>i===row?{...v,max_places:Number(e.target.value)}:v)})}/></label>
    <button type="button" onClick={()=>update(index,{limits:variant.limits.filter((_,i)=>i!==row)})}>Убрать тип</button>
   </div>)}
   <button type="button" disabled={variant.limits.length>=8||!types.length} onClick={()=>update(index,{limits:[...variant.limits,{pallet_type_id:0,max_places:1}]})}>Добавить тип тары</button>
  </article>)}
  <button type="button" disabled={value.length>=20} onClick={add}>Добавить вариант загрузки</button>
  {!value.length&&<p>Нормативные сочетания не заданы. Площадь пола не используется для их расчёта.</p>}
 </section>;
}
