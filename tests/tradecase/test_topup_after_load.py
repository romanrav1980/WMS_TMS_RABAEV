"""C-0161 offline checks: top-up while main cargo is loaded (counted once, packaging excess only), refusals on facts, and the NOT_APPLIED kit.
Live READ ONLY evidence (5 real departed trade trips): reports/tradecase/2026-10-23/claude/C0161/candidate-live.json."""
import hashlib
import json
import pathlib
from datetime import datetime, timedelta, timezone
from decimal import Decimal as D
import pytest
from app.modules.integrations.contracts_trade_transport import TradeTransportError
from app.modules.integrations.infrastructure.trade_capacity import _loaded, after_load_admission

ROOT = pathlib.Path(__file__).resolve().parents[2]
KIT = ROOT / "db/migrations/2026-10-23_topup_after_load"
# One box: 10 EA, 5 kg, 0.02 m3 (0.2 x 0.2 x 0.5); the plan has 60 boxes for recipient C1.
PKG = dict(sku_id="A", sku_version=1, units_per_box=10, weight=D(5), volume=D("0.02"), dimensions=(D("0.2"), D("0.2"), D("0.5")), article="ART-A")
PLAN = [dict(PKG, boxes=D(60), recipient_id="C1")]
TRIP = {"vehicle_id": "TP22.089ddb36", "planned_departure_at": "2026-10-23T12:00:00+00:00"}


def fact(op, units, gross, volume, status="LOADED", vehicle="TP22.089DDB36", article="ART-A", uom="EA"):
    return (op, status, vehicle, gross, volume, json.dumps({"nodes": [{"kind": "CONTAINER"}, {"kind": "STOCK", "article": article, "quantity": str(units), "base_uom": uom}]}))


class Cur:
    def __init__(self, link=(33665, "TP22.089DDB36"), facts=()):
        self.link, self.facts, self.rows = link, list(facts), []

    def execute(self, sql, **binds):
        self.rows = [self.link] if "RRL_TRADE_TRIP_LINK" in sql else self.facts if "RRL_TT_HU_LOAD_FACT" in sql else []

    def fetchone(self):
        return self.rows[0] if self.rows and self.rows[0] is not None else None

    def fetchall(self):
        return self.rows


def test_loaded_main_cargo_is_counted_once_only_packaging_excess_added():
    # 20 boxes loaded on one pallet: theory 100 kg / 0.4 m3, fact 125 kg / 0.9 m3 (pallet + air) -> excess 25 kg / 0.5 m3, no second 100 kg.
    r = _loaded(Cur(facts=[fact("L1", 200, 125, D("0.9"))]), 1, "T", TRIP, PLAN)
    assert (r["overhead_kg"], r["overhead_m3"], r["places"], r["loaded_units"]) == (D(25), D("0.5"), 1, {"ART-A": "200"})
    lighter = _loaded(Cur(facts=[fact("L1", 200, 90, D("0.3"))]), 1, "T", TRIP, PLAN)
    assert (lighter["overhead_kg"], lighter["overhead_m3"]) == (D(0), D(0))  # a lighter fact never frees planned space


def test_nothing_loaded_or_no_binding_is_the_ordinary_path():
    assert _loaded(Cur(link=None), 1, "T", TRIP, PLAN) is None
    assert _loaded(Cur(facts=[]), 1, "T", TRIP, PLAN) is None  # UNLOADED facts are not selected: an unloaded place frees its packaging


