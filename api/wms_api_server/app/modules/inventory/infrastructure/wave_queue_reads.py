"""Scope existing wave readers to current Oracle actor and one read-only snapshot."""
from typing import Any, Callable
from fastapi import HTTPException
from ....transaction_gateway import TransactionGateway
from .wave_execution_reader import assert_wave_view


class WaveQueueReads:
    def __init__(self, gateway: Any) -> None:
        self.gateway=gateway

    def wave(self, wave_id: int, actor: str, reader: Callable[[Any], Any]) -> Any:
        if wave_id<1:
            raise HTTPException(422,detail="Positive wave ID required")
        with self.gateway.transaction("Existing wave view READ ONLY") as cursor:
            if not getattr(self.gateway,"transaction_bound",False):
                cursor.execute("set transaction read only")
            assert_wave_view(cursor,wave_id,actor)
            return reader(TransactionGateway(cursor))

    def waves(self, actor: str, warehouse: int | None, reader: Callable[[Any,int | None],Any]) -> Any:
        with self.gateway.transaction("Current warehouse wave queue READ ONLY") as cursor:
            if not getattr(self.gateway,"transaction_bound",False):
                cursor.execute("set transaction read only")
            cursor.execute("""select WARE_ID,upper(trim(USER_GROUP)) from RUSERS
                where ID=:actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'pick_wave_view')=1""",actor=actor)
            row=cursor.fetchone()
            if row is None:
                raise HTTPException(403,detail="WAVE_ACTIVE_VIEWER_REQUIRED")
            actor_warehouse,group=row
            if group!="GLOBAL_ADMIN":
                if actor_warehouse is None or (warehouse is not None and warehouse!=actor_warehouse):
                    raise HTTPException(403,detail="WAVE_CURRENT_WARE_VIEWER_REQUIRED")
                warehouse=actor_warehouse
            return reader(TransactionGateway(cursor),warehouse)
