"""Read only published knowledge; filter visibility before search and related links."""
from ..contracts import KnowledgeArticle, KnowledgeReader

class KnowledgeService:
    def __init__(self, reader: KnowledgeReader) -> None:
        self.reader = reader

    def visible(self, permissions: set[str]) -> tuple[KnowledgeArticle, ...]:
        return tuple(article for article in self.reader.articles()
                     if "*" in permissions or article.required_permissions.issubset(permissions))

    def search(self, query: str, permissions: set[str], limit: int) -> list[dict[str, str]]:
        words = query.casefold().split()
        return [{"article_id": a.article_id, "title": a.title, "summary": a.summary}
                for a in self.visible(permissions)
                if all(w in (a.title + " " + a.summary + " " + a.body).casefold() for w in words)][:limit]

    def detail(self, article_id: str, permissions: set[str]) -> dict[str, object] | None:
        visible = {a.article_id: a for a in self.visible(permissions)}
        article = visible.get(article_id)
        if article is None:
            return None
        return {"article_id": article.article_id, "title": article.title, "summary": article.summary,
                "body": article.body, "revision": article.revision, "sources": article.sources,
                "related": [{"article_id": key, "title": visible[key].title}
                            for key in article.related if key in visible]}
