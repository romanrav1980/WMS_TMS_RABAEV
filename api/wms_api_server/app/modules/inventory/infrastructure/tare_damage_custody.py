"""Read active subsets of damaged assets; no inferred legacy provenance."""
from typing import Any


def damage_custody(gateway: Any,ware: int,actor: str)->dict[str,Any]:
    rows=gateway.fetch_all("""
        select p.DAMAGE_OPERATION_ID,rawtohex(p.BALANCE_KEY) BALANCE_KEY,
               b.OWNER_WARE_ID,b.PALLET_TYPE_ID,t.PALLET_TYPE_NAME,b.CUSTODIAN_KIND,b.CUSTODIAN_ID,
               to_char(p.QUANTITY,'TM9') TRACKED_QUANTITY,
               to_char(b.QUANTITY,'TM9') PHYSICAL_QUANTITY,
               p.VERSION_NO,p.LAST_OPERATION_ID,r.ACTOR DAMAGE_ACTOR,r.DECISION_REFERENCE DAMAGE_REFERENCE
          from RRL_TARE_DAMAGE_POSITION p join RRL_TARE_BALANCE b on b.BALANCE_KEY=p.BALANCE_KEY
          join RRL_TARE_RESOLUTION r on r.OPERATION_ID=p.DAMAGE_OPERATION_ID
          join RRL_PALLET_TYPE t on t.PALLET_TYPE_ID=b.PALLET_TYPE_ID
         where b.OWNER_WARE_ID=:ware and p.QUANTITY>0 and exists(
          select 1 from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0 and(
           upper(trim(u.USER_GROUP))='GLOBAL_ADMIN' or u.WARE_ID=b.OWNER_WARE_ID
           or(b.CUSTODIAN_KIND='STORE'and exists(select 1 from RRL_STORE_RECEIPT_USER su where su.USER_ID=u.ID and su.STORE_ADDR=b.CUSTODIAN_ID))
           or(b.CUSTODIAN_KIND='VEHICLE'and exists(
            select 1 from RRL_TRANSPORT_DRIVER_USER du join RRL_TRANSPORT_TASK tt on tt.VODITEL_ID=du.DRIVER_ID
            join RRL_TR_VEHICLE v on v.NUM=tt.TRANSPORT where du.USER_ID=u.ID and du.ACTIVE=1
            and nvl(tt.DELETED,0)=0 and nvl(v.DELETED,0)=0 and to_char(v.ID,'TM9')=b.CUSTODIAN_ID))))
         order by p.DAMAGE_OPERATION_ID,p.BALANCE_KEY fetch first 201 rows only
    """,{"ware":ware,"actor":actor})
    return {"warehouse_id":ware,"items":rows[:200],"has_more":len(rows)>200,
            "scope":"CURRENT_AUTHORIZED_CUSTODY","legacy_provenance_inferred":False}
