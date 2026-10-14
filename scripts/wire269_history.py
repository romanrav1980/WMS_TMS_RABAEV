from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/finance/contracts_day_reviews.py");s=p.read_text(encoding="utf-8").replace("class DayReviewsPort(Protocol):","class DayReviewsPort(Protocol):\n    def history(self,ware: int,day: date,region: str,after: int,limit: int,actor: str) -> dict: ...\n    def get(self,operation: str,actor: str) -> dict: ...");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py");s=p.read_text(encoding="utf-8")
pos=s.index("    def context(")
s=s[:pos]+"""    def history(self,ware: int,day: date,region: str,after: int,limit: int,actor: str) -> dict:
        from .day_review_history import history
        return history(self.gateway,ware,day,region,after,limit,actor)

    def get(self,operation: str,actor: str) -> dict:
        from .day_review_history import detail
        return detail(self.gateway,operation,actor)

"""+s[pos:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/finance/api/day_review_routes.py");s=p.read_text(encoding="utf-8")
s+="""

@router.get("/reviews/warehouses/{ware_id}/history")
def history(ware_id: int,business_date: date,timezone_region: str=Query(min_length=1,max_length=64),
            after_version: int=Query(default=0,ge=0),limit: int=Query(default=20,ge=1,le=50),
            user: AdminUser=Depends(require_permission("transport_dispatch_view")),
            service: DayReviewsPort=Depends(day_reviews_service)) -> dict:
    try:return service.history(ware_id,business_date,timezone_region,after_version,limit,user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc

@router.get("/reviews/{operation}")
def detail(operation: str,user: AdminUser=Depends(require_permission("transport_dispatch_view")),
           service: DayReviewsPort=Depends(day_reviews_service)) -> dict:
    try:return service.get(operation,user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
""";out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
