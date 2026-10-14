from collections.abc import Callable
from typing import Any
from ..contracts_tare import TareError

class Tare:
    def __init__(self,gateway: Any,post: Callable[...,dict[str,Any]]) -> None:
        self.gateway,self.poster=gateway,post

    def post(self,kind: str,operation_id: str,source: dict[str,Any],metadata: dict[str,Any],actor: str) -> dict[str,Any]:
        return self.poster(kind,operation_id,source,metadata,actor)

    def balances(self,owner_ware_id: int,actor: str) -> list[dict[str,Any]]:
        return self.gateway.fetch_all("""
            select b.OWNER_WARE_ID,b.PALLET_TYPE_ID,t.PALLET_TYPE_CODE,t.PALLET_TYPE_NAME,
                   b.CONDITION_CODE,b.CUSTODIAN_KIND,b.CUSTODIAN_ID,
                   to_char(b.QUANTITY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QUANTITY,
                   b.BALANCE_VERSION,b.UPDATED_AT,b.LAST_OPERATION_ID
              from RRL_TARE_BALANCE b join RRL_PALLET_TYPE t on t.PALLET_TYPE_ID=b.PALLET_TYPE_ID
             where b.OWNER_WARE_ID=:ware and (
               exists(select 1 from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0 and(upper(trim(u.USER_GROUP))='GLOBAL_ADMIN' or u.WARE_ID=b.OWNER_WARE_ID))
               or (b.CUSTODIAN_KIND='STORE' and exists(select 1 from RRL_STORE_RECEIPT_USER s where s.USER_ID=:actor and s.STORE_ADDR=b.CUSTODIAN_ID))
               or (b.CUSTODIAN_KIND='VEHICLE' and exists(select 1 from RRL_TRANSPORT_DRIVER_USER d join RRL_TRANSPORT_TASK tt on tt.VODITEL_ID=d.DRIVER_ID
                    join RRL_TR_VEHICLE veh on veh.NUM=tt.TRANSPORT
                    where d.USER_ID=:actor and d.ACTIVE=1 and nvl(tt.DELETED,0)=0 and to_char(veh.ID,'TM9')=b.CUSTODIAN_ID)))
             order by b.CUSTODIAN_KIND,b.CUSTODIAN_ID,b.PALLET_TYPE_ID,b.CONDITION_CODE fetch first 200 rows only
        """,{"ware":owner_ware_id,"actor":actor})

    def offers(self,task_id: int,actor: str) -> list[dict[str,Any]]:
        return self.gateway.fetch_all("""
            select o.OPERATION_ID,o.OWNER_WARE_ID,o.PALLET_TYPE_ID,o.CONDITION_CODE,
                   o.FROM_KIND,o.FROM_ID,o.TO_KIND,o.TO_ID,o.VEHICLE_NUMBER,
                   to_char(o.QUANTITY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QUANTITY,
                   o.OFFERED_BY,o.OFFERED_AT,a.OPERATION_ID ACCEPT_OPERATION_ID,
                   to_char(a.ACCEPTED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') ACCEPTED_QUANTITY,
                   to_char(a.SHORT_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') SHORT_QUANTITY,a.ACCEPTED_BY,a.ACCEPTED_AT
              from RRL_TARE_OFFER o left join RRL_TARE_ACCEPT a on a.OFFER_OPERATION_ID=o.OPERATION_ID
             where o.TT_ID=:task and(
                exists(select 1 from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0 and(upper(trim(u.USER_GROUP))='GLOBAL_ADMIN' or u.WARE_ID=o.OWNER_WARE_ID))
                or exists(select 1 from RRL_STORE_RECEIPT_USER s where s.USER_ID=:actor and s.STORE_ADDR=o.STORE_ADDR)
                or exists(select 1 from RRL_TRANSPORT_DRIVER_USER d join RRL_TRANSPORT_TASK tt on tt.VODITEL_ID=d.DRIVER_ID
                          where d.USER_ID=:actor and d.ACTIVE=1 and tt.ID=o.TT_ID and nvl(tt.DELETED,0)=0))
             order by o.OFFERED_AT desc,o.OPERATION_ID desc fetch first 100 rows only
        """,{"task":task_id,"actor":actor})

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
        customers=self.gateway.fetch_all("select CUSTOMER_ID,CUSTOMER_NAME from RRL_CUSTOMER where ACTIVE=1 order by CUSTOMER_NAME fetch first 200 rows only")
        permissions=self.gateway.fetch_all("select RRL_HAS_WRIGHT(:actor,'tare_damage') CAN_DAMAGE,RRL_HAS_WRIGHT(:actor,'tare_writeoff') CAN_WRITEOFF,RRL_HAS_WRIGHT(:actor,'tare_loss_report') CAN_LOSS_REPORT from dual",{"actor":actor})[0]
        return {"permissions":permissions,"customers":customers,"trip":trips[0],"warehouses":warehouses,"types":types,"stores":[r["addr"] for r in stores]}

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
