"""Current actor scope for inventory reads and commands, including saved-result replay."""
from typing import Any
from ..contracts_observations import InventoryObservationError

def assert_inventory_scope(gateway: Any,actor: str,*,revision: int|None=None,warehouse: int|None=None) -> None:
    if revision is not None:
        rows=gateway.fetch_all("select 1 ALLOWED from RRL_REVIZION r where r.ID=:revision and exists(select 1 from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0 and(u.WARE_ID=r.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN'))",{"revision":revision,"actor":actor})
    else:
        rows=gateway.fetch_all("select 1 ALLOWED from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0 and(u.WARE_ID=:ware or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')",{"ware":warehouse,"actor":actor})
    if len(rows)!=1:
        raise InventoryObservationError("INVENTORY_CURRENT_WAREHOUSE_ACTOR_REQUIRED",403)
