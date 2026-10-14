from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py");s=p.read_text(encoding="utf-8-sig")
s=s.replace('    net_weight_kg: str=Field(strict=True,pattern=r"^[0-9]{1,18}(\\.[0-9]{1,9})?$")','''    net_weight_kg: str=Field(strict=True,pattern=r"^[0-9]{1,18}(\\.[0-9]{1,9})?$")
    full_box_count: str|None=Field(default=None,strict=True,pattern=r"^[1-9][0-9]{0,17}$")
    complete_good_boxes: bool=Field(default=False,strict=True)''',1)
s+='''

class ReuseZone(BaseModel):
    model_config=ConfigDict(extra="forbid")
    receive_cell: str=Field(strict=True,min_length=1,max_length=60)
    expected_version: int=Field(strict=True,ge=1)

@router.put("/warehouses/{ware_id}/reuse-receiving")
def reuse_zone(ware_id: int,body: ReuseZone,user: AdminUser=Depends(require_permission("warehouse_settings_edit")),service: StoreReturnReceivePort=Depends(store_return_receive_service)) -> dict[str,Any]:
    try:return service.configure_reuse(ware_id,body.receive_cell,body.expected_version,user.username)
    except StoreReturnReceiveError as exc:raise failure(exc) from exc
''';out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_store_returns.py");s=p.read_text(encoding="utf-8-sig").replace("    def policy(","    def configure_reuse(self,ware_id: int,receive_cell: str,expected_version: int,actor: str) -> dict[str,Any]: ...\n    def policy(",1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py");s=p.read_text(encoding="utf-8-sig").replace("SUPPLIER_TARGET_CELL,DISPOSAL_TARGET_CELL,POLICY_VERSION","SUPPLIER_TARGET_CELL,DISPOSAL_TARGET_CELL,REUSE_RECEIVE_CELL,POLICY_VERSION",1).replace("when 'DISPOSAL' then policy.DISPOSAL_RECEIVE_CELL end RECEIVE_CELL","when 'DISPOSAL' then policy.DISPOSAL_RECEIVE_CELL when 'REUSE' then policy.REUSE_RECEIVE_CELL end RECEIVE_CELL",1)
s=s.replace("    def policy(",'''    def configure_reuse(self,ware_id: int,receive_cell: str,expected_version: int,actor: str) -> dict[str,Any]:
        try:
            with stock_configuration_transaction(self.gateway,"Return good-box segregated receiving zone",actor,"warehouse_settings_edit") as cursor:
                cursor.execute("update RRL_STORE_RETURN_WARE_POLICY set REUSE_RECEIVE_CELL=:cell,POLICY_VERSION=POLICY_VERSION+1,CHANGED_BY=:actor,CHANGED_AT=systimestamp where WARE_ID=:ware and POLICY_VERSION=:version",{"ware":ware_id,"cell":receive_cell,"actor":actor,"version":expected_version})
                if cursor.rowcount!=1:raise StoreReturnReceiveError("RETURN_REUSE_POLICY_VERSION_CONFLICT","Покажите текущие настройки возврата")
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if 20800<=code<=20999:raise StoreReturnReceiveError("RETURN_REUSE_ZONE_REJECTED",str(exc.args[0]).split("\\n",1)[0],403 if code==20882 else 409) from exc
            raise
        return self.policy(ware_id)

    def policy(''',1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/return_putaway.py");s=p.read_text(encoding="utf-8-sig").replace("else policy.DISPOSAL_TARGET_CELL end CURRENT_TARGET_CELL","when 'DISPOSAL' then policy.DISPOSAL_TARGET_CELL when 'REUSE' then nvl(rule.PICK_CELL,card.CELL) end CURRENT_TARGET_CELL",1)
s=s.replace("from RRL_STORE_RETURN_RECEIPT r left join","from RRL_STORE_RETURN_RECEIPT r join RRL_ARTICULS card on card.ACTICUL=r.ARTICLE left join RRL_RECEIPT_SKU_RULE rule on rule.ARTICUL=r.ARTICLE and rule.WARE_ID=r.WARE_ID left join",1);out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/store-return-receiving.html");s=p.read_text(encoding="utf-8-sig").replace('<button id="receivePolicySave">','<label>Отдельная приёмка исправных полных коробок<input id="receiveReuseCell" maxlength="60"></label><button id="receiveReuseSave">Сохранить зону исправного возврата</button><button id="receivePolicySave">',1)
s=s.replace('<button id="receiveConfirm">','<label>Для исправного возврата: полных коробок<input id="receiveBoxes" inputmode="numeric"></label><label><input id="receiveGoodBoxes" type="checkbox">Подтверждаю исправность и полную комплектацию коробок</label><button id="receiveConfirm">',1);out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/store-return-receiving.js");s=p.read_text(encoding="utf-8-sig").replace('el("receiveSupplierCell").value=data.supplier_receive_cell||"";','el("receiveSupplierCell").value=data.supplier_receive_cell||"";el("receiveReuseCell").value=data.reuse_receive_cell||"";',1)
s=s.replace('function summary(){','function summary(){el("receiveBoxes").value="";el("receiveGoodBoxes").checked=false;',1)
# Preserve existing durable receipt submit; add fields only for REUSE.
needle='const body={'
# Inspectable narrow insertion before canonical operation creation using actual source below.
s=s.replace(' async function savePolicy(){',''' async function saveReuse(){if(busy||pending)return;if(!policy)return say("Покажите текущие настройки.");const scope=key(),seq=++serial;busy=true;controls();try{const data=await request("/warehouses/"+warehouse()+"/reuse-receiving",{receive_cell:el("receiveReuseCell").value,expected_version:policy.policy_version},"PUT");if(scope===key()&&seq===serial){policy=data;el("receivePolicyVersion").textContent="Версия "+data.policy_version;rows=[];el("receivePickup").replaceChildren();summary();say("Зона исправного возврата сохранена.");}}catch(e){if(scope===key()){policy=null;say(e.message);}}finally{busy=false;controls();}}
 async function savePolicy(){''',1)
s=s.replace('window.addEventListener("wms-admin-auth-ready",','el("receiveReuseSave").addEventListener("click",saveReuse);\n window.addEventListener("wms-admin-auth-ready",',1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
