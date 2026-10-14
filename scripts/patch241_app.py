from pathlib import Path
root=Path("api/wms_api_server/app/modules/inventory")
p=root/"contracts_interwarehouse.py";s=p.read_text(encoding="utf-8").replace("    def record_temperature(self,","    def incoming(self, trip_id: int, actor: str) -> dict[str, Any]: ...\n    def record_temperature(self,",1);p.write_text(s,encoding="utf-8")
p=root/"infrastructure/interwarehouse.py";s=p.read_text(encoding="utf-8").replace("    def record_temperature(self,","    def incoming(self, trip_id: int, actor: str) -> dict[str, Any]:\n        from .interwarehouse_incoming import InterwarehouseIncoming\n        return InterwarehouseIncoming(self.gateway).read(trip_id,actor)\n\n    def record_temperature(self,",1);p.write_text(s,encoding="utf-8")
p=root/"api/interwarehouse_routes.py";s=p.read_text(encoding="utf-8");s+='''

@router.get("/trips/{trip_id}/incoming")
def incoming(trip_id: int,user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    try:
        return service.incoming(trip_id,user.username)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
''';p.write_text(s,encoding="utf-8")
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.html");s=p.read_text(encoding="utf-8").replace('<section class="panel" data-permission="transport_dispatch_edit"><h2>Связать','''<section class="panel" data-permission="transport_dispatch_view"><h2>Все подвозы целевого рейса</h2><label>Существующий рейс<input id="iwIncomingTrip" inputmode="numeric"></label><button id="iwIncomingLoad">Показать готовность подвозов</button><p id="iwIncomingStatus"></p><div id="iwIncomingRows"></div><p>Показаны межскладские обещания этому рейсу. Общая готовность подвозов не заменяет проверку вместимости, водителя, прочих СТ и разрешение выезда.</p></section><section class="panel" data-permission="transport_dispatch_edit"><h2>Связать''',1);p.write_text(s,encoding="utf-8")
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
s=s.replace('el("iwRows").replaceChildren();el("iwPhysicalPlan").replaceChildren();','el("iwRows").replaceChildren();el("iwIncomingRows").replaceChildren();el("iwIncomingStatus").textContent="";el("iwPhysicalPlan").replaceChildren();')
s=s.replace('el("iwThermalSave").addEventListener','''el("iwIncomingLoad").addEventListener("click",async()=>{if(busy||pending)return;const scope=key(),trip=Number(el("iwIncomingTrip").value);if(!Number.isSafeInteger(trip)||trip<1){say("Укажите существующий рейс.");return;}busy=true;controls();try{
 const result=await request("/trips/"+trip+"/incoming");if(scope!==key()||trip!==Number(el("iwIncomingTrip").value))return;
 el("iwIncomingStatus").textContent="Ожидается поставок: "+result.expected_deliveries+" · погружено и не приостановлено: "+result.ready_deliveries+". "+(result.incoming_ready?"Все указанные подвозы погружены.":"Межскладские подвозы пока не готовы.");
 el("iwIncomingRows").replaceChildren(...result.plans.map(row=>{const p=document.createElement("p");p.textContent="Источник "+row.source_ware_id+" / рейс "+row.source_tt_id+" · паллета "+row.pallet_identifier+" · "+row.article+" "+row.quantity+" "+row.base_uom+" · "+(row.temperature_decision==="HOLD"?"приостановлено по температуре":row.physically_loaded?"фактически погружено":row.onward_st_identifier?"СТ подготовлена, погрузка не подтверждена":row.placed_task_id?"размещено у ворот":row.receipt_operation_id?"принято, требуется размещение":row.unload_operation_id?"выгружено, требуется приёмка":"ожидается подвоз");return p;}));
 }catch(e){if(scope===key())say(e.message);}finally{busy=false;controls();}});
 el("iwThermalSave").addEventListener''',1)
p.write_text(s,encoding="utf-8")
