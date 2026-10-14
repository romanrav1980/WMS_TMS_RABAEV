from collections.abc import Callable
from typing import Any
import oracledb
from ...platform.public import stock_configuration_transaction
from ..contracts_store_returns import StoreReturnReceiveError


class StoreReturnReceiving:
    def __init__(self,gateway: Any,post: Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]) -> None:
        self.gateway=gateway
        self.post=post

    def configure(self,ware_id: int,supplier_cell: str,disposal_cell: str,expected_version: int,actor: str) -> dict[str,Any]:
        try:
            with stock_configuration_transaction(self.gateway,"Store return segregated receiving configuration",actor,"warehouse_settings_edit") as cursor:
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
                cursor.execute("update RRL_STORE_RETURN_WARE_POLICY set REUSE_RECEIVE_CELL=:cell,POLICY_VERSION=POLICY_VERSION+1,CHANGED_BY=:actor,CHANGED_AT=systimestamp where WARE_ID=:ware and POLICY_VERSION=:version",{"ware":ware_id,"cell":receive_cell,"actor":actor,"version":expected_version})
                if cursor.rowcount!=1:raise StoreReturnReceiveError("RETURN_REUSE_POLICY_VERSION_CONFLICT","Покажите текущие настройки возврата")
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if 20800<=code<=20999:raise StoreReturnReceiveError("RETURN_REUSE_ZONE_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
            raise
        return self.policy(ware_id)

    def policy(self,ware_id: int) -> dict[str,Any]:
        rows=self.gateway.fetch_all("select WARE_ID,SUPPLIER_RECEIVE_CELL,DISPOSAL_RECEIVE_CELL,SUPPLIER_TARGET_CELL,DISPOSAL_TARGET_CELL,REUSE_RECEIVE_CELL,POLICY_VERSION from RRL_STORE_RETURN_WARE_POLICY where WARE_ID=:ware",{"ware":ware_id})
        return rows[0] if rows else {"ware_id":ware_id,"policy_version":0}

    def pending(self,ware_id: int,actor: str) -> list[dict[str,Any]]:
        auth=self.gateway.fetch_all("select count(*) ALLOWED from RUSERS where ID=:actor and nvl(DELETED,0)=0 and(upper(trim(USER_GROUP))='GLOBAL_ADMIN' or WARE_ID=:ware)",{"actor":actor,"ware":ware_id})
        if auth[0]["allowed"]!=1:
            raise StoreReturnReceiveError("STORE_RETURN_RECEIVER_WAREHOUSE_BINDING_REQUIRED","Пользователь не назначен принимающему складу",403)
        return self.gateway.fetch_all("""
            select p.OPERATION_ID PICKUP_OPERATION_ID,p.VEHICLE_NUMBER,h.PALLET_IDENTIFIER,
                   a.ARTICLE,a.LOT_UID,a.BASE_UOM,a.DISPOSITION,t.STORE_ADDR,
                   to_char(a.BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QUANTITY,
                   to_char(h.GROSS_WEIGHT_KG,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') GROSS_WEIGHT_KG,
                   to_char(original.EXPIRY_DATE,'YYYY-MM-DD') EXPIRY_DATE,s.RETURN_DOCUMENT,
                   case a.DISPOSITION when 'SUPPLIER' then policy.SUPPLIER_RECEIVE_CELL when 'DISPOSAL' then policy.DISPOSAL_RECEIVE_CELL when 'REUSE' then policy.REUSE_RECEIVE_CELL end RECEIVE_CELL,
                   (select min(r.SUPPLIER_BATCH) from RRL_SAP_PALLET_RECEIPT r where r.UID_PALLET=nvl(original.STOCK_ORIGIN_UID,original.UID_PALLET)) ORIGINAL_SUPPLIER_BATCH
              from RRL_STORE_RETURN_PICKUP p join RRL_STORE_RETURN_HANDOVER h on h.OPERATION_ID=p.HANDOVER_OPERATION_ID
              join RRL_STORE_RETURN_TRANSPORT t on t.OPERATION_ID=h.TRANSPORT_OPERATION_ID
              join RRL_STORE_RETURN_APPROVAL a on a.OPERATION_ID=t.APPROVAL_OPERATION_ID
              join RRL_STORE_RETURN_SAP s on s.OPERATION_ID=t.SAP_OPERATION_ID
              join RRL_PALLETS original on original.UID_PALLET=a.LOT_UID
              left join RRL_STORE_RETURN_WARE_POLICY policy on policy.WARE_ID=s.WARE_ID
             where s.WARE_ID=:ware and not exists(select 1 from RRL_STORE_RETURN_RECEIPT r where r.PICKUP_OPERATION_ID=p.OPERATION_ID)
             order by p.TAKEN_AT,p.OPERATION_ID fetch first 100 rows only
        """,{"ware":ware_id})

    def confirm(self,operation_id: str,pickup_id: str,metadata: dict[str,Any],actor: str) -> dict[str,Any]:
        return self.post("STORE_RETURN_RECEIVE",operation_id,{"pickup_operation_id":pickup_id},metadata,actor)
