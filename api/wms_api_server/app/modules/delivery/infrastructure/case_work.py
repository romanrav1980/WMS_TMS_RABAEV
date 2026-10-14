from collections.abc import Callable
from typing import Any
from ..contracts import StoreReceiptError
from .store_cases import StoreCases


class CaseWork:
    def __init__(self,gateway: Any,post: Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]) -> None:
        self.gateway=gateway
        self.post=post

    def command(self,operation_id: str,case_id: str,metadata: dict[str,Any],actor: str) -> dict[str,Any]:
        return self.post("STORE_CASE_WORK",operation_id,{"case_id":case_id},metadata,actor)

    def assigned(self,actor: str) -> list[dict[str,Any]]:
        rows=self.gateway.fetch_all("""
            select CASE_ID,STORE_ADDR,STATUS,CASE_VERSION,EXPEDITION_USER,SECURITY_USER,SEARCH_DEADLINE,REASON_TEXT
              from RRL_STORE_DISCREPANCY_CASE where STATUS='ASSIGNED' and(EXPEDITION_USER=:actor or SECURITY_USER=:actor)
             order by SEARCH_DEADLINE,CASE_ID fetch first 101 rows only
        """,{"actor":actor})
        if len(rows)>100:
            raise StoreReceiptError("CASE_PERSONAL_QUEUE_BOUND_100","Назначено больше 100 открытых разбирательств: нужен отдельный диапазон")
        return rows

    def investigation(self,case_id: str,actor: str) -> dict[str,Any]:
        rows=self.gateway.fetch_all("select CASE_ID from RRL_STORE_DISCREPANCY_CASE where CASE_ID=:case_id and(EXPEDITION_USER=:actor or SECURITY_USER=:actor)",
                                    {"case_id":case_id,"actor":actor})
        if not rows:
            raise StoreReceiptError("CASE_ASSIGNED_INVESTIGATOR_ONLY","Разбирательство не назначено этому пользователю",403)
        return StoreCases(self.gateway).detail(case_id)

    def review(self,case_id: str,actor: str) -> dict[str,Any]:
        rows=self.gateway.fetch_all("select count(*) ALLOWED from RRL_STORE_DISCREPANCY_CASE c join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=c.LOAD_OPERATION_ID join RUSERS u on u.ID=:actor and nvl(u.DELETED,0)=0 and(u.WARE_ID=l.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')where c.CASE_ID=:case_id",{"actor":actor,"case_id":case_id})
        if rows[0]["allowed"]!=1:raise StoreReceiptError("CASE_CURRENT_WAREHOUSE_REVIEW_REQUIRED","Нет полномочий на разбирательство этого склада",403)
        return StoreCases(self.gateway).detail(case_id)