@pytest.mark.parametrize("facts,link,code", [
    ([fact("L1", 200, 125, D("0.9"), status="DEPARTED")], (33665, "TP22.089DDB36"), "TOPUP_TRIP_DEPARTED"),
    ([fact("L1", 200, 125, D("0.9"), vehicle="OTHER")], (33665, "TP22.089DDB36"), "TOPUP_AFTER_LOAD_VEHICLE_MISMATCH"),
    ([fact("L1", 200, 125, D("0.9"))], (33665, "OTHER"), "TOPUP_AFTER_LOAD_VEHICLE_MISMATCH"),
    ([fact("L1", 200, None, D("0.9"))], (33665, "TP22.089DDB36"), "TOPUP_AFTER_LOAD_FACT_MEASURE_REQUIRED"),
    ([fact("L1", 200, 125, D("0.9"), article="OTHER")], (33665, "TP22.089DDB36"), "TOPUP_AFTER_LOAD_UNPLANNED_GOODS"),
    ([fact("L1", 700, 400, D("2"))], (33665, "TP22.089DDB36"), "TOPUP_AFTER_LOAD_UNPLANNED_GOODS"),  # more than the 600 EA planned
    ([fact("L1", 200, 125, D("0.9"), uom="KG")], (33665, "TP22.089DDB36"), "TOPUP_AFTER_LOAD_BASE_UOM_UNSUPPORTED"),
])
def test_facts_that_cannot_be_counted_once_are_refused(facts, link, code):
    with pytest.raises(TradeTransportError) as err:
        _loaded(Cur(link=link, facts=facts), 1, "T", TRIP, PLAN)
    assert err.value.code == code


def test_admission_departure_route_and_recipient():
    now = datetime(2026, 10, 23, 10, 0, tzinfo=timezone.utc)
    loaded = {"recipients": ["C1"]}
    ctx = {"started": True, "trip": TRIP, "loaded": loaded}
    assert after_load_admission({"started": False}, "C9", now) is None  # before loading: unchanged path
    assert after_load_admission(ctx, "C1", now) is None
    assert after_load_admission(ctx, "C2", now) == "TOPUP_AFTER_LOAD_RECIPIENT_NOT_ON_TRIP"
    assert after_load_admission({**ctx, "loaded": {"recipients": ["C1", "C2"]}}, "C1", now) == "TOPUP_AFTER_LOAD_ROUTE_ORDER_UNVERIFIED"
    assert after_load_admission(ctx, "C1", now + timedelta(hours=2)) == "TOPUP_DEPARTURE_TIME_PASSED"


def text(name):
    return (KIT / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def test_kit_gates_basis_and_lock_order():
    read, api, cmd = text("002_read_body.sql"), text("003_api_body.sql"), text("004_cmd_body.sql")
    assert "acc:=acc||'|L:'||f.LOAD_OPERATION_ID||':'||f.STATUS||':'||f.CONTENT_VERSION;" in read and "acc:=acc||'|T:'||t.NATIVE_TASK_ID||':'||t.TRANSPORT;" in read
    assert "f.STATUS='DEPARTED'" in read and "o.COMMAND_TYPE='TRIP_DEPART'" in read
    for body in (api, cmd):
        assert "loading_started" not in body and "TOPUP_TRIP_DEPARTED" in body
    plan = cmd[cmd.index("procedure common_plan("):cmd.index("procedure compile_command(")]
    assert "row_key(r,'RRL_TRANSPORT_TASK'" in plan and "RRL_TRADE_TRIP_LINK" in plan
    confirm = cmd[cmd.index("procedure confirm("):cmd.index("procedure release(")]
    assert confirm.index("RRL_TRADE_TOPUP_READ.departed") < confirm.index("trip_basis(")  # departure first, then the basis with load facts
    save = api[api.index("procedure save("):]
    assert save.index("if replay(op,hash_value,ware,p_result)then return;end if;") < save.index("RRL_TRADE_TOPUP_READ.departed")  # exact replay first
    assert "function departed(p_ware number,p_trip varchar2)return number;" in text("001_read_spec.sql")


def test_kit_hashes_and_live_evidence():
    m = json.loads(text("manifest.json"))
    assert m["status"] == "NOT_APPLIED" and m["applied_by_claude"] is False
    for v in m["before_sha256"].values():
        assert v in text("000_preflight.sql") and v in text("rollback_verify.sql")
    for v in m["after_sha256"].values():
        assert v in text("verify.sql")
    for name, sha in m["files_sha256"].items():
        assert hashlib.sha256((KIT / name).read_bytes()).hexdigest() == sha, name
    live = json.loads((ROOT / "reports/tradecase/2026-10-23/claude/C0161/candidate-live.json").read_text(encoding="utf-8"))
    assert live and all(v["departed"] == 1 and v["python"] != "COMPUTED" and v["basis"] != v["live_basis"] for v in live.values())
