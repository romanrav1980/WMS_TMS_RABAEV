"""Current RUSERS warehouse, rights and original CASE evidence in one snapshot."""
from typing import Any
import oracledb
from ....transaction_gateway import TransactionGateway
from ..contracts_case_read import CaseReadError
from .case_read_model import LegacyCaseReads
from .case_view_scope import require_viewer, require_task_view


def native_task_scope(cur: Any, task: int, actor: str, permission: str) -> None:
    """Public legacy command guard: read scopes must never replace execution checks."""
    try:
        cur.callproc("RRL_CASE_TASK_ACCESS.assert_scope", [task, actor, permission, None])
    except oracledb.DatabaseError as exc:
        code = getattr(exc.args[0], "code", 0)
        if code == 20882:
            raise CaseReadError("CASE_CURRENT_WARE_VIEWER_REQUIRED", "Недоступный склад CASE-задания") from exc
        if code == 20886:
            missing = "CASE_TASK_IDENTITY_MISSING" in str(exc.args[0])
            raise CaseReadError("CASE_TASK_NOT_FOUND" if missing else "CASE_TASK_WARE_REQUIRED",
                                "CASE-задание отсутствует" if missing else "Не задан склад CASE-задания",
                                404 if missing else 409) from exc
        raise


def task_scope(cur: Any, task: int, actor: str) -> None:
    require_viewer(cur, actor)
    require_task_view(cur, task, actor)


class ScopedCaseReads:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def tasks(self, actor: str, resource: int | None, scope: str, status: str | None, limit: int,
              warehouse: int | None = None, wave: int | None = None, include_closed: bool = False) -> list[dict[str, Any]]:
        if scope not in {"mine", "free", "all", "self"} or not 1 <= limit <= 500:
            raise CaseReadError("CASE_LIST_SCOPE_INVALID", "Допустимы mine/free/all/self и предел1–500", 422)
        with self.gateway.transaction("Current CASE queue READ ONLY snapshot") as cur:
            if not getattr(self.gateway, "transaction_bound", False):
                cur.execute("set transaction read only")
            require_viewer(cur, actor, warehouse)
            if wave is not None:
                if isinstance(wave, bool) or not isinstance(wave, int) or wave < 1:
                    raise CaseReadError("CASE_WAVE_INVALID", "Номер волны должен быть положительным целым", 422)
                cur.execute("select WARE_ID from RRL_PICK_WAVE where PICK_WAVE_ID=:wave", wave=wave)
                row = cur.fetchone()
                if row is None:
                    raise CaseReadError("CASE_WAVE_NOT_FOUND", "Волна отсутствует", 404)
                require_viewer(cur, actor, row[0])
                if warehouse is not None and row[0] != warehouse:
                    raise CaseReadError("CASE_CURRENT_WARE_WAVE_REQUIRED", "Волна другого склада")
            if resource is not None:
                cur.execute("select WARE_ID from RRL_RESOURCE where RESOURCE_ID=:id and ACTIVE=1", id=resource)
                row = cur.fetchone()
                if row is None:
                    raise CaseReadError("CASE_RESOURCE_NOT_FOUND", "Действующий ресурс отсутствует", 404)
                require_viewer(cur, actor, row[0])
                if warehouse is not None and row[0] != warehouse:
                    raise CaseReadError("CASE_CURRENT_WARE_RESOURCE_REQUIRED", "Ресурс другого склада")
            return LegacyCaseReads(TransactionGateway(cur)).list_tasks(
                resource, scope, status, limit, warehouse, view_actor=actor, wave_id=wave, include_closed=include_closed,
            )

    def task(self, task: int, actor: str) -> dict[str, Any]:
        with self.gateway.transaction("Current CASE detail READ ONLY snapshot") as cur:
            if not getattr(self.gateway, "transaction_bound", False):
                cur.execute("set transaction read only")
            task_scope(cur, task, actor)
            result = LegacyCaseReads(TransactionGateway(cur)).get_task(task)
            if result is None:
                raise CaseReadError("CASE_TASK_NOT_FOUND", "CASE-задание отсутствует", 404)
            return result


    def carrier(self,warehouse:int,identifier:str,actor:str)->dict[str,Any]:
        if not identifier.strip() or len(identifier)>150:
            raise CaseReadError('CASE_CARRIER_IDENTIFIER_INVALID','Invalid carrier identifier',422)
        with self.gateway.transaction('Current scanned CASE detail READ ONLY snapshot')as cur:
            if not getattr(self.gateway,'transaction_bound',False):cur.execute('set transaction read only')
            require_viewer(cur,actor,warehouse)
            cur.execute('select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where WARE_ID=:w and SSCC=:id fetch first 2 rows only',w=warehouse,id=identifier.strip())
            rows=cur.fetchall()
            if not rows:raise CaseReadError('CASE_TASK_NOT_FOUND','Carrier not found',404)
            if len(rows)>1:raise CaseReadError('CASE_CARRIER_AMBIGUOUS','Carrier identifier is ambiguous',409)
            task=int(rows[0][0]);require_task_view(cur,task,actor)
            result=LegacyCaseReads(TransactionGateway(cur)).get_task(task)
            if result is None:raise CaseReadError('CASE_TASK_NOT_FOUND','Carrier not found',404)
            cur.execute("select RRL_ACCESS_API.allowed(:a,'case_pick_manage','WAREHOUSE',:w,:owner)from dual",a=actor,w=str(warehouse),owner=result.get('assigned_to'))
            permitted=cur.fetchone()[0]==1
            if permitted:
                try:cur.callproc('RRL_TRADE_CASE_ACCESS.assert_scope',[task,actor,1])
                except oracledb.DatabaseError as exc:
                    if getattr(exc.args[0],'code',0)!=20882:raise
                    permitted=False
            cur.execute('select count(*)from RRL_WMS_HU_LINK where CHILD_CASE_TASK_ID=:t and ACTIVE_FLAG=1',t=task);parent=cur.fetchone()[0]>0
            cur.execute("select count(*)from RRL_ASSEMBLY_SESSION where CASE_PICK_TASK_ID=:t and STATE in('OPEN','BLOCKED','HOLD')",t=task);assembly=cur.fetchone()[0]>0
            state_ok=result.get('status')not in{'CANCELLED','FAILED','SHIPPED'}and not result.get('shipped_operation')
            lots=result.get('physical_lots',[])
            result.update(return_allowed=permitted and state_ok and not parent and not assembly and 1<=len(lots)<=200,
                          return_blocking_reason='PERMISSION'if not permitted else'PARENT'if parent else'ASSEMBLY'if assembly else'STATE'if not state_ok else'EMPTY'if not lots else None)
            return result

    def shorts(self, actor: str, status: str | None, limit: int,
               warehouse: int | None = None) -> list[dict[str, Any]]:
        if not 1 <= limit <= 500:
            raise CaseReadError("CASE_LIST_SCOPE_INVALID", "Предел должен быть1–500", 422)
        with self.gateway.transaction("Current CASE shortages READ ONLY snapshot") as cur:
            if not getattr(self.gateway, "transaction_bound", False):
                cur.execute("set transaction read only")
            require_viewer(cur, actor, warehouse)
            return LegacyCaseReads(TransactionGateway(cur)).list_shorts(status, limit, warehouse, view_actor=actor)
