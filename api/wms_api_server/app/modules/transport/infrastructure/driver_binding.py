from typing import Any
import oracledb
from ...platform.public import stock_configuration_transaction
from ..contracts import TransportLoadingError


class DriverBinding:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def configure(self,driver_id: int,user_id: str,active: bool,expected_version: int,actor: str) -> dict[str,Any]:
        try:
            with stock_configuration_transaction(self.gateway,"Explicit authenticated driver binding",actor,"warehouse_settings_edit") as cursor:
                cursor.execute("select BINDING_VERSION from RRL_TRANSPORT_DRIVER_USER where DRIVER_ID=:id",{"id":driver_id})
                rows=cursor.fetchall()
                if (rows[0][0] if rows else 0)!=expected_version:
                    raise TransportLoadingError("DRIVER_BINDING_VERSION_CONFLICT","Обновите привязку водителя")
                cursor.execute("""
                    merge into RRL_TRANSPORT_DRIVER_USER d using(select :driver DRIVER_ID from dual)s on(d.DRIVER_ID=s.DRIVER_ID)
                    when matched then update set USER_ID=:user_id,ACTIVE=:active,BINDING_VERSION=BINDING_VERSION+1,CHANGED_BY=:actor,CHANGED_AT=systimestamp
                    when not matched then insert(DRIVER_ID,USER_ID,ACTIVE,BINDING_VERSION,CHANGED_BY)values(:driver,:user_id,:active,1,:actor)
                """,{"driver":driver_id,"user_id":user_id,"active":int(active),"actor":actor})
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code==1 or 20800<=code<=20999:
                raise TransportLoadingError("DRIVER_BINDING_REJECTED",str(exc.args[0]).split("\n",1)[0],status=403 if code==20882 else 409) from exc
            raise
        return {"driver_id":driver_id,"user_id":user_id,"active":active,"binding_version":expected_version+1}

    def get(self,driver_id: int) -> dict[str,Any]:
        rows=self.gateway.fetch_all("select DRIVER_ID,USER_ID,ACTIVE,BINDING_VERSION,CHANGED_BY,CHANGED_AT from RRL_TRANSPORT_DRIVER_USER where DRIVER_ID=:id",{"id":driver_id})
        return rows[0] if rows else {"driver_id":driver_id,"binding_version":0,"active":False}
