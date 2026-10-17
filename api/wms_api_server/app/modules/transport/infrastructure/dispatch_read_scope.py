"""Read admission held with access-revision guard; no independent role policy."""
from typing import Any, Callable, TypeVar
import oracledb
from ....transaction_gateway import TransactionGateway
from ....db import rows_as_dicts
from ..contracts_dispatch_read import DispatchReadError

T = TypeVar("T")


def trip_scope_predicate() -> str:
    """Trusted SQL fragment, fixed TT alias; never interpolate user-supplied SQL."""
    return """(RRL_ACCESS_API.is_admin(:read_actor)=1 or
      (exists(select 1 from RRL_SBORKA_PALLETS m where m.TRANSTASK_ID=TT.ID)
       and not exists(select 1 from RRL_SBORKA_PALLETS m where m.TRANSTASK_ID=TT.ID and
        (m.WARE_ID is null or RRL_ACCESS_API.allowed(:read_actor,'transport_dispatch_view','WAREHOUSE',to_char(m.WARE_ID))=0)))
      or (TT.USER_ID=:read_actor and not exists(select 1 from RRL_SBORKA_PALLETS m where m.TRANSTASK_ID=TT.ID)
          and exists(select 1 from RUSERS u where u.ID=:read_actor and nvl(u.DELETED,0)=0
           and RRL_ACCESS_API.allowed(:read_actor,'transport_dispatch_view','WAREHOUSE',to_char(u.WARE_ID))=1)))"""


def begin_scoped_read(cur: Any, actor: str) -> None:
    cur.execute("lock table RRL_ACCESS_REV in share mode wait 5")
    cur.execute("""select count(*) from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0 and
        (RRL_ACCESS_API.is_admin(:actor)=1 or exists(select 1 from RRL_WARES w
         where RRL_ACCESS_API.allowed(:actor,'transport_dispatch_view','WAREHOUSE',to_char(w.ID))=1))""", actor=actor)
    if cur.fetchone()[0] != 1:
        raise DispatchReadError("TRANSPORT_SCOPED_VIEW_REQUIRED")


def scoped_dispatch_rows(gateway: Any, sql: str, params: dict[str, Any], actor: str | None) -> list[dict[str, Any]]:
    if actor is None:
        return gateway.fetch_all(sql, params)
    try:
        with gateway.transaction("Dispatcher list scoped read") as cur:
            begin_scoped_read(cur, actor)
            cur.execute(sql, params)
            return [{key.upper(): value for key, value in row.items()} for row in rows_as_dicts(cur)]
    except oracledb.DatabaseError as error:
        raise DispatchReadError("TRANSPORT_SCOPED_READ_UNAVAILABLE", 503) from error


def guarded_trip_read(gateway: Any, task: int, actor: str, reader: Callable[[Any], T]) -> T:
    try:
        with gateway.transaction("Dispatcher object scoped read") as cur:
            begin_scoped_read(cur, actor)
            cur.execute("select count(*) from RRL_TRANSPORT_TASK TT where TT.ID=:task and " + trip_scope_predicate(),
                        task=task, read_actor=actor)
            if cur.fetchone()[0] != 1:
                raise DispatchReadError("TRANSPORT_TRIP_NOT_ACCESSIBLE", 404)
            return reader(TransactionGateway(cur))
    except oracledb.DatabaseError as error:
        raise DispatchReadError("TRANSPORT_SCOPED_READ_UNAVAILABLE", 503) from error
