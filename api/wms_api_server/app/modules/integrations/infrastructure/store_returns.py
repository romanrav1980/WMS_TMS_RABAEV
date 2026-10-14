from collections.abc import Callable
from typing import Any
from ..domain.store_return import read_store_return


class SapStoreReturns:
    def __init__(self,post: Callable[[str,str,dict[str,Any],dict[str,Any],str],dict[str,Any]]) -> None:
        self.post=post

    def receive(self,raw: bytes,actor: str) -> dict[str,Any]:
        document=read_store_return(raw)
        return self.post("STORE_RETURN_SAP_BIND",str(document["operation_id"]),
                         {"approval_operation_id":document["approval_operation_id"]},document["metadata"],actor)
