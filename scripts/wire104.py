from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py");s=p.read_text(encoding="utf-8-sig").replace("    def catalog(","    def forecast(self,ware_id: int,wave_id: int,actor: str) -> dict[str,Any]: ...\n    def catalog(",1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py");s=p.read_text(encoding="utf-8-sig").replace("    def catalog(",'''    def forecast(self,ware_id: int,wave_id: int,actor: str) -> dict[str,Any]:
        self._warehouse(ware_id,actor)
        wave=self.gateway.fetch_all("select PICK_WAVE_ID,STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=:wave and WARE_ID=:ware",{"wave":wave_id,"ware":ware_id})
        if not wave:raise TareError("TARE_FORECAST_WAVE_REQUIRED","Волна не принадлежит выбранному складу",409)
        counts=self.gateway.fetch_all("""
            select count(*) CASE_COUNT,
                   sum(case when exists(select 1 from RRL_WMS_HU_LINK h where h.CHILD_CASE_TASK_ID=t.CASE_PICK_TASK_ID and h.ACTIVE_FLAG=1) then 1 else 0 end) NESTED_CASE_COUNT
              from RRL_CASE_PICK_TASK t where t.PICK_WAVE_ID=:wave and t.WARE_ID=:ware and t.STATUS not in('SHIPPED','CANCELLED')
        """,{"wave":wave_id,"ware":ware_id})[0]
        if counts["case_count"]>10000:raise TareError("TARE_FORECAST_WAVE_WINDOW_REQUIRED","Разделите прогноз: в волне более 10000 мест CASE",409)
        rows=self.gateway.fetch_all("""
            with demand as(
             select t.PALLET_TYPE_ID,count(*) CASE_COUNT,
                    sum(case when RRL_TARE_PLANNING.case_booking(t.CASE_PICK_TASK_ID,t.WARE_ID,t.PALLET_TYPE_ID) is null then 1 else 0 end) UNBOOKED_COUNT
               from RRL_CASE_PICK_TASK t where t.PICK_WAVE_ID=:wave and t.WARE_ID=:ware and t.STATUS not in('SHIPPED','CANCELLED')
                and not exists(select 1 from RRL_WMS_HU_LINK h where h.CHILD_CASE_TASK_ID=t.CASE_PICK_TASK_ID and h.ACTIVE_FLAG=1)
              group by t.PALLET_TYPE_ID
            ), expected as(
             select o.PALLET_TYPE_ID,sum(o.QUANTITY) PROPOSED_RETURN_QTY from RRL_TARE_OFFER o
              where o.OWNER_WARE_ID=:ware and o.TO_KIND='WAREHOUSE' and o.TO_ID=to_char(:ware,'TM9') and o.CONDITION_CODE='GOOD'
               and not exists(select 1 from RRL_TARE_ACCEPT a where a.OFFER_OPERATION_ID=o.OPERATION_ID)
              group by o.PALLET_TYPE_ID
            )
            select t.PALLET_TYPE_ID,t.PALLET_TYPE_NAME,nvl(d.CASE_COUNT,0) STANDALONE_CASE_COUNT,
                   nvl(d.UNBOOKED_COUNT,0) UNBOOKED_CASE_COUNT,to_char(a.AVAILABLE_QTY,'TM9') AVAILABLE_QUANTITY,
                   case when a.BALANCE_KEY is null then null else to_char(greatest(nvl(d.UNBOOKED_COUNT,0)-a.AVAILABLE_QTY,0),'TM9') end SHORTAGE_QUANTITY,
                   to_char(nvl(e.PROPOSED_RETURN_QTY,0),'TM9') PROPOSED_RETURN_QUANTITY,
                   case when a.BALANCE_KEY is null then 'OBSERVATION_REQUIRED' else 'OBSERVED' end COUNT_STATE
              from RRL_PALLET_TYPE t left join demand d on d.PALLET_TYPE_ID=t.PALLET_TYPE_ID
               left join RRL_TARE_AVAILABILITY a on a.PALLET_TYPE_ID=t.PALLET_TYPE_ID and a.OWNER_WARE_ID=:ware
               left join expected e on e.PALLET_TYPE_ID=t.PALLET_TYPE_ID
             where t.ACTIVE=1 or d.PALLET_TYPE_ID is not null order by t.PALLET_TYPE_NAME fetch first 100 rows only
        """,{"wave":wave_id,"ware":ware_id})
        return {"warehouse_id":ware_id,"wave_id":wave_id,"wave_status":wave[0]["status"],"types":rows,
                "nested_case_count":counts["nested_case_count"] or 0,"scope":"EXISTING_STANDALONE_CASE",
                "planned_returns_are_available":False,"fullpal_type_assignment_required":True}

    def catalog(''',1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py");s=p.read_text(encoding="utf-8-sig")+'''
@router.get("/warehouses/{ware_id}/waves/{wave_id}/forecast")
def forecast(ware_id: int,wave_id: int,user: AdminUser=Depends(require_permission("tare_view")),service: TareAssemblyPort=Depends(tare_assembly_service)) -> dict[str,Any]:
    try:return service.forecast(ware_id,wave_id,user.username)
    except TareError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
''';out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/tare-assembly.html");s=p.read_text(encoding="utf-8-sig").replace('<div id="taAvailability"></div>','<div id="taAvailability"></div><h2>Потребность существующей волны</h2><label>Номер волны<input id="taWave" inputmode="numeric"></label><button id="taForecast">Показать потребность и недостачу</button><div id="taForecastRows"></div><p>Прогноз самостоятельных CASE. Для вложенных мест закрепите тару верхнего контейнера; для FULLPAL явно выберите тип поддона. Ожидаемые возвраты не увеличивают доступность.</p>',1);out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/tare-assembly.js");s=p.read_text(encoding="utf-8-sig").replace(' async function send(scope)', ''' async function forecast(){await read(async current=>{const wave=Number(el("taWave").value);if(!Number.isSafeInteger(wave)||wave<1)throw Error("Укажите существующую волну.");const data=await request("/warehouses/"+ware()+"/waves/"+wave+"/forecast");if(!current())return;el("taForecastRows").replaceChildren(...data.types.map(row=>{const p=document.createElement("p");p.textContent=row.pallet_type_name+" · незакреплённых CASE "+row.unbooked_case_count+" · свободно "+(row.available_quantity??"пересчёт не выполнен")+" · недостача "+(row.shortage_quantity??"не определена")+" · предложено вернуть "+row.proposed_return_quantity;return p;}));say("Вложенных CASE: "+data.nested_case_count+". Их тара учитывается верхним местом; ожидаемый возврат ещё не принят.");});}
 async function send(scope)''',1)
s=s.replace('[["taCatalog",catalog]','[["taForecast",forecast],["taCatalog",catalog]',1)
s=s.replace('++serial;bookings=[];', '++serial;el("taForecastRows").replaceChildren();bookings=[];')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
