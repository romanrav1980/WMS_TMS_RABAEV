"""Pure native view admission and explicit legacy calendar fields for supply worklists."""
from datetime import date,timedelta
from typing import Any

DATE_FIELDS={'PLANNED_ACCEPT':'h.PLANNING_ACCEPT_TIME','ACCEPTED':'h.DATE_OF_ACCEPT','DOCUMENT':'h.DATE_OF_NAKLAD'}


def require_supply_view(cur: Any,actor: str,warehouse: int|None=None)->None:
    cur.execute("""select count(*) from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0
        and exists(select 1 from RRL_WARES w where (:ware is null or w.ID=:ware)
        and RRL_ACCESS_API.allowed(:actor,'sap_supply_view','WAREHOUSE',to_char(w.ID))=1)""",
        actor=actor,ware=warehouse)
    if cur.fetchone()[0]!=1:raise PermissionError('SUPPLY_SCOPED_VIEW_REQUIRED')


def calendar_window(start: date|None,finish: date|None,basis: str,include_unplanned: bool)->tuple[str,dict]:
    if basis not in DATE_FIELDS:raise ValueError('SUPPLY_DATE_BASIS_INVALID')
    if (start is None)!=(finish is None):raise ValueError('SUPPLY_BOTH_CALENDAR_DATES_REQUIRED')
    if start is None:return '1=1',{}
    if finish<start or (finish-start).days>=31 or finish==date.max:raise ValueError('SUPPLY_CALENDAR_WINDOW_MAX_31_DAYS')
    field=DATE_FIELDS[basis]
    expression=f'({field}>=:date_start and {field}<:date_finish)'
    if include_unplanned:expression=f'({expression} or {field} is null)'
    return expression,{'date_start':start,'date_finish':finish+timedelta(days=1)}
