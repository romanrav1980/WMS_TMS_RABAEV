from __future__ import annotations
from typing import Any,Protocol

class TraceManifestError(RuntimeError):
    def __init__(self,code: str,message: str,status: int=409) -> None:
        self.code=code
        self.status=status
        super().__init__(message)

class TraceManifestPort(Protocol):
    def import_manifest(self,operation_id: str,raw: str,actor: str) -> dict[str,Any]: ...
    def list(self,ware_id: int,actor: str) -> list[dict[str,Any]]: ...
    def capture_context(self,kind: str,document_id: int,article: str,cell: str,pallet: str,actor: str) -> dict[str,Any]: ...
    def invalidate_aggregate(self,operation_id: str,request: dict[str,Any],actor: str) -> dict[str,Any]: ...
    def aggregates(self,origin: str,ware: int,actor: str) -> list[dict[str,Any]]: ...

def trace_manifest_service() -> TraceManifestPort:
    raise RuntimeError("Trace manifest service not wired")
