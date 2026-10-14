from collections.abc import Callable
from typing import Any
import oracledb
from ...platform.public import stock_configuration_transaction,read_oracle_json
from ..domain.interwarehouse_scans import normalize_interwarehouse_scans
from ..contracts_store_returns import StoreReturnReceiveError
from . import return_receiving_reads as reads


class StoreReturnReceiving:
    def __init__(self,gateway: Any,post: Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]) -> None:
        self.gateway=gateway
        self.post=post

    def configure(self,ware_id: int,supplier_cell: str,disposal_cell: str,expected_version: int,actor: str) -> dict[str,Any]:
        try:
            with stock_configuration_transaction(self.gateway,"Store return segregated receiving configuration",actor,"warehouse_settings_edit") as cursor:
                reads.require_scope(cursor,ware_id,actor,"warehouse_settings_edit")
                cursor.execute("select POLICY_VERSION from RRL_STORE_RETURN_WARE_POLICY where WARE_ID=:ware",{"ware":ware_id})
                rows=cursor.fetchall()
                if (rows[0][0] if rows else 0)!=expected_version:
                    raise StoreReturnReceiveError("STORE_RETURN_WARE_POLICY_VERSION_CONFLICT","Обновите настройки приёмки возвратов")
                cursor.execute("""
                    merge into RRL_STORE_RETURN_WARE_POLICY d using(select :ware WARE_ID from dual)s on(d.WARE_ID=s.WARE_ID)
                    when matched then update set SUPPLIER_RECEIVE_CELL=:supplier_cell,DISPOSAL_RECEIVE_CELL=:disposal_cell,
                      POLICY_VERSION=POLICY_VERSION+1,CHANGED_BY=:actor,CHANGED_AT=systimestamp
                    when not matched then insert(WARE_ID,SUPPLIER_RECEIVE_CELL,DISPOSAL_RECEIVE_CELL,POLICY_VERSION,CHANGED_BY)
                      values(:ware,:supplier_cell,:disposal_cell,1,:actor)
                """,{"ware":ware_id,"supplier_cell":supplier_cell,"disposal_cell":disposal_cell,"actor":actor})
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if 20800<=code<=20999:
                raise StoreReturnReceiveError("STORE_RETURN_WARE_POLICY_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
            raise
        return {"ware_id":ware_id,"supplier_receive_cell":supplier_cell,"disposal_receive_cell":disposal_cell,"policy_version":expected_version+1}

    def configure_reuse(self,ware_id: int,receive_cell: str,expected_version: int,actor: str) -> dict[str,Any]:
        try:
            with stock_configuration_transaction(self.gateway,"Return good-box segregated receiving zone",actor,"warehouse_settings_edit") as cursor:
                reads.require_scope(cursor,ware_id,actor,"warehouse_settings_edit")
                cursor.execute("update RRL_STORE_RETURN_WARE_POLICY set REUSE_RECEIVE_CELL=:cell,POLICY_VERSION=POLICY_VERSION+1,CHANGED_BY=:actor,CHANGED_AT=systimestamp where WARE_ID=:ware and POLICY_VERSION=:version",{"ware":ware_id,"cell":receive_cell,"actor":actor,"version":expected_version})
                if cursor.rowcount!=1:raise StoreReturnReceiveError("RETURN_REUSE_POLICY_VERSION_CONFLICT","Покажите текущие настройки возврата")
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if 20800<=code<=20999:raise StoreReturnReceiveError("RETURN_REUSE_ZONE_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
            raise
        return self.policy(ware_id,actor)

    def policy(self,ware_id: int,actor: str) -> dict[str,Any]:
        return reads.policy(self.gateway,ware_id,actor)

    def page(self,ware_id: int,after: str,limit: int,actor: str) -> dict:
        return reads.page(self.gateway,ware_id,actor,after,limit)

    def source(self,ware_id: int,pickup_id: str,actor: str) -> dict:
        return reads.source(self.gateway,ware_id,pickup_id,actor)

    def pending(self,ware_id: int,actor: str) -> list[dict[str,Any]]:
        result=reads.page(self.gateway,ware_id,actor,limit=100,proof=True)
        if result["has_more"]:raise StoreReturnReceiveError("RETURN_RECEIVING_USE_PAGED_QUEUE","Откройте очередь с продолжением списка")
        return result["items"]

    def confirm(self,operation_id: str,pickup_id: str,metadata: dict[str,Any],actor: str) -> dict[str,Any]:
        try:metadata=normalize_interwarehouse_scans(metadata)
        except (ValueError,KeyError,TypeError)as exc:raise StoreReturnReceiveError("RETURN_SCAN_INPUT_INVALID",str(exc),422,operation_id)from exc
        return self.post("STORE_RETURN_RECEIVE",operation_id,{"pickup_operation_id":pickup_id},metadata,actor)
