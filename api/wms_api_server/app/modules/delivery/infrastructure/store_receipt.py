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

    def abandon_unloading(self,body: dict[str,Any],actor: str)->dict[str,Any]:
        from .store_unloading import abandon_unloading
        return abandon_unloading(self.gateway,body,actor)

    def start_unloading(self,body: dict[str,Any],actor: str)->dict[str,Any]:
        from .store_unloading import start_unloading
        return start_unloading(self.gateway,body,actor)

    def unloading(self,load: str,address: str,actor: str)->dict[str,Any]:
        from .store_unloading import read_unloading
        return read_unloading(self.gateway,load,address,actor)

    def release_custody(self,operation_id: str,receipt_id: str,actor: str) -> dict[str,Any]:
        return self.post("STORE_CUSTODY_RELEASE",operation_id,{"receipt_operation_id":receipt_id},{},actor)

    def cases(self, address: str, after: str, limit: int) -> dict[str,Any]:
        return StoreCases(self.gateway).list(address,after,limit)

    def case_detail(self, case_id: str) -> dict[str,Any]:
        return StoreCases(self.gateway).detail(case_id)

    def preview(self, load_operation_id: str, store_address: str, actor: str) -> dict[str,Any]:
        return read_store_preview(self.gateway,load_operation_id,store_address,actor)

    def places(self,trip_id: int,store_address: str,actor: str,after: str="",limit: int=200)->list[dict[str,Any]]:
        if limit<1 or limit>200 or len(after)>100:raise StoreReceiptError("STORE_PLACE_PAGE_BOUND","Use a page of1..200 places",422)
        try:
            with self.gateway.transaction("Current store receiver page access")as cur:
                cur.callproc("RRL_STOCK_STORE_RECEIPT_READ.require_receiver",[actor,store_address])
        except oracledb.DatabaseError as exc:
            if getattr(exc.args[0],"code",0)==20882:raise StoreReceiptError("STORE_RECEIPT_FORBIDDEN","Current authorized receiver required",403)from exc
            raise
        params={"trip":trip_id,"addr":store_address,"actor":actor,"after_id":after,"page_size":limit}
        eligible="""
            select lf.LOAD_OPERATION_ID,coalesce(lf.ROOT_UID,'CASE:'||to_char(lf.ROOT_CASE_TASK_ID)) ROOT_KEY,
                   lf.GROSS_WEIGHT_KG,lf.DEPARTED_AT,receipt.OPERATION_ID RECEIPT_OPERATION_ID,receipt.RECEIPT_STATE,lf.LOADED_AT SORT_AT
              from RRL_TT_HU_LOAD_FACT lf left join RRL_STORE_RECEIPT_FACT receipt on receipt.LOAD_OPERATION_ID=lf.LOAD_OPERATION_ID
             where lf.TT_ID=:trip and lf.STATUS='DEPARTED'
               and not exists(select 1 from RRL_INTERWARE_PLAN leg where leg.SOURCE_LOAD_OPERATION_ID=lf.LOAD_OPERATION_ID)
               and exists(select 1 from RRL_STORE_RECEIPT_POLICY where STORE_ADDR=:addr)
               and exists(select 1 from RRL_TT_HU_LOAD_ST member where member.LOAD_OPERATION_ID=lf.LOAD_OPERATION_ID and member.ACTIVE_FLAG=1 and member.DESTINATION_ADDR=:addr)
               and not exists(select 1 from RRL_TT_HU_LOAD_ST member where member.LOAD_OPERATION_ID=lf.LOAD_OPERATION_ID and member.ACTIVE_FLAG=1 and (member.DESTINATION_ADDR is null or member.DESTINATION_ADDR<>:addr))
               and exists(select 1 from RUSERS receiver where receiver.ID=:actor and nvl(receiver.DELETED,0)=0
                and(RRL_ACCESS_API.allowed(receiver.ID,'store_receipt_confirm','STORE',lower(rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(:addr,'AL32UTF8'),4))))=1
                  or(RRL_HAS_WRIGHT(receiver.ID,'store_receipt_confirm')=1 and exists(select 1 from RRL_STORE_RECEIPT_USER binding where binding.USER_ID=receiver.ID and binding.STORE_ADDR=:addr))))
"""
        if after:
            found=self.gateway.fetch_all("with eligible as("+eligible+")select count(*) N from eligible where LOAD_OPERATION_ID=:after_id",{k:v for k,v in params.items()if k!="page_size"})
            if found[0]["n"]!=1:raise StoreReceiptError("STORE_PLACE_CURSOR_SCOPE","Cursor must belong to the current trip/address/receiver",422)
        return self.gateway.fetch_all("with eligible as("+eligible+""")
            select l.LOAD_OPERATION_ID,l.ROOT_KEY,l.GROSS_WEIGHT_KG,l.DEPARTED_AT,l.RECEIPT_OPERATION_ID,l.RECEIPT_STATE from eligible l
             where :after_id is null or exists(select 1 from eligible anchor where anchor.LOAD_OPERATION_ID=:after_id
                and(l.SORT_AT>anchor.SORT_AT or(l.SORT_AT=anchor.SORT_AT and l.LOAD_OPERATION_ID>anchor.LOAD_OPERATION_ID)))
             order by l.SORT_AT,l.LOAD_OPERATION_ID fetch first :page_size rows only""",params)

    def confirm(self, operation_id: str, load_operation_id: str, store_address: str, metadata: dict[str,Any], actor: str) -> dict[str,Any]:
        metadata=dict(metadata)
        if metadata.get('unloading')is None:metadata.pop('unloading',None)
        scans=metadata.pop("scans",None)
        if scans:
            from ...inventory.public import normalize_unit_scan_codes
            try:
                metadata["unit_scans"]=normalize_unit_scan_codes(scans)
            except ValueError as exc:
                raise StoreReceiptError("STORE_MARK_SCAN_INVALID",str(exc),422,operation_id) from exc
        aggregates=metadata.get("aggregation_scans",[])
        if aggregates:
            from ...inventory.public import normalize_interwarehouse_scans
            normalized=[]
            try:
                for entry in aggregates:
                    disposition=entry.get("disposition","ACCEPTED")
                    if disposition not in("ACCEPTED","REFUSED","DAMAGED"):raise ValueError("Invalid aggregate disposition")
                    value=normalize_interwarehouse_scans({"aggregation_scans":[{k:v for k,v in entry.items()if k!="disposition"}]})["aggregation_scans"][0]
                    normalized.append(dict(value,disposition=disposition))
            except ValueError as exc:
                raise StoreReceiptError("STORE_AGG_SCAN_INVALID",str(exc),422,operation_id)from exc
            metadata["aggregation_scans"]=normalized
        else:metadata.pop("aggregation_scans",None)
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
