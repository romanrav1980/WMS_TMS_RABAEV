from collections.abc import Callable
from typing import Any
from ..contracts import StoreReceiptError


class ReturnTransport:
    def __init__(self,gateway: Any,post: Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]) -> None:
        self.gateway=gateway
        self.post=post

    def plan(self,operation_id: str,approval_id: str,metadata: dict[str,Any],actor: str) -> dict[str,Any]:
        return self.post("STORE_RETURN_TRANSPORT_PLAN",operation_id,{"approval_operation_id":approval_id},metadata,actor)

    def eligible(self) -> list[dict[str,Any]]:
        return self.gateway.fetch_all("""
            select a.OPERATION_ID APPROVAL_ID,a.ARTICLE,a.LOT_UID,a.BASE_UOM,
                   to_char(a.BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QUANTITY,
                   a.DISPOSITION,a.RETURN_BASIS,f.STORE_ADDR,s.RETURN_DOCUMENT,s.WARE_ID,s.RECEIVE_CELL
              from RRL_STORE_RETURN_APPROVAL a join RRL_STORE_RETURN_SAP s on s.APPROVAL_OPERATION_ID=a.OPERATION_ID
              join RRL_STORE_RECEIPT_FACT f on f.OPERATION_ID=a.RECEIPT_OPERATION_ID
             where not exists(select 1 from RRL_STORE_RETURN_TRANSPORT t where t.APPROVAL_OPERATION_ID=a.OPERATION_ID)
             order by a.APPROVED_AT,a.OPERATION_ID fetch first 100 rows only
        """,{})

    def trip(self,task_id: int) -> list[dict[str,Any]]:
        rows=self.gateway.fetch_all("""
            select t.OPERATION_ID,t.APPROVAL_OPERATION_ID,a.RETURN_BASIS,t.TT_ID,t.VEHICLE_NUMBER,t.DRIVER_ID,t.STORE_ADDR,t.RECEIVING_WARE_ID,
                   to_char(t.GROSS_WEIGHT_KG,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') GROSS_WEIGHT_KG,
                   t.PHYSICAL_PLACES,t.CAPACITY_BASIS,t.PLANNED_BY,t.PLANNED_AT
              from RRL_STORE_RETURN_TRANSPORT t join RRL_STORE_RETURN_APPROVAL a on a.OPERATION_ID=t.APPROVAL_OPERATION_ID where t.TT_ID=:trip order by PLANNED_AT,OPERATION_ID fetch first 201 rows only
        """,{"trip":task_id})
        if len(rows)>200:
            raise StoreReceiptError("STORE_RETURN_TRIP_BOUND_200","Нужен отдельный диапазон возвратов рейса")
        return rows
