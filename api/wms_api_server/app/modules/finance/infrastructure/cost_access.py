from typing import Any
from ..contracts import LogisticsCostError

def require_warehouse(cursor: Any,ware: int,actor: str,permission: str) -> None:
    cursor.execute("""select count(*)from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0
    and(u.WARE_ID=:ware or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,:permission)=1
    and 1=(select count(*)from RRL_WARES where ID=:ware)""",{"actor":actor,"ware":ware,"permission":permission})
    if cursor.fetchone()[0]!=1:raise LogisticsCostError("COST_WAREHOUSE_FORBIDDEN","Нет полномочий на этот склад",403)
