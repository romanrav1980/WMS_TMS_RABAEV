"""Photo evidence precedes receipt and never conducts warehouse quantity."""
from dataclasses import dataclass
from typing import Any,Protocol


@dataclass(frozen=True)
class ArchivedPhoto:
    contents: bytes
    mime_type: str
    sha256: str


class StoreEvidencePort(Protocol):
    def upload(self, load_operation_id: str, store_address: str, view: str, mime_type: str, contents: bytes, actor: str) -> dict[str,Any]: ...
    def photos(self, load_operation_id: str, store_address: str, actor: str) -> list[dict[str,Any]]: ...
    def content(self, photo_id: str, actor: str) -> ArchivedPhoto: ...


def store_evidence_service() -> StoreEvidencePort:
    raise RuntimeError("Store evidence service not wired")
