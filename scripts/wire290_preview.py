from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/store_returns.py");s=p.read_text(encoding="utf-8")
s+='''

    def reuse_preview(self,receipt_id: str,line_no: int,quantity: str,actor: str) -> dict[str,Any]:
        import oracledb
        try:
            with self.gateway.transaction("Current return reuse source READ ONLY")as q:
                q.execute("set transaction read only");out=q.var(oracledb.DB_TYPE_CLOB)
                q.callproc("RRL_RETURN_REUSE_API.preview",[receipt_id,line_no,quantity,actor,out])
                return read_oracle_json(out.getvalue())
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            raise StoreReceiptError("RETURN_REUSE_PREVIEW_REFUSED",str(exc.args[0]).split("\\n",1)[0],403 if code==20882 else 409 if 20800<=code<=20999 else 503)from exc
'''
out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/delivery/contracts_returns.py");s=p.read_text(encoding="utf-8").replace("class StoreReturnsPort(Protocol):","class StoreReturnsPort(Protocol):\n    def reuse_preview(self,receipt_id: str,line_no: int,quantity: str,actor: str) -> dict[str,Any]: ...");out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/delivery/api/store_return_routes.py");s=p.read_text(encoding="utf-8").replace("APIRouter,Depends,HTTPException","APIRouter,Depends,HTTPException,Query")
s+='''

@router.get("/{receipt_id}/reuse-preview")
def reuse_preview(receipt_id: str,line_no: int=Query(ge=1,le=200),
                  quantity: str=Query(pattern=r"^[0-9]{1,18}(\\.[0-9]{1,9})?$"),
                  user: AdminUser=Depends(require_permission("store_return_approve")),
                  service: StoreReturnsPort=Depends(store_returns_service)) -> dict[str,Any]:
    if not 1<=len(receipt_id)<=100:raise HTTPException(422,"Укажите исходную приёмку")
    try:return service.reuse_preview(receipt_id,line_no,quantity,user.username)
    except StoreReceiptError as exc:raise failure(exc)from exc
'''
out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/store-returns.js");s=p.read_text(encoding="utf-8")
needle=' const say=text=>{el("returnMessage").textContent=text;};'
assert needle in s
s=s.replace(needle,needle+'''
 const reusePanel=document.createElement("section"),reuseButton=document.createElement("button"),reuseMessage=document.createElement("p");
 reuseButton.type="button";reuseButton.textContent="Проверить исходную партию и полные коробки";
 reusePanel.append(reuseButton,reuseMessage);unitPanel.after(reusePanel);
 const reuseReasons={RETURN_REUSE_ORIGINAL_VERIFIED_BATCH_GOOD_BOX_REQUIRED:"Исходная партия не подтверждена приёмкой SAP",
 RETURN_REUSE_FULL_BOX_BASE_QUANTITY_CONFLICT:"Количество не соответствует полным коробкам текущей упаковки",
 RETURN_REUSE_SOURCE_EXPIRY_ARTICLE_REQUIRED:"Исходный срок годности истёк или данные партии неполны",
 RETURN_REUSE_CURRENT_SOURCE_BOX_UOM_REQUIRED:"Нет согласованной упаковки коробки"};
 async function previewReuse(){
  if(!dossier||busy||pending)return;
  const token=serial,scope=key(),receipt=dossier.source.operation_id;
  const line=Number(el("returnLine").value),quantity=el("returnQuantity").value.trim();
  if(!/^[0-9]{1,18}(\\.[0-9]{1,9})?$/.test(quantity)){reuseMessage.textContent="Укажите точное количество.";return;}
  busy=true;controls();reuseMessage.textContent="";
  try{
   const q=new URLSearchParams({line_no:String(line),quantity});
   const v=await request("/api/delivery/store-returns/"+encodeURIComponent(receipt)+"/reuse-preview?"+q);
   if(token!==serial||scope!==key())return;
   reuseMessage.textContent=v.source_eligible
    ? "Исходная партия и упаковка подходят. "+(v.currently_approvable?"Количество доступно для согласования.":"Этого количества уже нет в доступном остатке согласования.")
      +" Комплектность и коды единиц проверяются отдельно при передаче и приёмке."
    : (reuseReasons[v.source_reason]||"Исходные данные не допускают повторное использование.");
  }catch(e){if(token===serial&&scope===key())reuseMessage.textContent=e.message;}
  finally{if(token===serial&&scope===key()){busy=false;controls();}}
 }
 reuseButton.addEventListener("click",previewReuse);
 for(const id of ["returnLine","returnQuantity","returnDisposition"])el(id)?.addEventListener("change",()=>{reuseMessage.textContent="";});
''')
s=s.replace('++serial;dossier=null;pending=null;unitPanel.replaceChildren();','++serial;busy=false;dossier=null;pending=null;unitPanel.replaceChildren();reuseMessage.textContent="";')
out[p.as_posix()]=s
p=Path("db/migrations/2026-10-11_ni062_reuse_approval/003_recompile.sql");out[p.as_posix()]=p.read_text(encoding="utf-8")+"alter package RRL_STOCK_STORE_RETURN_CMD compile body;\nalter package RRL_RETURN_REUSE_API compile body;\n"
print(json.dumps(out,ensure_ascii=True))
