"""C-0162 offline checks: scoped pool preview, current rights before replay (native kit text), execute right by current assignment.
Live READ ONLY evidence (candidate assert_access on root's 7 recorded pool operations): reports/tradecase/2026-10-23/claude/C0162/candidate-live.json."""
import hashlib
import json
import pathlib
import re
from types import SimpleNamespace
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.modules.inventory.api import pool_routes as routes
from app.modules.inventory.infrastructure import pool_service

ROOT = pathlib.Path(__file__).resolve().parents[2]
KIT = ROOT / "db/migrations/2026-10-23_trade_pool_access"
SNS, BLC = "SNS|A|200|2030-01-01", "BLC|A|250|2030-01-01"
TRADE = {"unit": "EA", "from_stock": 1, "policy_version": 3, "available": "260", "step": "1", "trade": 1,
         "classes": [{"key": SNS, "owner": "SNS", "free": "250"}, {"key": BLC, "owner": "BLC", "free": "10"}],
         "orders": [{"line_id": 1, "quantity": "20", "dispatch_order": 0, "classes": [SNS]},
                    {"line_id": 2, "quantity": "15", "dispatch_order": 1, "classes": [BLC]},
                    {"line_id": 3, "quantity": "5", "dispatch_order": 2, "classes": [SNS]}],
         "reservations": [{"id": 9, "line_id": 2, "quantity": "10"}]}


class Cur:
    """READ ONLY transaction of the preview: warehouse right, the authoritative snapshot, trade owners and owner visibility."""

    def __init__(self, snapshot, warehouse_ok=True, owners=None, visible=("SNS",)):
        self.snapshot, self.warehouse_ok, self.owners, self.visible, self.sql, self.rows = snapshot, warehouse_ok, owners or {}, set(visible), [], []

    def execute(self, sql, params=None):
        self.sql.append(sql)
        if "RRL_ACCESS_API.allowed" in sql:
            self.rows = [(1 if self.warehouse_ok else 0,)]
        elif "snapshot_json" in sql:
            self.rows = [(json.dumps(self.snapshot),)]
        elif "RRL_TRADE_ORDER_LINE" in sql:
            self.rows = [(r, *self.owners[r]) for r in params.values() if r in self.owners]
        elif "owner_allowed" in sql:
            self.rows = [(1 if params["o"] in self.visible else 0,)]

    def fetchone(self):
        return self.rows[0]

    def fetchall(self):
        return self.rows


class Gateway:
    def __init__(self, cur):
        self.cur = cur

    def transaction(self, name):
        cur = self.cur

        class Ctx:
            def __enter__(self):
                return cur

            def __exit__(self, *a):
                return False
        return Ctx()


def test_preview_requires_the_current_warehouse_right_before_reading_the_pool():
    cur = Cur(TRADE, warehouse_ok=False)
    with pytest.raises(PermissionError):
        pool_service.PoolService(Gateway(cur)).preview(210564699, "TC", "scoped")
    assert cur.sql[0] == "set transaction read only" and not any("snapshot_json" in s for s in cur.sql)


def test_trade_preview_shows_only_visible_owners_and_says_it_is_partial():
    cur = Cur(TRADE, owners={1: ("SNS", "SNS"), 2: ("BLC", "BLC"), 3: ("SNS", "SNS")})
    r = pool_service.PoolService(Gateway(cur)).preview(210564699, "TC", "scoped")
    assert [o["line_id"] for o in r["orders"]] == [1, 3] and [c["key"] for c in r["classes"]] == [SNS]
    assert set(r["allocations"]) == {"1", "3"} and r["reservations"] == [] and r["complete"] is False and r["available_quantity"] is None
    # the plan itself was computed from the whole reader-independent snapshot (BLC row 2 still took the BLC class there)
    full = pool_service.PoolService(Gateway(Cur(TRADE, owners={1: ("SNS", "SNS"), 2: ("BLC", "BLC"), 3: ("SNS", "SNS")}, visible=("SNS", "BLC")))).preview(210564699, "TC", "all")
    assert full["complete"] is True and full["allocations"] == {"1": "20", "2": "10", "3": "5"} and full["available_quantity"] == "260"


def test_non_trade_preview_is_whole_after_the_warehouse_check():
    plain = {"unit": "EA", "from_stock": 1, "policy_version": 1, "available": "10", "step": "1",
             "orders": [{"line_id": 1, "quantity": "6", "dispatch_order": 0}], "reservations": []}
    r = pool_service.PoolService(Gateway(Cur(plain))).preview(1, "X", "user")
    assert r["complete"] is True and r["orders"] == plain["orders"] and "classes" not in r


