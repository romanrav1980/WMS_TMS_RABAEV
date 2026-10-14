from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/tare.py")
s=p.read_text(encoding="utf-8-sig")+'''
    def context(self,task_id: int,actor: str) -> dict[str,Any]:
        trips=self.gateway.fetch_all("""
            select tt.ID TASK_ID,veh.ID VEHICLE_ID,veh.NUM VEHICLE_NUMBER
              from RRL_TRANSPORT_TASK tt join RRL_TR_VEHICLE veh on veh.NUM=tt.TRANSPORT
             where tt.ID=:task and nvl(tt.DELETED,0)=0 and nvl(veh.DELETED,0)=0 and(
               exists(select 1 from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0 and(upper(trim(u.USER_GROUP))='GLOBAL_ADMIN' or u.WARE_ID is not null))
               or exists(select 1 from RRL_TRANSPORT_DRIVER_USER b where b.DRIVER_ID=tt.VODITEL_ID and b.USER_ID=:actor and b.ACTIVE=1)
               or exists(select 1 from RRL_STORE_RECEIPT_USER su join RRL_SBORKA_PALLETS st on st.ADDR=su.STORE_ADDR where st.TRANSTASK_ID=tt.ID and su.USER_ID=:actor))
        """,{"task":task_id,"actor":actor})
        if len(trips)!=1:raise TareError("TARE_TRIP_CONTEXT_FORBIDDEN","Рейс не назначен пользователю или машина неоднозначна",403)
        warehouses=self.gateway.fetch_all("select ID,NAME from RRL_WARES order by NAME,ID fetch first 200 rows only")
        types=self.gateway.fetch_all("select PALLET_TYPE_ID,PALLET_TYPE_NAME,PALLET_TYPE_CODE from RRL_PALLET_TYPE where ACTIVE=1 order by PALLET_TYPE_NAME fetch first 100 rows only")
        stores=self.gateway.fetch_all("select distinct ADDR from RRL_SBORKA_PALLETS where TRANSTASK_ID=:task and ADDR is not null order by ADDR fetch first 200 rows only",{"task":task_id})
        return {"trip":trips[0],"warehouses":warehouses,"types":types,"stores":[r["addr"] for r in stores]}
'''
p2=Path("api/wms_api_server/app/modules/inventory/contracts_tare.py")
s2=p2.read_text(encoding="utf-8-sig").replace("    def offers(","    def context(self,task_id: int,actor: str) -> dict[str,Any]: ...\n    def offers(")
p3=Path("api/wms_api_server/app/modules/inventory/api/tare_routes.py")
s3=p3.read_text(encoding="utf-8-sig")+'''
@router.get("/trips/{task_id}/context")
def context(task_id: int,user: AdminUser=Depends(require_permission("tare_view")),service: TarePort=Depends(tare_service)) -> dict[str,Any]:
    try:return service.context(task_id,user.username)
    except TareError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
'''
print(json.dumps({str(p):s,str(p2):s2,str(p3):s3},ensure_ascii=True))
