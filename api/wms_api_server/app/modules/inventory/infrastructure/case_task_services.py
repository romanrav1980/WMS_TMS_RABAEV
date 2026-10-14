"""Existing CASE reads and metadata binding; no new physical executor."""
from typing import Any, Callable
from ....oracle_gateway import OracleGateway
from .case_pick_policy import case_pick_policy
from .case_shipment_binding import bind_case_shipment

class CaseTaskServices:
    def __init__(self,gateway: OracleGateway) -> None:self.gateway=gateway
    def marking_policy(self,task: int,line: int,actor: str,assert_scope: Callable[[Any,int,str,str],None]) -> dict[str,Any]:
        from ....transaction_gateway import TransactionGateway
        with self.gateway.transaction("Current CASE marking policy READ ONLY snapshot") as cur:
            cur.execute("set transaction read only")
            assert_scope(cur,task,actor,"case_pick_execute")
            return case_pick_policy(TransactionGateway(cur),task,line)
    def bind_shipment(self,task: int,pallet: str,container: str,version: int,actor: str) -> dict[str,Any]:
        return bind_case_shipment(self.gateway,task,pallet,container,version,actor)
