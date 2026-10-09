from typing import Protocol

from ..contracts import ReceiptPolicyUpdate


class PolicyConflict(ValueError):
    pass


class PolicyStore(Protocol):
    def get(self, articul: str) -> dict: ...
    def replace(self, articul: str, request: ReceiptPolicyUpdate, actor: str) -> dict: ...


class ReceiptPolicyService:
    def __init__(self, store: PolicyStore) -> None:
        self.store = store

    def get(self, articul: str) -> dict:
        return self.store.get(articul)

    def replace(self, articul: str, request: ReceiptPolicyUpdate, actor: str) -> dict:
        return self.store.replace(articul, request, actor)
