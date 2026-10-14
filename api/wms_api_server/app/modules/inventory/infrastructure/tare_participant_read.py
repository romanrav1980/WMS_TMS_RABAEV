"""Current holder signatures for the existing trip; warehouse admin never signs for a driver."""
from typing import Any


def participant_holders(gateway: Any,trip: int,actor: str)->dict[str,Any]:
    users=gateway.fetch_all("""
        select WARE_ID,case when upper(trim(USER_GROUP))='GLOBAL_ADMIN'then 1 else 0 end ALL_WAREHOUSES,
               RRL_HAS_WRIGHT(ID,'tare_offer') CAN_OFFER,RRL_HAS_WRIGHT(ID,'tare_accept') CAN_ACCEPT
          from RUSERS where ID=:actor and nvl(DELETED,0)=0
    """,{"actor":actor})
    if len(users)!=1:return {"warehouse_id":None,"all_warehouses":False,"trip_driver":False,"stores":[],"can_offer":False,"can_accept":False}
    driver=gateway.fetch_all("""
        select count(*) CNT from RRL_TRANSPORT_DRIVER_USER d join RRL_TRANSPORT_TASK t on t.VODITEL_ID=d.DRIVER_ID
         where t.ID=:trip and nvl(t.DELETED,0)=0 and d.USER_ID=:actor and d.ACTIVE=1
    """,{"trip":trip,"actor":actor})[0]
    stores=gateway.fetch_all("""
        select distinct s.STORE_ADDR from RRL_STORE_RECEIPT_USER s join RRL_SBORKA_PALLETS p on p.ADDR=s.STORE_ADDR
         where s.USER_ID=:actor and p.TRANSTASK_ID=:trip order by s.STORE_ADDR fetch first 201 rows only
    """,{"trip":trip,"actor":actor})
    user=users[0]
    return {"warehouse_id":user["ware_id"],"all_warehouses":bool(user["all_warehouses"]),
            "trip_driver":bool(driver["cnt"]),"stores":[r["store_addr"]for r in stores[:200]],
            "stores_has_more":len(stores)>200,"can_offer":bool(user["can_offer"]),"can_accept":bool(user["can_accept"])}
