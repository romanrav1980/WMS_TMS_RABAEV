from typing import Protocol

from ..domain.artmas import read_artmas10


class IdocConflict(ValueError):
    pass


class InboxStore(Protocol):
    def receive(self, envelope: dict, actor: str) -> dict: ...
    def get(self, inbox_id: str) -> dict: ...


class ArticleApply(Protocol):
    def apply(self, inbox_id: str, actor: str) -> dict: ...


class ArtmasIngestion:
    def __init__(self, inbox: InboxStore, articles: ArticleApply) -> None:
        self.inbox = inbox
        self.articles = articles

    def receive(self, raw: bytes, actor: str) -> dict:
        accepted = self.inbox.receive(read_artmas10(raw), actor)
        result = self.articles.apply(accepted["inbox_id"], actor)
        return {**result, "idempotent": accepted["idempotent"]}

    def get(self, inbox_id: str) -> dict:
        return self.inbox.get(inbox_id)
