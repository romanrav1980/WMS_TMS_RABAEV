// C-0020 (NI06.3): подтверждённое заявление о недостаче и переход к этому случаю в существующем реестре
// недостач (raw tare-loss.html) с тем же складом и ID. Решение принимается только там, другим сотрудником.
// Адрес raw-интерфейса задаётся VITE_RAW_ADMIN_BASE; без него показываются точные склад и ID для поиска.
export type LossConfirmed={operation_id:string;owner_ware_id:number;quantity:string;decision_reference:string;custodian_kind:string;custodian_id:string};

export function lossRegistryUrl(c:LossConfirmed):string|null{
 const base=String(import.meta.env.VITE_RAW_ADMIN_BASE||"").replace(/\/$/,"");
 if(!base)return null;
 return base+"/tare-loss.html?"+new URLSearchParams({warehouse_id:String(c.owner_ware_id),claim_id:c.operation_id});
}

export function TareLossCase({claim}:{claim:LossConfirmed}){
 const url=lossRegistryUrl(claim);
 return <section className="tare-case" aria-label="Заявление о недостаче">
  <header><strong>Акт {claim.decision_reference}</strong><span className="tare-chip">Ожидает независимого решения</span></header>
  <dl className="tare-facts">
   <div><dt>Склад-владелец</dt><dd>{claim.owner_ware_id}</dd></div>
   <div><dt>Держатель</dt><dd>{claim.custodian_kind} {claim.custodian_id}</dd></div>
   <div><dt>Не обнаружено</dt><dd>{claim.quantity}</dd></div>
   <div><dt>Заявление</dt><dd>{claim.operation_id}</dd></div>
  </dl>
  <p className="tare-next">Количество исключено из доступной тары. Списать или отклонить заявление может только другой сотрудник с правом списания в реестре недостач.</p>
  {url
   ?<a href={url} target="_blank" rel="noopener" title="Открыть этот случай в реестре недостач; склад и заявление будут выбраны">Открыть случай в реестре недостач</a>
   :<p role="status">Откройте «Недостача складской тары» → склад {claim.owner_ware_id} → заявление {claim.operation_id}.</p>}
 </section>;
}
