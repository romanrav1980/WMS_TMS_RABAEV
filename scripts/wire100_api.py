from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/contracts_tare.py");s=p.read_text(encoding="utf-8-sig").replace("    def context(","    def damage_cases(self,ware_id: int,actor: str) -> list[dict[str,Any]]: ...\n    def context(");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/tare.py");s=p.read_text(encoding="utf-8-sig")+'''
    def damage_cases(self,ware_id: int,actor: str) -> list[dict[str,Any]]:
        return self.gateway.fetch_all("""
            select r.OPERATION_ID,r.OWNER_WARE_ID,r.PALLET_TYPE_ID,t.PALLET_TYPE_NAME,
                   r.CUSTODIAN_KIND,r.CUSTODIAN_ID,r.DELIVERY_ACCEPT_OPERATION_ID,
                   to_char(r.QUANTITY,'TM9') DAMAGED_QUANTITY,
                   to_char(nvl(w.QTY,0),'TM9') WRITTEN_OFF_QUANTITY,
                   r.REASON_TEXT,r.DECISION_REFERENCE,r.ACTOR,r.CREATED_AT
              from RRL_TARE_RESOLUTION r join RRL_PALLET_TYPE t on t.PALLET_TYPE_ID=r.PALLET_TYPE_ID
              left join(select DAMAGE_OPERATION_ID,sum(QUANTITY) QTY from RRL_TARE_RESOLUTION where RESOLUTION_KIND='WRITE_OFF' group by DAMAGE_OPERATION_ID)w on w.DAMAGE_OPERATION_ID=r.OPERATION_ID
             where r.OWNER_WARE_ID=:ware and r.RESOLUTION_KIND='DAMAGE' and(
                RRL_HAS_WRIGHT(:actor,'tare_writeoff')=1
                or exists(select 1 from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0 and(upper(trim(u.USER_GROUP))='GLOBAL_ADMIN' or u.WARE_ID=r.OWNER_WARE_ID))
                or(r.CUSTODIAN_KIND='STORE' and exists(select 1 from RRL_STORE_RECEIPT_USER su where su.USER_ID=:actor and su.STORE_ADDR=r.CUSTODIAN_ID))
                or(r.CUSTODIAN_KIND='VEHICLE' and exists(select 1 from RRL_TRANSPORT_DRIVER_USER b join RRL_TRANSPORT_TASK tt on tt.VODITEL_ID=b.DRIVER_ID
                  join RRL_TR_VEHICLE veh on veh.NUM=tt.TRANSPORT where b.USER_ID=:actor and b.ACTIVE=1 and to_char(veh.ID,'TM9')=r.CUSTODIAN_ID)))
             order by r.CREATED_AT desc,r.OPERATION_ID desc fetch first 200 rows only
        """,{"ware":ware_id,"actor":actor})
''';out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8-sig")+"\nfrom .api.tare_resolution_routes import router as tare_resolution_router\n";out[str(p)]=s
p=Path("api/wms_api_server/app/main.py");s=p.read_text(encoding="utf-8-sig")+"\nfrom .modules.inventory.public import tare_resolution_router\napp.include_router(tare_resolution_router)\n";out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_stock.py");s=p.read_text(encoding="utf-8-sig").replace('{"TARE_COUNT",','{"TARE_DAMAGE", "TARE_WRITE_OFF", "TARE_COUNT",');out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/tare_policy.py");s=p.read_text(encoding="utf-8-sig").replace('d.TT_ID,d.ACCEPT_OPERATION_ID,','d.TT_ID,d.ACCEPT_OPERATION_ID,d.CLAIM_KEY,');out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
