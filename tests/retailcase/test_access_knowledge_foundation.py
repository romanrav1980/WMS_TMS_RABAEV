"""Access contracts and publication visibility; no live business/Oracle acceptance claim."""
from dataclasses import replace
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.knowledge_composition import register_knowledge
from app.config import get_settings
from app.modules.platform.public import KnowledgeService, PublishedKnowledge, knowledge_user
from app.modules.platform.contracts import AccessScope, RoleAssignment, KnowledgeArticle

NOW = datetime(2026, 10, 14, tzinfo=timezone.utc)


def assignment(**changes):
    values = dict(assignment_id="a1", username="u1", role_id="dispatcher", scope=AccessScope("GROUP", "north"),
                  valid_from=NOW, valid_until=NOW + timedelta(days=1), assigned_by="admin", reason="shift")
    return RoleAssignment(**(values | changes))


def test_assignment_keeps_role_scope_and_author_together():
    a = assignment()
    b = assignment(assignment_id="a2", role_id="auditor", scope=AccessScope("NETWORK"))
    assert a.scope.object_id == "north" and b.scope.kind == "NETWORK"
    assert a.role_id == "dispatcher" and a.assigned_by == "admin"


@pytest.mark.parametrize("changes", [dict(valid_from=NOW.replace(tzinfo=None)), dict(valid_until=NOW),
                                       dict(valid_until=NOW-timedelta(seconds=1)), dict(reason=" "), dict(version=True)])
def test_reject_invalid_assignment(changes):
    with pytest.raises(ValueError):
        assignment(**changes)


@pytest.mark.parametrize("args", [("GROUP",), ("NETWORK", "warehouse-1"), ("SELF", "user-supplied"),
                                  ("GROUP", "north", "SNAPSHOT", None), ("STORE", "1", "SNAPSHOT", 2),
                                  ("GROUP", "north", "CURRENT", 2), ("GROUP", "north", "SNAPSHOT", True)])
def test_scope_not_ambiguous(args):
    with pytest.raises(ValueError):
        AccessScope(*args)


def test_group_snapshot_is_explicit():
    assert AccessScope("GROUP", "north", "SNAPSHOT", 7).snapshot_version == 7


class Reader:
    def articles(self):
        return (KnowledgeArticle("public", "Public", "Summary", "Normal text", ("secret",), (), "1"),
                KnowledgeArticle("secret", "Secret", "Protected", "needle", (), (), "1", frozenset({"audit"})))


def test_filter_before_search_and_related_links():
    service = KnowledgeService(Reader())
    assert service.search("needle", set(), 20) == []
    assert service.detail("secret", set()) is None
    assert service.detail("public", set())["related"] == []
    assert service.detail("public", {"audit"})["related"] == [{"article_id": "secret", "title": "Secret"}]
    assert service.detail("secret", {"*"}) is not None


def test_api_auth_bounds_and_no_filesystem_route():
    app = FastAPI()
    app.dependency_overrides[get_settings] = lambda: replace(get_settings(), admin_auth_enabled=True)
    register_knowledge(app)
    with TestClient(app) as client:
        assert client.get("/api/help/articles").status_code == 401
        class User:
            permissions = set()
        app.dependency_overrides[knowledge_user] = User
        assert {row["article_id"] for row in client.get("/api/help/articles").json()} == {
            "using-help", "access-model", "operation-recovery", "consolidation-plan"}
        assert client.get("/api/help/articles?query=" + "a"*121).status_code == 422
        assert client.get("/api/help/articles?limit=51").status_code == 422
        assert client.get("/api/help/articles/unknown").status_code == 404
        assert client.get("/api/help/articles/using-help").json()["revision"] == "2026-10-16/2"


def test_publication_rejects_duplicate_or_broken_links(tmp_path):
    row = dict(article_id="one", title="One", summary="Summary", body="Body", sources=[], revision="1", related=["missing"])
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps([row]), encoding="utf-8")
    with pytest.raises(ValueError):
        PublishedKnowledge(path)
    row["related"] = []
    path.write_text(json.dumps([row,row]), encoding="utf-8")
    with pytest.raises(ValueError):
        PublishedKnowledge(path)


def test_assignment_payload_canonicalizes_equivalent_timezone_instants():
    from app.modules.platform.api.metadata_inputs import Command, normalize
    payload=dict(assignment_id="time",username="u1",role_id="dispatcher",scope_kind="WAREHOUSE",scope_id="1",
                 valid_from="2026-10-15T03:00:00+03:00",valid_until="2026-10-15T04:00:00+03:00",reason="shift",expected_version=0)
    first=normalize(Command(operation_id="time1",command_type="ASSIGN",payload=payload),"ACCESS")
    second=normalize(Command(operation_id="time1",command_type="ASSIGN",payload=payload|{
        "valid_from":"2026-10-15T00:00:00Z","valid_until":"2026-10-15T01:00:00Z"}),"ACCESS")
    assert first==second
    assert first["payload"]["valid_from"]=="2026-10-15T00:00:00.000000+00:00"