def test_route_passes_the_reader_and_maps_scope_refusal_to_403():
    seen = []

    class Service:
        def preview(self, warehouse, article, actor):
            seen.append(actor)
            if actor == "outsider":
                raise pool_service.PoolAccessError("POOL_WAREHOUSE_ACCESS_DENIED")
            return {"ok": True}
    app = FastAPI(); app.include_router(routes.router)
    app.dependency_overrides[routes.pool_service] = Service
    app.dependency_overrides[routes.pool_view] = lambda: SimpleNamespace(username="planner")
    assert TestClient(app).get("/api/inventory/soft-pools/1/X").json() == {"ok": True}
    app.dependency_overrides[routes.pool_view] = lambda: SimpleNamespace(username="outsider")
    r = TestClient(app).get("/api/inventory/soft-pools/1/X")
    assert r.status_code == 403 and r.json()["detail"] == {"code": "POOL_WAREHOUSE_ACCESS_DENIED"} and seen == ["planner", "outsider"]


def text(name):
    return (KIT / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def test_posting_api_gets_exactly_one_hook_before_the_committed_replay_branch():
    before, after = text("before_posting_api_body.sql").splitlines(), text("003_posting_api_body.sql").splitlines()
    added = [x for x in after if x not in before]
    assert len(after) == len(before) + 1 and added == ["  if g_kind='RESERVATION_ALLOCATE_POOL'then RRL_STOCK_POOL_CMD.assert_access(p_request,p_actor);end if;  -- C-0162: current rights before replay"]
    body = "\n".join(after)
    hook = body.index("RRL_STOCK_POOL_CMD.assert_access")
    assert hook < body.index("-- Immutable committed replay is considered before any mutable article/cell/UOM validation.")
    assert body.count("RRL_STOCK_POOL_CMD.assert_access") == 1


def test_pool_command_rights_and_replay_owner_check():
    spec, cmd = text("001_pool_cmd_spec.sql"), text("002_pool_cmd_body.sql")
    assert "procedure assert_access(p_request clob,p_actor varchar2);" in spec
    assert "RRL_HAS_WRIGHT" not in cmd and "RRL_ACCESS_API.allowed(p_actor,'stock_reservation_edit','WAREHOUSE',to_char(p_ware))" in cmd
    access = cmd[cmd.index(" procedure assert_access("):cmd.index(" procedure execute_command(")]
    assert access.index("require_edit(p_actor,ware);") < access.index("RESOLVED_PLAN_JSON")  # rights before anything about the stored operation
    assert "require_plan_owners(json_object_t.parse(wire).get_object('domain'),p_actor,ware)" in access
    owners = cmd[cmd.index(" procedure require_plan_owners("):cmd.index(" procedure assert_access(")]
    assert "if cls is null or src is null or src.get_size=0 then return;end if;" in owners and "assert_owner(p_actor,p_ware,c.get_string('owner'),1)" in owners
    execute = cmd[cmd.index(" procedure execute_command("):]
    assert execute.index("ware:=v.get_number('warehouse')") < execute.index("require_edit(p_actor,ware);")
    new = "\n".join(x for x in cmd.splitlines() if x not in text("before_pool_cmd_body.sql").splitlines())
    for stmt in re.findall(r"(?is)\bselect\b.*?;", new):
        assert "get_string" not in stmt and "get_object" not in stmt  # JSON object methods never inside SQL (ORA-40573)


def test_kit_hashes_and_live_evidence():
    m = json.loads(text("manifest.json"))
    assert m["status"] in ("NOT_APPLIED", "APPLIED") and m["applied_by_claude"] is False
    assert m["before_sha256"]["RRL_STOCK_POOL_CMD:PACKAGE BODY"] == "4ABD6C109C87870EF6D042B1F03D25FE7A60F64E7E58EB4A39DA1C45F4DE796F"
    for v in m["before_sha256"].values():
        assert v in text("000_preflight.sql") and v in text("rollback_verify.sql")
    for v in m["after_sha256"].values():
        assert v in text("verify.sql")
    for name, sha in m["files_sha256"].items():
        assert hashlib.sha256((KIT / name).read_bytes()).hexdigest() == sha, name
    live = json.loads((ROOT / "reports/tradecase/2026-10-23/claude/C0162/candidate-live.json").read_text(encoding="utf-8"))
    admin = [v for k, v in live.items() if k.endswith("|admin")]
    others = [v for k, v in live.items() if not k.endswith("|admin")]
    assert admin and all(v["result"] == "ALLOWED" for v in admin)
    assert others and all(v["result"].endswith("POOL_ALLOCATION_FORBIDDEN") for v in others)
