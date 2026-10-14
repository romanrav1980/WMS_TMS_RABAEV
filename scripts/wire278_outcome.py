from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py");s=p.read_text(encoding="utf-8")
at=s.index("    def prepare(")
s=s[:at]+"""    def resolve(self,order_id: int,payload: dict,actor: str) -> dict:
        digest=sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
        # Wait on exactly the same source locks as preparation before declaring absence.
        with source_transaction(self.gateway,"Resolve original ST preparation outcome",actor,"customer_order_import",order=order_id)as cur:
            cur.execute("select s.PREPARATION_HASH,s.PREPARATION_JSON,c.WARE_ID from RRL_SAP_STORE_ORDER s join RRL_CUSTOMER_ORDER c on c.CUSTOMER_ORDER_ID=s.CUSTOMER_ORDER_ID where s.CUSTOMER_ORDER_ID=:order_id",order_id=order_id)
            row=cur.fetchone()
            if row is None:raise LookupError("SAP source order not found")
            assert_store_scope(cur,actor,"customer_order_import",row[2])
            if not row[0]:return {"state":"NOT_PREPARED","customer_order_id":order_id,"operation_id":payload["operation_id"],"stock_changed":False}
            if row[0]!=digest:raise StoreOrderConflict("Source was prepared by a different saved command; inspect its existing ST")
            return {"state":"ST_PREPARED","operation_id":payload["operation_id"],"result":read_oracle_json(row[1]),"stock_changed":False}

"""+s[at:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/application/ports.py");s=p.read_text(encoding="utf-8").replace("class PreparationPort(Protocol):","class PreparationPort(Protocol):\n    def resolve(self,order_id: int,payload: dict,actor: str) -> dict: ...");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py");s=p.read_text(encoding="utf-8")
s+="""
@router.post('/{order_id}/prepare-st/resolve')
def resolve_preparation(order_id: int,body: PreparationRequest,user: AdminUser=Depends(require_permission('customer_order_import')),
                        service: PreparationPort=Depends(preparation_service)) -> dict:
    if sum(len(p.lines)for p in body.pallets)>10000:raise HTTPException(422,'At most 10000 planned rows')
    try:return service.resolve(order_id,body.model_dump(mode='json'),user.username)
    except PermissionError as exc:raise HTTPException(403,str(exc))from exc
    except LookupError as exc:raise HTTPException(404,str(exc))from exc
    except StoreOrderConflict as exc:raise HTTPException(409,str(exc))from exc
""";out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/sap-preparation-layout.js");s=p.read_text(encoding="utf-8")
s=s.replace("el('splRetry').disabled=busy||!p;","el('splRetry').disabled=busy||!p;el('splResolve').disabled=busy||!p;")
s=s.replace(" async function send(){"," async function send(resolve=false){")
s=s.replace("if(!proposal)throw", "if(resolve||!proposal)throw",1)
s=s.replace("command.order_id+'/prepare-st',","command.order_id+'/prepare-st'+(resolve?'/resolve':''),")
s=s.replace("   if(v.customer_order_id!==command.order_id", """   if(resolve&&v.state==='NOT_PREPARED'){
    localStorage.removeItem(key());proposal=null;el('splMessage').textContent='После ожидания исходной команды сервер подтвердил: СТ не подготовлена. Перечитайте предложение перед новым решением.';return;
   }
   const result=resolve?v.result:v;
   if(result.customer_order_id!==command.order_id""")
s=s.replace("||v.status!=='ST_PREPARED'", "||result.status!=='ST_PREPARED'")
s=s.replace("+v.st_number+", "+result.st_number+").replace("+v.pallet_identifiers.length+", "+result.pallet_identifiers.length+")
s=s.replace("el('splRetry').addEventListener('click',send);","el('splRetry').addEventListener('click',()=>send());el('splResolve').addEventListener('click',()=>send(true));")
s=s.replace("el('splSave').addEventListener('click',send);","el('splSave').addEventListener('click',()=>send());")
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8").replace('<p id="splPending"', '<button id="splResolve" disabled>Проверить исход сохранённой команды</button><p id="splPending"',1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
