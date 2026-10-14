"""Current warehouse authorization and phase facts in one read-only Oracle snapshot."""
from pathlib import Path
from typing import Any
from ..contracts_store_returns import StoreReturnReceiveError
from ..domain.interwarehouse_timing import annotate_timing

QUEUE_SQL = Path(__file__).with_suffix(".sql").read_text(encoding="utf-8")


class InterwarehouseQueue:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def read(self, ware_id: int, actor: str, include_completed: bool=False) -> list[dict[str, Any]]:
        with self.gateway.transaction("Interwarehouse current scope and aware phase facts") as q:
            q.execute("set transaction read only")
            q.execute("""select count(*) from RUSERS where ID=:actor and nvl(DELETED,0)=0
                and RRL_HAS_WRIGHT(ID,'transport_dispatch_view')=1
                and(WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')""", actor=actor, ware=ware_id)
            if q.fetchone()[0] != 1:
                raise StoreReturnReceiveError("INTERWARE_WARE_FORBIDDEN", "Пользователь не назначен складу или лишён права просмотра", 403)
            q.execute(QUEUE_SQL, ware=ware_id,history=int(include_completed))
            columns = [column[0].lower() for column in q.description]
            return [annotate_timing(dict(zip(columns, values))) for values in q.fetchall()]
