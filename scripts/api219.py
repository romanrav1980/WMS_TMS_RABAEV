from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/contracts_stock.py");s=p.read_text(encoding="utf-8");s=s.replace('"TARE_OFFER", "TARE_ACCEPT",','"TARE_OFFER", "TARE_ACCEPT", "TARE_OFFER_CANCEL",',1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/tare_routes.py");s=p.read_text(encoding="utf-8");anchor="class Accept(Operation):";assert anchor in s;s=s.replace(anchor,'''class OfferCancel(Operation):
    offer_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    scan_vehicle: str=Field(strict=True,min_length=1,max_length=50)
    reason: str=Field(strict=True,min_length=1,max_length=500)

'''+anchor,1);anchor='@router.get("/warehouses/{ware_id}/balances")';assert anchor in s;s=s.replace(anchor,'''@router.post("/offer-cancel")
def offer_cancel(body: OfferCancel,user: AdminUser=Depends(require_permission("tare_offer")),service: TarePort=Depends(tare_service)) -> dict[str,Any]:
    return post(service,body,"TARE_OFFER_CANCEL",("offer_operation_id",),user)

'''+anchor,1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/tare.py");s=p.read_text(encoding="utf-8");s=s.replace("a.ACCEPTED_BY,a.ACCEPTED_AT","a.ACCEPTED_BY,a.ACCEPTED_AT,c.OPERATION_ID CANCEL_OPERATION_ID,c.REASON CANCEL_REASON,c.CANCELLED_BY,c.CANCELLED_AT",1);s=s.replace("from RRL_TARE_OFFER o left join RRL_TARE_ACCEPT a on a.OFFER_OPERATION_ID=o.OPERATION_ID","from RRL_TARE_OFFER o left join RRL_TARE_ACCEPT a on a.OFFER_OPERATION_ID=o.OPERATION_ID\n              left join RRL_TARE_OFFER_CANCEL c on c.OFFER_OPERATION_ID=o.OPERATION_ID",1);out[str(p)]=s
for path in["api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py","api/wms_api_server/app/modules/finance/infrastructure/reconciliation_sources.py"]:
 p=Path(path);s=p.read_text(encoding="utf-8");anchor="not exists(select 1 from RRL_TARE_ACCEPT a where a.OFFER_OPERATION_ID=o.OPERATION_ID)";assert anchor in s;s=s.replace(anchor,anchor+" and not exists(select 1 from RRL_TARE_OFFER_CANCEL c where c.OFFER_OPERATION_ID=o.OPERATION_ID)",1);out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/tare-ledger.html");s=p.read_text(encoding="utf-8");anchor='<button id="tareRetry" hidden>';assert anchor in s;s=s.replace(anchor,'''<section class="panel" data-permission="tare_offer"><h2>Отмена непринятой передачи</h2><button id="tareCancelRefresh">Показать предложения и историю</button><div id="tareOfferHistory"></div><label>Непринятое предложение<select id="tareCancelOffer"></select></label><label>Скан машины<input id="tareCancelScan" autocomplete="off"></label><label>Причина отмены<input id="tareCancelReason" maxlength="500"></label><button id="tareCancel">Отменить предложение</button><p>Отмена не изменяет баланс. Принятую тару возвращают отдельной передачей.</p></section>'''+anchor,1);out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/tare-ledger.js");s=p.read_text(encoding="utf-8");s=s.replace('!row.accept_operation_id&&row.to_kind','!row.accept_operation_id&&!row.cancel_operation_id&&row.to_kind',1)
anchor=" async function send(scope)";idx=s.index(anchor);s=s[:idx]+''' async function cancelOffers(){await read(async current=>{
  const data=await request("/trips/"+number("tareTrip")+"/offers");if(!current())return;
  el("tareOfferHistory").replaceChildren(...data.map(row=>{const p=document.createElement("p");p.textContent=row.operation_id+" · "+row.quantity+" · "+(row.cancel_operation_id?"Отменено: "+row.cancel_reason:row.accept_operation_id?"Принято":"Ожидает приёмки");return p;}));
  const actor=auth().state.user?.username,admin=auth().hasPermission("*");
  el("tareCancelOffer").replaceChildren(new Option("Выберите предложение",""),...data.filter(row=>!row.accept_operation_id&&!row.cancel_operation_id&&(row.offered_by===actor||admin)).map(row=>new Option(row.operation_id+" · "+row.quantity,row.operation_id)));
 });}
 function cancelOffer(){return prepare("/offer-cancel",()=>{
  const offer=el("tareCancelOffer").value,scan=el("tareCancelScan").value.trim(),reason=el("tareCancelReason").value.trim();
  if(!offer||!scan||!reason)throw Error("Выберите предложение, отсканируйте машину и укажите причину.");
  return{offer_operation_id:offer,scan_vehicle:scan,reason};
 });}
'''+s[idx:]
s=s.replace('say(result.status==="POSTED"?','say(result.status==="CANCELLED"?"Отмена подтверждена. Баланс не изменён; обновите историю.":result.status==="POSTED"?',1)
anchor='window.addEventListener("wms-admin-auth-ready",';idx=s.index(anchor);s=s[:idx]+'el("tareCancelRefresh").onclick=cancelOffers;el("tareCancel").onclick=cancelOffer;'+s[idx:]
# Clear current cancellation options/history on auth change rather than expose previous scope.
anchor='context=null;rows=null;offers=[];';s=s.replace(anchor,anchor+'el("tareCancelOffer").replaceChildren();el("tareOfferHistory").replaceChildren();',1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
