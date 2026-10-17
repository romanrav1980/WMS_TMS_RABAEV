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
            cursor.execute("select RRL_ACCESS_API.is_admin(:actor) from dual",actor=actor)
            global_admin=cursor.fetchone()[0]==1
            if warehouse is not None:
                cursor.execute("select RRL_ACCESS_API.allowed(:actor,'pick_wave_view','WAREHOUSE',:ware) from dual",actor=actor,ware=str(warehouse))
                if cursor.fetchone()[0]!=1:
                    raise HTTPException(403,detail="WAVE_CURRENT_WARE_VIEWER_REQUIRED")
            elif not global_admin:
                cursor.execute("""select ID from RRL_WARES
                    where RRL_ACCESS_API.allowed(:actor,'pick_wave_view','WAREHOUSE',to_char(ID))=1
                    order by ID fetch first 2 rows only""",actor=actor)
                available=cursor.fetchall()
                if not available:
                    raise HTTPException(403,detail="WAVE_ACTIVE_VIEWER_REQUIRED")
                if len(available)>1:
                    raise HTTPException(422,detail="WAVE_SELECT_EXPLICIT_WAREHOUSE")
                warehouse=int(available[0][0])
            return reader(TransactionGateway(cursor),warehouse)
