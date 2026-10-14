"""Immutable Oracle receipt and existing authenticated/configuration boundaries."""
import json
from collections.abc import Callable
from typing import Any
import oracledb
from ...platform.public import stock_configuration_transaction
from ..contracts import StoreReceiptError
from .store_cases import StoreCases
from .store_receipt_read import read_store_preview


class StoreReceipt:
    def __init__(self, gateway: Any, post: Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]) -> None:
        self.gateway=gateway
        self.post=post

    def cases(self, address: str, after: str, limit: int) -> dict[str,Any]:
        return StoreCases(self.gateway).list(address,after,limit)

    def case_detail(self, case_id: str) -> dict[str,Any]:
        return StoreCases(self.gateway).detail(case_id)

    def preview(self, load_operation_id: str, store_address: str, actor: str) -> dict[str,Any]:
        return read_store_preview(self.gateway,load_operation_id,store_address,actor)

    def places(self, trip_id: int, store_address: str, actor: str) -> list[dict[str,Any]]:
        rows=self.gateway.fetch_all("""
            select lf.LOAD_OPERATION_ID,coalesce(lf.ROOT_UID,'CASE:'||to_char(lf.ROOT_CASE_TASK_ID)) ROOT_KEY,
                   lf.GROSS_WEIGHT_KG,lf.DEPARTED_AT,receipt.OPERATION_ID RECEIPT_OPERATION_ID,receipt.RECEIPT_STATE
              from RRL_TT_HU_LOAD_FACT lf left join RRL_STORE_RECEIPT_FACT receipt on receipt.LOAD_OPERATION_ID=lf.LOAD_OPERATION_ID
             where lf.TT_ID=:trip and lf.STATUS='DEPARTED'
               and exists(select 1 from RRL_STORE_RECEIPT_POLICY where STORE_ADDR=:addr)
               and exists(select 1 from RRL_TT_HU_LOAD_ST member where member.LOAD_OPERATION_ID=lf.LOAD_OPERATION_ID and member.ACTIVE_FLAG=1 and member.DESTINATION_ADDR=:addr)
               and not exists(select 1 from RRL_TT_HU_LOAD_ST member where member.LOAD_OPERATION_ID=lf.LOAD_OPERATION_ID and member.ACTIVE_FLAG=1 and (member.DESTINATION_ADDR is null or member.DESTINATION_ADDR<>:addr))
               and (exists(select 1 from RUSERS where ID=:actor and USER_GROUP='GLOBAL_ADMIN')
                    or exists(select 1 from RRL_STORE_RECEIPT_USER where USER_ID=:actor and STORE_ADDR=:addr))
             order by lf.LOADED_AT,lf.LOAD_OPERATION_ID fetch first 201 rows only
        """,{"trip":trip_id,"addr":store_address,"actor":actor})
        if len(rows)>200:
            raise StoreReceiptError("STORE_RECEIPT_PLACE_BOUND_200","Разбейте приёмку на отдельные рейсы")
        return rows

    def confirm(self, operation_id: str, load_operation_id: str, store_address: str, metadata: dict[str,Any], actor: str) -> dict[str,Any]:
        return self.post("STORE_RECEIPT",operation_id,
                         {"load_operation_id":load_operation_id,"store_address":store_address},metadata,actor)

    def configure(self, store_address: str, mode: str, expected_version: int, actor: str) -> dict[str,Any]:
        with stock_configuration_transaction(self.gateway,"Explicit store receipt policy",actor,"warehouse_settings_edit") as cursor:
            cursor.execute("select count(*) from RRL_ADDR where ADDR=:addr",{"addr":store_address})
            if cursor.fetchone()[0]!=1:
                raise StoreReceiptError("STORE_ADDRESS_AMBIGUOUS","Нужен один действующий адрес магазина")
            cursor.execute("select POLICY_VERSION from RRL_STORE_RECEIPT_POLICY where STORE_ADDR=:addr",{"addr":store_address})
            rows=cursor.fetchall()
            if (rows[0][0] if rows else 0)!=expected_version:
                raise StoreReceiptError("STORE_POLICY_VERSION_CONFLICT","Обновите настройки адреса")
            cursor.execute("""
                merge into RRL_STORE_RECEIPT_POLICY p using(select :addr STORE_ADDR from dual)s on(p.STORE_ADDR=s.STORE_ADDR)
                when matched then update set RECEIPT_MODE=:receipt_mode,POLICY_VERSION=POLICY_VERSION+1,CHANGED_BY=:actor,CHANGED_AT=systimestamp
                when not matched then insert(STORE_ADDR,RECEIPT_MODE,POLICY_VERSION,CHANGED_BY) values(:addr,:receipt_mode,1,:actor)
            """,{"addr":store_address,"receipt_mode":mode,"actor":actor})
        return {"store_address":store_address,"mode":mode,"policy_version":expected_version+1}

    def assign_receiver(self, store_address: str, username: str, actor: str) -> dict[str,Any]:
        with stock_configuration_transaction(self.gateway,"Explicit store receiver binding",actor,"warehouse_settings_edit") as cursor:
            cursor.execute("select count(*) from RUSERS where ID=:user_id",{"user_id":username})
            if cursor.fetchone()[0]!=1:
                raise StoreReceiptError("STORE_RECEIVER_UNKNOWN","Получатель должен быть действующим пользователем RUSERS")
            cursor.execute("select count(*) from RRL_STORE_RECEIPT_POLICY where STORE_ADDR=:addr",{"addr":store_address})
            if cursor.fetchone()[0]!=1:
                raise StoreReceiptError("STORE_POLICY_REQUIRED","Сначала настройте режим приёмки адреса")
            cursor.execute("""
                merge into RRL_STORE_RECEIPT_USER p using(select :user_id USER_ID,:addr STORE_ADDR from dual)s
                 on(p.USER_ID=s.USER_ID and p.STORE_ADDR=s.STORE_ADDR)
                when not matched then insert(USER_ID,STORE_ADDR,ASSIGNED_BY) values(:user_id,:addr,:actor)
            """,{"user_id":username,"addr":store_address,"actor":actor})
        return {"store_address":store_address,"username":username,"assigned":True}
