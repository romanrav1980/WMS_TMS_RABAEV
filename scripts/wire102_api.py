from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/api/tare_routes.py");s=p.read_text(encoding="utf-8-sig")
s=s.replace('    scan_vehicle: str=Field(strict=True,min_length=1,max_length=50)\n\n    @field_validator','    scan_vehicle: str=Field(strict=True,min_length=1,max_length=50)\n    booking_operation_ids: list[str]=Field(default_factory=list,max_length=100)\n\n    @field_validator',1)
s=s.replace('values=body.model_dump();operation=values.pop("operation_id");','values=body.model_dump();\n    if values.get("booking_operation_ids")==[]:values.pop("booking_operation_ids",None)\n    operation=values.pop("operation_id");',1)
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py");s=p.read_text(encoding="utf-8-sig").replace("    def catalog(","    def loaded_bookings(self,ware_id: int,task_id: int,actor: str) -> list[dict[str,Any]]: ...\n    def catalog(");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py");s=p.read_text(encoding="utf-8-sig")
needle="    def catalog("
s=s.replace(needle,'''
    def loaded_bookings(self,ware_id: int,task_id: int,actor: str) -> list[dict[str,Any]]:
        self._warehouse(ware_id,actor)
        return self.gateway.fetch_all("""
            select b.OPERATION_ID,b.PALLET_TYPE_ID,t.PALLET_TYPE_NAME,b.PLACE_KIND,b.PLACE_ID,
                   lf.LOAD_OPERATION_ID,lf.TT_ID,lf.VEHICLE_ID,lf.VEHICLE_NUMBER,lf.STATUS LOAD_STATUS
              from RRL_TARE_BOOK b join RRL_PALLET_TYPE t on t.PALLET_TYPE_ID=b.PALLET_TYPE_ID
              join RRL_TT_HU_LOAD_FACT lf on
                    (b.PLACE_KIND='HU' and lf.ROOT_UID=b.PLACE_ID)
                    or(b.PLACE_KIND='CASE' and to_char(lf.ROOT_CASE_TASK_ID,'TM9')=b.PLACE_ID)
             where b.OWNER_WARE_ID=:ware and b.STATUS='HELD' and lf.WARE_ID=:ware and lf.TT_ID=:task and lf.STATUS in('LOADED','DEPARTED')
             order by b.PALLET_TYPE_ID,b.PLACE_KIND,b.PLACE_ID fetch first 100 rows only
        """,{"ware":ware_id,"task":task_id})

'''+needle,1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py");s=p.read_text(encoding="utf-8-sig")+'''
@router.get("/warehouses/{ware_id}/trips/{task_id}/loaded-bookings")
def loaded_bookings(ware_id: int,task_id: int,user: AdminUser=Depends(require_permission("tare_view")),service: TareAssemblyPort=Depends(tare_assembly_service)) -> list[dict[str,Any]]:
    try:return service.loaded_bookings(ware_id,task_id,user.username)
    except TareError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
''';out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
