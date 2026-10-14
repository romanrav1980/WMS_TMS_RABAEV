import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/finance/infrastructure/transport_tariff_sources.py");v=p.read_text(encoding="utf-8")
v=v.replace("from .cost_access import require_warehouse","from .cost_access import require_warehouse\nfrom ...platform.public import read_oracle_json")
v=v.replace("select ID,PRICE_NAME,COMPANY,TYPE_TR,","select p.ID,p.PRICE_NAME,p.COMPANY,p.TYPE_TR,")
v=v.replace("to_char(PRICE,","to_char(p.PRICE,").replace("to_char(PRICE_FOR_HOURS,","to_char(p.PRICE_FOR_HOURS,").replace("to_char(PRICE_FOR_ADDR,","to_char(p.PRICE_FOR_ADDR,").replace("to_char(NORM_HOURS,","to_char(p.NORM_HOURS,")
v=v.replace("""        from RRL_TRANSPORT_PRICE
        where (COMPANY=:company or COMPANY='DEFAULT')and
        (PRICE_NAME=:region_key or PRICE_NAME=:type_key)
        order by ID,PRICE_NAME,COMPANY""","""        ,h.RESULT_JSON from RRL_TRANSPORT_PRICE p
        left join RRL_TRANSPORT_NORM_HEAD nh on nh.SOURCE_PRICE_ID=p.ID and nh.WARE_ID=:ware
        left join RRL_TRANSPORT_NORM_HISTORY h on h.SOURCE_PRICE_ID=nh.SOURCE_PRICE_ID and h.VERSION_NO=nh.VERSION_NO
        where (p.COMPANY=:company or p.COMPANY='DEFAULT')and
        (p.PRICE_NAME=:region_key or p.PRICE_NAME=:type_key)
        order by p.ID,p.PRICE_NAME,p.COMPANY""")
v=v.replace('company=company,region_key=region_key,type_key=','ware=ware,company=company,region_key=region_key,type_key=')
v=v.replace('row=dict(zip(names,values))','row=dict(zip(names,values[:8]))')
v=v.replace('            result.append(row)','            row["published_norm"]=read_oracle_json(values[8])if values[8]is not None else None\n            result.append(row)')
out[str(p)]=v
out["admin/wms_admin_frontend/src/features/finance/TransportTariffSources.tsx"]='''import {useEffect,useState} from "react";
import {apiFetch} from "../../api";
type Norm={version:number;currency:string;effective_from:string;vehicle_size_class:string;rolling_unload_rate:string;manual_unload_rate:string;loader_rate:string};
type Candidate={id:number;price_name:string;company:string;vehicle_rate:string;hour_rate:string;point_rate:string;match_kind:string;published_norm:Norm|null};
type Source={trip_id:number;warehouse_id:number;carrier:string|null;vehicle_type:string;legacy_region_key:string;candidates:Candidate[];selection_state:string;actual_receipt_count:number;receipt_address_count:number};
export function TransportTariffSources({trip,warehouse}:{trip:number;warehouse:number}){
 const [data,setData]=useState<Source|null>(null),[error,setError]=useState(""),[busy,setBusy]=useState(false);
 useEffect(()=>{setData(null);setError("");setBusy(false);},[trip,warehouse]);
 async function read(){
  setBusy(true);setError("");
  try{setData(await apiFetch<Source>(`/api/finance/logistics-costs/trips/${trip}/transport-tariff-sources?warehouse_id=${warehouse}`));}
  catch(e){setError(e instanceof Error?e.message:"Не удалось прочитать тариф.");}
  finally{setBusy(false);}
 }
 const current=data?.trip_id===trip&&data.warehouse_id===warehouse?data:null;
 return <section aria-label="Тариф перевозки">
  <button type="button" onClick={read} disabled={busy}>{busy?"Загрузка…":`Тариф перевозки рейса ${trip}, склад ${warehouse}`}</button>
  {error&&<p role="alert">{error}</p>}
  {current&&<><p>Перевозчик: {current.carrier||"не указан"}. Тип машины: {current.vehicle_type}. Региональный ключ: {current.legacy_region_key}.</p>
   {current.candidates.length===0?<p>Подходящий транспортный тариф не настроен.</p>:<table><thead><tr><th>Исходный тариф</th><th>Автомобиль</th><th>Час</th><th>Точка</th><th>Опубликованная норма</th></tr></thead>
    <tbody>{current.candidates.map((r,i)=><tr key={r.id+":"+i}><td>{r.price_name} / {r.company}</td><td>{r.vehicle_rate}</td><td>{r.hour_rate}</td><td>{r.point_rate}</td>
    <td>{r.published_norm?<>{r.published_norm.currency}, версия {r.published_norm.version}, с {r.published_norm.effective_from}; класс {r.published_norm.vehicle_size_class}<small>Выгрузка тележки {r.published_norm.rolling_unload_rate}, вручную {r.published_norm.manual_unload_rate}, дополнительный грузчик {r.published_norm.loader_rate}.</small></>:"Валюта, период и нормы выгрузки требуют настройки"}</td></tr>)}</tbody></table>}
   <p>Зафиксировано приёмок: {current.actual_receipt_count}, адресов: {current.receipt_address_count}. Способ выгрузки и работа грузчика подтверждаются отдельно. Просмотр тарифа не начисляет расходы.</p>
  </>}
 </section>;
}
'''
p=Path("admin/wms_admin_frontend/src/features/finance/BillingWarehouseCosts.tsx");v=p.read_text(encoding="utf-8")
v=v.replace('import {BillingExtraExpenses}', 'import {TransportTariffSources} from "./TransportTariffSources";\nimport {BillingExtraExpenses}')
v=v.replace('"начало CASE"','"начало сборки коробки"')
needle=' const current=summary?.invoice_id===invoiceId?summary:null,rows=current?.lines||[];'
assert needle in v
v=v.replace(needle,needle+'\n const trips=[...new Map(rows.map(row=>[row.tt_id+":"+row.ware_id,{trip:row.tt_id,warehouse:row.ware_id}])).values()];')
# Keep the existing separate expense section and show source details lazily.
needle='<BillingExtraExpenses invoiceId={invoiceId}/>'
assert needle in v
v=v.replace(needle,'{trips.map(row=><TransportTariffSources key={row.trip+":"+row.warehouse} {...row}/>)}'+needle)
out[str(p)]=v
print(json.dumps(out))
