from typing import Any
from ..contracts_plan import TransportPlanError

def dispatcher(cur: Any, actor: str) -> None:
    cur.execute("""select count(*)from RUSERS where ID=:actor and nvl(DELETED,0)=0
        and RRL_HAS_WRIGHT(ID,'transport_dispatch_edit')=1""", actor=actor)
    if cur.fetchone()[0] != 1:
        raise TransportPlanError("PLAN_ACTIVE_DISPATCHER_REQUIRED", "Требуется действующий диспетчер", 403)

