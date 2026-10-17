"""Bounded curated publication, never an arbitrary wiki/file browser."""
import json
import re
from pathlib import Path
from ..contracts import KnowledgeArticle

class PublishedKnowledge:
    def __init__(self, catalog_path: Path) -> None:
        if catalog_path.stat().st_size > 1_000_000:
            raise ValueError("Knowledge publication exceeds size budget")
        rows = json.loads(catalog_path.read_text(encoding="utf-8-sig"))
        if not isinstance(rows, list) or len(rows) > 200:
            raise ValueError("Invalid knowledge publication")
        self._articles = tuple(self._parse(row) for row in rows)
        keys = {a.article_id for a in self._articles}
        if len(keys) != len(rows) or any(key not in keys for a in self._articles for key in a.related):
            raise ValueError("Duplicate article or broken internal reference")

    def _parse(self, row: dict[str, object]) -> KnowledgeArticle:
        for key in ("article_id", "title", "summary", "body", "revision"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError("Non-empty article text required")
        for key in ("related", "sources", "required_permissions"):
            values = row.get(key, [])
            if not isinstance(values, list) or any(not isinstance(x, str) or not x.strip() for x in values):
                raise ValueError("Article references must be strings")
        article_id = str(row["article_id"])
        if not re.fullmatch(r"[a-z][a-z0-9-]{1,79}", article_id):
            raise ValueError("Invalid article identifier")
        return KnowledgeArticle(article_id, str(row["title"]), str(row["summary"]), str(row["body"]),
                                tuple(row.get("related", [])), tuple(row.get("sources", [])),
                                str(row["revision"]), frozenset(row.get("required_permissions", [])))

    def articles(self) -> tuple[KnowledgeArticle, ...]:
        return self._articles
