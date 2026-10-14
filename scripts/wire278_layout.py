from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/preparation_readiness.py");s=p.read_text(encoding="utf-8")
s=s.replace("(select count(*)from RRL_ARTICULS z where z.ACTICUL=r.ARTICUL),r.UNIT_COUNT","(select count(*)from RRL_ARTICULS z where z.ACTICUL=r.ARTICUL),r.UNIT_COUNT,to_char(a.NORMA_UKLADKI,{_NUM})")
s=s.replace("rounded,count,unit_count=row","rounded,count,unit_count,norm=row")
s=s.replace('"pack_quantity":pack,"pack_mass":mass', '"pack_quantity":pack,"pallet_norm":norm,"pack_mass":mass')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py");s=p.read_text(encoding="utf-8")
s=s.replace("    def prepare(", "    def layout(self,order_id: int,counts: dict[str,int],actor: str) -> dict:\n        from .preparation_layout import preparation_layout\n        return preparation_layout(self.gateway,order_id,counts,actor)\n\n    def prepare(",1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/application/ports.py");s=p.read_text(encoding="utf-8").replace("class PreparationPort(Protocol):","class PreparationPort(Protocol):\n    def layout(self,order_id: int,counts: dict[str,int],actor: str) -> dict: ...");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/api/preparation_read_routes.py");s=p.read_text(encoding="utf-8")
s+="""
from pydantic import BaseModel,ConfigDict,Field
from typing import Annotated
class LayoutProposal(BaseModel):
    model_config=ConfigDict(extra="forbid")
    article_pallet_counts: dict[str,Annotated[int,Field(strict=True,ge=1,le=100)]]=Field(default_factory=dict,max_length=1000)

@router.post("/{order_id}/preparation-layout")
def layout(order_id: int,body: LayoutProposal,user: AdminUser=Depends(require_permission("customer_order_view")),
           service: PreparationPort=Depends(preparation_service)) -> dict:
    try:return service.layout(order_id,body.article_pallet_counts,user.username)
    except PermissionError as exc:raise HTTPException(403,str(exc))from exc
    except LookupError as exc:raise HTTPException(404,str(exc))from exc
    except ValueError as exc:raise HTTPException(409,str(exc))from exc
""";out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
