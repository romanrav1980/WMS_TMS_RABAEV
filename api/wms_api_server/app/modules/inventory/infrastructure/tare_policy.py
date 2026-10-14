from typing import Any
import oracledb
from ...platform.public import stock_configuration_transaction
from ..contracts_tare import TareError

class TarePolicy:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def read(self,scope_kind: str,scope_key: str) -> dict[str,Any]:
        rows=self.gateway.fetch_all("select SCOPE_KIND,SCOPE_KEY,RETURN_MODE,RETURN_DAYS,TIMEZONE_REGION,POLICY_VERSION,CHANGED_BY,CHANGED_AT from RRL_TARE_RETURN_POLICY where SCOPE_KIND=:kind and SCOPE_KEY=:scope",{"kind":scope_kind,"scope":scope_key})
        return rows[0] if rows else {"scope_kind":scope_kind,"scope_key":scope_key,"policy_version":0}

    def configure(self,scope_kind: str,scope_key: str,metadata: dict[str,Any],actor: str) -> dict[str,Any]:
        try:
            with stock_configuration_transaction(self.gateway,"Tare return deadline configuration",actor,"warehouse_settings_edit") as cursor:
                cursor.execute("select POLICY_VERSION from RRL_TARE_RETURN_POLICY where SCOPE_KIND=:kind and SCOPE_KEY=:scope",{"kind":scope_kind,"scope":scope_key})
                rows=cursor.fetchall();version=rows[0][0] if rows else 0
                if version!=metadata["expected_version"]:
                    raise TareError("TARE_POLICY_VERSION_CONFLICT","Покажите текущую редакцию срока возврата")
                cursor.execute("""
                    merge into RRL_TARE_RETURN_POLICY p using(select :kind SCOPE_KIND,:scope SCOPE_KEY from dual)s
                    on(p.SCOPE_KIND=s.SCOPE_KIND and p.SCOPE_KEY=s.SCOPE_KEY)
                    when matched then update set RETURN_MODE=:return_mode,RETURN_DAYS=:days,TIMEZONE_REGION=:timezone,
                    POLICY_VERSION=POLICY_VERSION+1,CHANGED_BY=:actor,CHANGED_AT=systimestamp
                    when not matched then insert(SCOPE_KIND,SCOPE_KEY,RETURN_MODE,RETURN_DAYS,TIMEZONE_REGION,POLICY_VERSION,CHANGED_BY)
                    values(:kind,:scope,:return_mode,:days,:timezone,1,:actor)
                """,{"kind":scope_kind,"scope":scope_key,"return_mode":metadata["return_mode"],"days":metadata["return_days"],"timezone":metadata["timezone_region"],"actor":actor})
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if 20800<=code<=20999:
                raise TareError("TARE_POLICY_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
            raise
        return self.read(scope_kind,scope_key)

    def debt(self,ware_id: int,actor: str) -> list[dict[str,Any]]:
        return self.gateway.fetch_all("""
            select d.OWNER_WARE_ID,d.PALLET_TYPE_ID,t.PALLET_TYPE_NAME,d.CONDITION_CODE,d.STORE_ADDR,d.TT_ID,d.ACCEPT_OPERATION_ID,d.CLAIM_KEY,
                   to_char(d.ACCEPTED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') DELIVERED_QUANTITY,
                   to_char(d.OUTSTANDING_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') OUTSTANDING_QUANTITY,
                   d.ACCEPTED_AT,d.SCOPE_KIND,d.SCOPE_KEY,d.POLICY_VERSION,d.RETURN_MODE,d.RETURN_DAYS,d.TIMEZONE_REGION,
                   to_char(d.EFFECTIVE_DUE_AT at time zone '+00:00','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') EFFECTIVE_DUE_AT,d.DEBT_STATE
              from RRL_TARE_STORE_DEBT d join RRL_PALLET_TYPE t on t.PALLET_TYPE_ID=d.PALLET_TYPE_ID
             where d.OWNER_WARE_ID=:ware and d.OUTSTANDING_QTY>0 and(
                RRL_HAS_WRIGHT(:actor,'tare_manage')=1
                or exists(select 1 from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0 and(upper(trim(u.USER_GROUP))='GLOBAL_ADMIN' or u.WARE_ID=d.OWNER_WARE_ID))
                or exists(select 1 from RRL_STORE_RECEIPT_USER su where su.USER_ID=:actor and su.STORE_ADDR=d.STORE_ADDR)
                or exists(select 1 from RRL_TRANSPORT_DRIVER_USER b join RRL_TRANSPORT_TASK tt on tt.VODITEL_ID=b.DRIVER_ID where b.USER_ID=:actor and b.ACTIVE=1 and tt.ID=d.TT_ID))
             order by case d.DEBT_STATE when 'OVERDUE' then 0 when 'UNCONFIGURED_LEGACY' then 1 else 2 end,d.EFFECTIVE_DUE_AT,d.ACCEPTED_AT,d.ACCEPT_OPERATION_ID
             fetch first 200 rows only
        """,{"ware":ware_id,"actor":actor})
