import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py")
s=p.read_text(encoding="utf-8").replace("APIRouter, Depends, Path","APIRouter, Depends, Path, Query, HTTPException, Response")
s=s.replace("from .task_scan_routes import UnitScan","from .task_scan_routes import UnitScan\nfrom ..domain.quality_label import quality_label_html")
anchor='@router.post("/{identifier}/scan")'
assert anchor in s
s=s.replace(anchor,'''@router.get("/{identifier}/control-label")
def control_label(identifier: str = Path(min_length=1,max_length=150),
                  expected_signature: str|None = Query(default=None,pattern=r"^[A-F0-9]{64}$"),
                  user: AdminUser = Depends(require_permission("outgoing_pallet_check")),
                  service: QualityPort = Depends(outgoing_quality_service)) -> Response:
    snapshot=service.status(identifier,user.username)
    if expected_signature is not None and snapshot.get("composition_signature")!=expected_signature:
        raise HTTPException(409,"Состав изменился. Перечитайте результат контроля перед печатью.")
    return Response(quality_label_html(snapshot,user.username),media_type="text/html",
                    headers={"Cache-Control":"no-store","X-Content-Type-Options":"nosniff"})


'''+anchor)
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/outgoing-quality.js");s=p.read_text(encoding="utf-8")
s=s.replace('<button data-load>Предъявить к контролю</button>','<button data-load>Предъявить к контролю</button><button data-print-label>Этикетка допуска / красный тег</button>')
anchor=' function freeze(identifier,kind,body){'
assert anchor in s
s=s.replace(anchor,''' el("print-label").onclick=async()=>{
  const id=snapshot?.shipment_identifier,signature=snapshot?.composition_signature,scope=key(),stamp=generation;
  if(busy||pending||!id||el("id").value.trim()!==id){message.textContent="Перечитайте текущий результат контроля.";return;}
  const popup=window.open("about:blank","_blank");if(!popup){message.textContent="Разрешите открытие окна печати.";return;}
  try{
   const response=await fetch(base()+path(id)+"/control-label"+(signature?"?expected_signature="+encodeURIComponent(signature):""),{headers:window.wmsAdminAuth.headers(),cache:"no-store"});
   if(!response.ok){const data=await response.json();throw Error(typeof data.detail==="string"?data.detail:"Этикетка не сформирована");}
   const html=await response.text();
   if(scope!==key()||stamp!==generation||snapshot?.shipment_identifier!==id||snapshot?.composition_signature!==signature||el("id").value.trim()!==id){popup.close();return;}
   if(!popup.closed){popup.document.open();popup.document.write(html);popup.document.close();}
  }catch(error){popup.close();if(scope===key()&&stamp===generation)message.textContent=error.message;}
 };
'''+anchor)
out[str(p)]=s
print(json.dumps(out))
