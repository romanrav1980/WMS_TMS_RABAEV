from collections.abc import Callable
from typing import Any
import oracledb
from ..contracts import LogisticsCostError
from .cost_access import require_warehouse
from .expense_catalog import set_article
from .expense_reports import report_expense
from .expense_decisions import decide_expense

class LogisticsExpenses:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def _action(self,fn: Callable[...,dict[str,Any]],*args: Any) -> dict[str,Any]:
        for attempt in range(2):
            try:return fn(self.gateway,*args)
            except oracledb.DatabaseError as exc:
                code=getattr(exc.args[0],"code",0)
                if code==1 and attempt==0:continue
                if code==1:raise LogisticsCostError("EXPENSE_OPERATION_CONFLICT","Операция или стадия уже сохранена") from exc
                if 20800<=code<=20999:raise LogisticsCostError("EXPENSE_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
                raise
        raise LogisticsCostError("EXPENSE_OPERATION_CONFLICT","Операция уже сохранена")

    def article(self,code: str,name: str,scope: str,included: bool,active: bool,version: int,actor: str) -> dict[str,Any]:
        return self._action(set_article,code,name,scope,included,active,version,actor)

    def normative_cost_sources(self,ware: int,actor: str,cost_operation_id: str|None=None)->list[dict[str,Any]]:
        from .transport_cost_read import normative_cost_sources
        return normative_cost_sources(self.gateway,ware,actor,cost_operation_id)

    def articles(self) -> list[dict[str,Any]]:
        return self.gateway.fetch_all("select CODE,NAME,OBJECT_SCOPE,INCLUDED_IN_RATE,ACTIVE_FLAG,VERSION_NO from RRL_LOGISTICS_EXP_ARTICLE order by CODE fetch first 200 rows only")

    def report(self,op: str,ware: int,code: str,kind: str,object_id: int,amount: str,currency: str,day: str,reference: str,reason: str,actor: str,correction: str|None=None,expected: str|None=None,cost_correction: str|None=None) -> dict[str,Any]:
        return self._action(report_expense,op,ware,code,kind,object_id,amount,currency,day,reference,reason,actor,correction,expected,cost_correction)

    def decide(self,op: str,expense: str,phase: str,outcome: str,basis: str,reference: str,reason: str,actor: str) -> dict[str,Any]:
        return self._action(decide_expense,op,expense,phase,outcome,basis,reference,reason,actor)

    def pending(self,ware: int,actor: str,operation_id: str|None=None) -> list[dict[str,Any]]:
        from ....transaction_gateway import TransactionGateway
        from .expense_register_read import warehouse_expenses
        with self.gateway.transaction("Read own warehouse expenses") as cur:
            cur.execute("set transaction read only")
            require_warehouse(cur,ware,actor,"transport_dispatch_view")
            return warehouse_expenses(TransactionGateway(cur),ware,operation_id)
