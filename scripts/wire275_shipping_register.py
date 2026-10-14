from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/finance/contracts_day_reviews.py");s=p.read_text(encoding="utf-8").replace("class DayReviewsPort(Protocol):","class DayReviewsPort(Protocol):\n    def shipping_register(self,ware: int,day: date,after: int,limit: int,actor: str) -> dict: ...");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py");s=p.read_text(encoding="utf-8");pos=s.index("    def history(")
s=s[:pos]+"""    def shipping_register(self,ware: int,day: date,after: int,limit: int,actor: str) -> dict:
        from .shipping_register import report
        return report(self.gateway,ware,day,after,limit,actor)

"""+s[pos:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/finance/api/day_review_routes.py");s=p.read_text(encoding="utf-8")
s+="""

@router.get("/warehouses/{ware_id}/shipping-register")
def shipping_register(ware_id: int,business_date: date,after_id: int=Query(default=0,ge=0),limit: int=Query(default=20,ge=1,le=50),
                      user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                      service: DayReviewsPort=Depends(day_reviews_service)) -> dict:
    try:return service.shipping_register(ware_id,business_date,after_id,limit,user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc
""";out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
