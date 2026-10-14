from collections.abc import Callable
from typing import Any
import oracledb
from ..contracts import StoreReceiptError


class ReturnCustody:
    def __init__(self,gateway: Any,post: Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]) -> None:
        self.gateway=gateway
        self.post=post

    def handover(self,operation_id: str,transport_id: str,metadata: dict[str,Any],actor: str) -> dict[str,Any]:
        return self.post("STORE_RETURN_HANDOVER",operation_id,{"transport_operation_id":transport_id},metadata,actor)

    def pickup(self,operation_id: str,handover_id: str,metadata: dict[str,Any],actor: str) -> dict[str,Any]:
        return self.post("STORE_RETURN_PICKUP",operation_id,{"handover_operation_id":handover_id},metadata,actor)

    def store_pending(self,store_address: str,actor: str,task_id: int | None=None) -> list[dict[str,Any]]:
        try:
            with self.gateway.transaction("Store return source authorization") as cursor:
                cursor.execute("begin RRL_STOCK_STORE_RECEIPT_READ.require_receiver(:actor,:store);end;",{"actor":actor,"store":store_address})
        except oracledb.DatabaseError as exc:
            if getattr(exc.args[0],"code",0)==20882:
                raise StoreReceiptError("STORE_RETURN_STORE_FORBIDDEN","Магазин не назначен пользователю",403) from exc
            raise
        return self.gateway.fetch_all("""
            select t.OPERATION_ID TRANSPORT_OPERATION_ID,t.TT_ID,t.VEHICLE_NUMBER,t.DRIVER_ID,t.STORE_ADDR,t.RECEIVING_WARE_ID,
                   to_char(t.GROSS_WEIGHT_KG,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PLANNED_GROSS_WEIGHT_KG,t.PHYSICAL_PLACES,
                   a.ARTICLE,a.LOT_UID,a.BASE_UOM,to_char(a.BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QUANTITY
              from RRL_STORE_RETURN_TRANSPORT t join RRL_STORE_RETURN_APPROVAL a on a.OPERATION_ID=t.APPROVAL_OPERATION_ID
             where t.STORE_ADDR=:store and(:trip is null or t.TT_ID=:trip) and not exists(select 1 from RRL_STORE_RETURN_HANDOVER h where h.TRANSPORT_OPERATION_ID=t.OPERATION_ID)
             order by t.PLANNED_AT,t.OPERATION_ID fetch first 100 rows only
        """,{"store":store_address,"trip":task_id})

    def driver_pending(self,actor: str,task_id: int | None=None) -> list[dict[str,Any]]:
        return self.gateway.fetch_all("""
            select h.OPERATION_ID HANDOVER_OPERATION_ID,h.PALLET_IDENTIFIER,t.TT_ID,t.VEHICLE_NUMBER,t.STORE_ADDR,t.RECEIVING_WARE_ID,
                   to_char(h.GROSS_WEIGHT_KG,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') GROSS_WEIGHT_KG,h.PHYSICAL_PLACES,h.HANDED_BY
              from RRL_STORE_RETURN_HANDOVER h join RRL_STORE_RETURN_TRANSPORT t on t.OPERATION_ID=h.TRANSPORT_OPERATION_ID
              join RRL_TRANSPORT_DRIVER_USER b on b.DRIVER_ID=t.DRIVER_ID and b.ACTIVE=1 and b.USER_ID=:actor
              join RRL_TRANSPORT_TASK tt on tt.ID=t.TT_ID and tt.VODITEL_ID=t.DRIVER_ID and tt.TRANSPORT=t.VEHICLE_NUMBER and nvl(tt.DELETED,0)=0
             where (:trip is null or t.TT_ID=:trip) and not exists(select 1 from RRL_STORE_RETURN_PICKUP p where p.HANDOVER_OPERATION_ID=h.OPERATION_ID)
             order by h.HANDED_AT,h.OPERATION_ID fetch first 100 rows only
        """,{"actor":actor,"trip":task_id})
