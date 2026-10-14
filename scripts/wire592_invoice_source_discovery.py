from pathlib import Path
p=Path("api/wms_api_server/app/modules/finance/infrastructure/transport_cost_read.py");v=p.read_text(encoding="utf-8")
anchor='        return {"invoice_id":invoice,"items":items,'
assert anchor in v
v=v.replace(anchor,'''        cursor.execute("""select distinct l.TT_ID,l.WARE_ID from RRL_TT_HU_LOAD_FACT l
         join RRL_TRANSPORT_TASK t on t.ID=l.TT_ID
         join RUSERS u on u.ID=:actor and nvl(u.DELETED,0)=0
          and(u.WARE_ID=l.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')
          and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_view')=1
         where t.PAY_ORDER_ID=:invoice order by l.TT_ID,l.WARE_ID fetch first 201 rows only""",
                       actor=actor,invoice=invoice)
        sources=cursor.fetchall()
        if len(sources)>200:raise LogisticsCostError("TRANSPORT_INVOICE_SOURCE_BOUND","Не более 200 пар рейс/склад; используйте детализацию")
        return {"invoice_id":invoice,"sources":[{"trip":trip,"warehouse":ware}for trip,ware in sources],"items":items,''',1)
p.write_text(v,encoding="utf-8")
p=Path("admin/wms_admin_frontend/src/features/finance/BillingTransportCosts.tsx");v=p.read_text(encoding="utf-8")
v='import {TransportTariffSources} from "./TransportTariffSources";\n'+v
v=v.replace('type Result={invoice_id:number;','type Result={invoice_id:number;sources:Array<{trip:number;warehouse:number}>;')
v=v.replace('  <p>Показаны внутренние нормативные затраты.', '  {current?.sources.map(source=><TransportTariffSources key={source.trip+":"+source.warehouse} {...source}/>)}\n  <p>Показаны внутренние нормативные затраты.')
p.write_text(v,encoding="utf-8")
p=Path("admin/wms_admin_frontend/src/features/finance/BillingWarehouseCosts.tsx");v=p.read_text(encoding="utf-8")
v=v.replace('import {TransportTariffSources} from "./TransportTariffSources";\n','')
v=v.replace(' const trips=[...new Map(rows.map(row=>[row.tt_id+":"+row.ware_id,{trip:row.tt_id,warehouse:row.ware_id}])).values()];\n','')
v=v.replace('</section>{trips.map(row=><TransportTariffSources key={row.trip+":"+row.warehouse} {...row}/>)}','</section>')
p.write_text(v,encoding="utf-8")
print("592 transport norm/cost source discovery now uses original invoice trips/loads, independent of prior BOX money lines.")
