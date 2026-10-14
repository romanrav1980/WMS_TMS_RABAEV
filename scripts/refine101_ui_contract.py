from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py");s=p.read_text(encoding="utf-8-sig").replace("    def availability(","    def catalog(self,actor: str) -> dict[str,Any]: ...\n    def availability(");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py");s=p.read_text(encoding="utf-8-sig")
needle="    def availability("
s=s.replace(needle,'''
    def catalog(self,actor: str) -> dict[str,Any]:
        warehouses=self.gateway.fetch_all("""
            select w.ID,w.NAME from RRL_WARES w where exists(
              select 1 from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0
               and(upper(trim(u.USER_GROUP))='GLOBAL_ADMIN' or u.WARE_ID=w.ID or RRL_HAS_WRIGHT(u.ID,'tare_manage')=1))
            order by w.NAME,w.ID fetch first 200 rows only
        """,{"actor":actor})
        types=self.gateway.fetch_all("select PALLET_TYPE_ID,PALLET_TYPE_NAME from RRL_PALLET_TYPE where ACTIVE=1 order by PALLET_TYPE_NAME fetch first 100 rows only")
        return {"warehouses":warehouses,"types":types}

'''+needle,1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py");s=p.read_text(encoding="utf-8-sig")
s=s.replace('    pallet_type_id: int|None=', '    expected_warehouse_id: int|None=Field(default=None,strict=True,ge=1)\n    pallet_type_id: int|None=',1)
s=s.replace('return command(service,"TARE_BOOK",body.operation_id,{"place_kind":body.place_kind,"place_id":body.place_id},{"pallet_type_id":body.pallet_type_id},user)',
'''metadata={"pallet_type_id":body.pallet_type_id}
    if body.expected_warehouse_id is not None:metadata["expected_warehouse_id"]=body.expected_warehouse_id
    return command(service,"TARE_BOOK",body.operation_id,{"place_kind":body.place_kind,"place_id":body.place_id},metadata,user)''',1)
s+='''
@router.get("/assembly/catalog")
def catalog(user: AdminUser=Depends(require_permission("tare_view")),service: TareAssemblyPort=Depends(tare_assembly_service)) -> dict[str,Any]:
    return service.catalog(user.username)
''';out[str(p)]=s
p=Path("db/migrations/2026-10-10_ni063_tare_assembly/003_command.sql");s=p.read_text(encoding="utf-8-sig")
s=s.replace(" RRL_TARE_PARTICIPANT.warehouse_actor(p_actor,v_ware);"," if m.has('expected_warehouse_id') and(m.get_number('expected_warehouse_id') is null or m.get_number('expected_warehouse_id')!=v_ware)then raise_application_error(-20886,'TARE_PLACE_SELECTED_WAREHOUSE_CONFLICT');end if;\n RRL_TARE_PARTICIPANT.warehouse_actor(p_actor,v_ware);",1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
