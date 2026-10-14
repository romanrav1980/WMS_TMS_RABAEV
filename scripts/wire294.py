from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8");s+='\n    def shortage(self,receipt_id: str,actor: str) -> dict:\n        from .interwarehouse_shortage import read_shortage\n        return read_shortage(self.gateway,receipt_id,actor)\n';out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py");s=p.read_text(encoding="utf-8");s=s.replace("class InterwarehousePort(Protocol):","class InterwarehousePort(Protocol):\n    def shortage(self,receipt_id: str,actor: str) -> dict[str,Any]: ...",1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");s=p.read_text(encoding="utf-8");s+='''
@router.get("/receipts/{receipt_id}/shortage")
def shortage(receipt_id: str,user: AdminUser=Depends(require_permission("transport_dispatch_view")),
             service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    if len(receipt_id)>100:raise HTTPException(422,"receipt identifier bound")
    try:return service.shortage(receipt_id,user.username)
    except StoreReturnReceiveError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc
''';out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.html");s=p.read_text(encoding="utf-8")
panel='<section class="panel" data-permission="transport_dispatch_view"><h2>Сверка фактически недостающего товара</h2><label>Приёмка<select id="iwShortReceipt"></select></label><button id="iwShortLoad">Показать количество и исходные единицы</button><p id="iwShortSummary"></p><div id="iwShortUnits"></div><p>Недостача сохраняется отдельно от складского остатка. Это сверка фактов, а не акт утраты или квитанция государственной системы.</p></section>'
s=s.replace('<button id="iwRetry"',panel+'<button id="iwRetry"',1);out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
needle='decisionPlans=rows;'
assert needle in s;s=s.replace(needle,needle+'el("iwShortReceipt").replaceChildren(...rows.filter(r=>r.receipt_operation_id).map(r=>new Option((r.received_pallet_identifier||r.pallet_identifier)+" · принято "+r.received_quantity+" · недостача "+(r.short_quantity||"0"),r.receipt_operation_id)));',1)
s=s.replace('incidentCandidates=[];el("iwCloseIncident").replaceChildren();historyPlan="";','el("iwShortReceipt").replaceChildren();el("iwShortSummary").textContent="";el("iwShortUnits").replaceChildren();incidentCandidates=[];el("iwCloseIncident").replaceChildren();historyPlan="";')
handler=''' el("iwShortLoad").addEventListener("click",async()=>{if(busy||pending)return;const scope=key(),receipt=el("iwShortReceipt").value,seq=++serial;if(!receipt){say("Обновите планы и выберите приёмку.");return;}busy=true;controls();try{
 const r=await request("/receipts/"+encodeURIComponent(receipt)+"/shortage");if(scope!==key()||seq!==serial)return;
 el("iwShortSummary").textContent="Заявлено "+r.expected_quantity+" · принято "+r.accepted_quantity+" · недостача "+r.short_quantity+" "+r.base_uom+" · "+(r.carrier_custody_released?"Ответственность завершена":"Ответственность не завершена")+" · "+(r.discrepancy_reason||"");
 el("iwShortUnits").replaceChildren(...r.missing_units.map(u=>{const p=document.createElement("p");p.textContent="Единица "+u.unit_id+" · "+u.declared_quantity+" "+u.base_uom+" · "+u.current_stock_status+" · паллета "+u.current_pallet_identifier+" · кодов "+u.registered_code_count+(r.current_unit_state_conflicts.includes(u.key)?" · состояние изменилось, требуется расследование":"");return p;}));
 }catch(e){if(scope===key())say(e.message);}finally{busy=false;controls();}});
'''
s=s.replace(' el("iwLoad").addEventListener',handler+' el("iwLoad").addEventListener',1);out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
