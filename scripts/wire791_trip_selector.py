from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/contracts_st_deferral.py");t=p.read_text(encoding="utf-8")
t="from datetime import date,datetime\n"+t
t=t.replace("    def history(", "    def candidates(self,st: str,actor: str,start: date|None,end: date|None,district: str|None,store: str|None,after_date: datetime|None,after_id: int,limit: int) -> dict: ...\n    def history(",1)
out[str(p)]=t
p=Path("api/wms_api_server/app/modules/transport/infrastructure/st_deferral.py");t=p.read_text(encoding="utf-8")
t="from datetime import date,datetime\n"+t
t=t.replace("    def context(",'''    def candidates(self,st: str,actor: str,start: date|None,end: date|None,district: str|None,store: str|None,after_date: datetime|None,after_id: int,limit: int) -> dict:
        from .trip_selector import candidates
        try:
            return candidates(self.gateway,st,actor,start,end,district,store,after_date,after_id,limit)
        except oracledb.DatabaseError as exc:
            raise trip_error(exc) from exc

    def context(''',1)
out[str(p)]=t
p=Path("api/wms_api_server/app/modules/transport/api/st_deferral_routes.py");t=p.read_text(encoding="utf-8")
t="from datetime import date,datetime\n"+t
t+='''
@router.get("/trip-candidates")
def trip_candidates(st_number: str=Query(min_length=1,max_length=100),
                    date_from: date|None=None,date_to: date|None=None,
                    district: str|None=Query(default=None,max_length=80),
                    store_code: str|None=Query(default=None,max_length=80),
                    after_date: datetime|None=None,after_trip_id: int=Query(default=0,ge=0),
                    limit: int=Query(default=50,ge=1,le=100),
                    user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                    service: StDeferralPort=Depends(st_deferral_service)) -> dict:
    try:
        return service.candidates(st_number,user.username,date_from,date_to,district,store_code,after_date,after_trip_id,limit)
    except TransportPlanError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
'''
out[str(p)]=t
print(json.dumps(out,ensure_ascii=True))
