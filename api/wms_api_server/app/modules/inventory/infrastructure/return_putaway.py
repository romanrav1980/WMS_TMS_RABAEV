from collections.abc import Callable
from typing import Any
import oracledb
from ...platform.public import stock_configuration_transaction
from ..contracts_store_returns import StoreReturnReceiveError


class ReturnPutaway:
    def __init__(self,gateway: Any,post: Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]) -> None:
        self.gateway=gateway
        self.post=post

    def configure(self,ware_id: int,supplier_target: str,disposal_target: str,expected_version: int,actor: str) -> dict[str,Any]:
        try:
            with stock_configuration_transaction(self.gateway,"Return placement target configuration",actor,"warehouse_settings_edit") as cursor:
                cursor.execute("select POLICY_VERSION from RRL_STORE_RETURN_WARE_POLICY where WARE_ID=:ware",{"ware":ware_id})
                rows=cursor.fetchall()
                if len(rows)!=1 or rows[0][0]!=expected_version:
                    raise StoreReturnReceiveError("STORE_RETURN_PLACEMENT_POLICY_VERSION_CONFLICT","Покажите текущие настройки зон")
                cursor.execute("""
                    update RRL_STORE_RETURN_WARE_POLICY set SUPPLIER_TARGET_CELL=:supplier,DISPOSAL_TARGET_CELL=:disposal,
                           POLICY_VERSION=POLICY_VERSION+1,CHANGED_BY=:actor,CHANGED_AT=systimestamp where WARE_ID=:ware
                """,{"ware":ware_id,"supplier":supplier_target,"disposal":disposal_target,"actor":actor})
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if 20800<=code<=20999:
                raise StoreReturnReceiveError("STORE_RETURN_PLACEMENT_CONFIGURATION_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
            raise
        return {"ware_id":ware_id,"supplier_target_cell":supplier_target,"disposal_target_cell":disposal_target,"policy_version":expected_version+1}

    def pending(self,ware_id: int,actor: str,receipt_operation_id: str | None=None) -> list[dict[str,Any]]:
        auth=self.gateway.fetch_all("select count(*) ALLOWED from RUSERS where ID=:actor and nvl(DELETED,0)=0 and(upper(trim(USER_GROUP))='GLOBAL_ADMIN' or WARE_ID=:ware)",{"actor":actor,"ware":ware_id})
        if auth[0]["allowed"]!=1:
            raise StoreReturnReceiveError("STORE_RETURN_PLACEMENT_WAREHOUSE_BINDING_REQUIRED","Пользователь не назначен складу",403)
        receipt_filter=" and r.OPERATION_ID=:receipt" if receipt_operation_id is not None else ""
        binds={"ware":ware_id}
        if receipt_operation_id is not None:
            binds["receipt"]=receipt_operation_id
        return self.gateway.fetch_all(f"""
            select r.OPERATION_ID RECEIPT_OPERATION_ID,r.UID_PALLET,r.ARTICLE,r.BASE_UOM,r.RECEIVE_CELL,r.DISPOSITION,r.NAKLAD_ID,
                   to_char(r.BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QUANTITY,
                   plan_record.TASK_ID,wt.STATUS TASK_STATUS,wt.TO_CELL,
                   case r.DISPOSITION when 'SUPPLIER' then policy.SUPPLIER_TARGET_CELL when 'DISPOSAL' then policy.DISPOSAL_TARGET_CELL when 'REUSE' then nvl(rule.PICK_CELL,card.CELL) end CURRENT_TARGET_CELL
              from RRL_STORE_RETURN_RECEIPT r join RRL_ARTICULS card on card.ACTICUL=r.ARTICLE left join RRL_RECEIPT_SKU_RULE rule on rule.ARTICUL=r.ARTICLE and rule.WARE_ID=r.WARE_ID left join RRL_STORE_RETURN_WARE_POLICY policy on policy.WARE_ID=r.WARE_ID
              left join RRL_STORE_RETURN_PUT_PLAN plan_record on plan_record.RECEIPT_OPERATION_ID=r.OPERATION_ID
                   and plan_record.TASK_ID=(select max(p.TASK_ID) from RRL_STORE_RETURN_PUT_PLAN p where p.RECEIPT_OPERATION_ID=r.OPERATION_ID)
              left join RRL_WAREHOUSE_TASK wt on wt.TASK_ID=plan_record.TASK_ID
             where r.WARE_ID=:ware{receipt_filter} and not exists(select 1 from RRL_STORE_RETURN_PLACEMENT placed where placed.RECEIPT_OPERATION_ID=r.OPERATION_ID)
             order by r.RECEIVED_AT,r.OPERATION_ID fetch first 100 rows only
        """,binds)

    def plan(self,operation_id: str,receipt_id: str,actor: str) -> dict[str,Any]:
        return self.post("STORE_RETURN_PUTAWAY_PLAN",operation_id,{"receipt_operation_id":receipt_id},{},actor)
