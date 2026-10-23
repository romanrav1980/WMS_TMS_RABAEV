"""C-0166 offline checks: an inventory shortage journals the exact lost units; the same physical code found again on the same lot/cell
is restored through the existing INVENTORY_COUNT writer (no second writer, no new unit). Python routing, lots read, native rules, kit."""
import hashlib
import json
import pathlib
import re
import oracledb
import pytest
from app.modules.inventory.contracts_observations import CountObservation, CountScan, CountSubmission
from app.modules.inventory.infrastructure import inventory_lot_reads, inventory_observations, inventory_scan_codes as subject

ROOT = pathlib.Path(__file__).resolve().parents[2]
KIT = ROOT / "db/migrations/2026-10-23_inventory_found_units"


class Db:
    """Answers the three reads of resolve_count_codes: scan identity, live composition, open inventory losses."""

    def __init__(self, scans, live, losses, missing_table=False):
        self.scans, self.live, self.losses, self.missing_table, self.seen = scans, live, losses, missing_table, []

    def transaction(self, name):
        db = self

        class Var:
            def setvalue(self, _, value):
                self.value = value

        class Cur:
            rows = []

            def var(self, kind):
                return Var()

            def execute(self, sql, params=None, **kw):
                db.seen.append(sql)
                if "set transaction" in sql:
                    return
                if "RRL_INVENTORY_LOSS_UNIT" in sql:
                    if db.missing_table:
                        raise oracledb.DatabaseError(type("E", (), {"code": 942})())
                    keys = json.loads(params["keys"].value)
                    self.rows = [(k, *db.losses[k]) for k in keys if k in db.losses]
                elif "RRL_SKU_RECEIPT_PROFILE" in sql:
                    batch = json.loads(params["scans"].value)
                    self.rows = [(s["index"], db.scans[s["hash"]]) for s in batch if s["hash"] in db.scans]
                else:
                    self.rows = [(0, k, q, "EA") for k, q in db.live.items()]

            def fetchall(self):
                return self.rows

            def __iter__(self):
                return iter(self.rows)

        class Ctx:
            def __enter__(self):
                return Cur()

            def __exit__(self, *a):
                return False
        return Ctx()


def line(quantity, codes):
    return CountObservation(uid="LOT1", cell="A-1", article="SKU", unit="EA", quantity=quantity, expected_stock_version=3,
                            scans=[CountScan("CRPT", "TOBACCO", c) for c in codes])


def digest(code):
    identity = subject.canonical_mark("CRPT", "TOBACCO", code)["identity"]
    return hashlib.sha256(identity.encode()).hexdigest()


CODES = ["0104600000000001215abcdefghijkl" + str(i) for i in range(3)]


@pytest.fixture
def known(monkeypatch):
    monkeypatch.setattr(subject, "canonical_mark", lambda s, p, c, *a: {"identity": c})
    return {digest(c): "K" + str(i) for i, c in enumerate(CODES)}


def test_shortage_lists_missing_keys(known):
    db = Db(known, {"K0": "1", "K1": "1", "K2": "1"}, {})
    found = []
    assert subject.resolve_count_codes(db, [line("2", CODES[:2])], found) == [["K2"]] and found == [[]]


def test_found_code_of_an_open_loss_is_routed_to_restoration(known):
    db = Db(known, {"K0": "1", "K1": "1"}, {"K2": ("1", "EA")})
    found = []
    assert subject.resolve_count_codes(db, [line("3", CODES)], found) == [[]] and found == [["K2"]]
    assert any("RRL_INVENTORY_LOSS_UNIT" in s for s in db.seen)


def test_fully_lost_lot_can_get_its_found_unit_back(known):
    db = Db(known, {}, {"K0": ("1", "EA")})
    found = []
    assert subject.resolve_count_codes(db, [line("1", CODES[:1])], found) == [[]] and found == [["K0"]]


def test_refusals(known):
    # an issued unit without an open inventory loss (shipped or issued otherwise) stays refused
    with pytest.raises(ValueError, match="no longer present"):
        subject.resolve_count_codes(Db(known, {"K0": "1"}, {}), [line("2", CODES[:2])], [])
    # found and missing on one pallet: separate counts
    with pytest.raises(ValueError, match="separate counts"):
        subject.resolve_count_codes(Db(known, {"K0": "1", "K1": "1"}, {"K2": ("1", "EA")}), [line("2", [CODES[0], CODES[2]])], [])
    # quantity must equal live present plus found
    with pytest.raises(ValueError, match="do not match"):
        subject.resolve_count_codes(Db(known, {"K0": "1"}, {"K1": ("1", "EA")}), [line("3", CODES[:2])], [])
    # without the found channel the previous refusal is unchanged
    with pytest.raises(ValueError, match="no longer present"):
        subject.resolve_count_codes(Db(known, {"K0": "1"}, {"K1": ("1", "EA")}), [line("2", CODES[:2])])
    # before the native kit is applied the journal is absent: an explicit refusal, not a 500
    with pytest.raises(ValueError, match="not installed"):
        subject.resolve_count_codes(Db(known, {"K0": "1"}, {}, missing_table=True), [line("2", CODES[:2])], [])


def test_count_command_carries_found_keys_and_replays_unchanged(known, monkeypatch):
    posted = []

    class Posting:
        def post(self, command):
            posted.append(command); return {"operation_id": command.operation_id}

    class Gw(Db):
        def fetch_all(self, sql, params):
            return []
    monkeypatch.setattr(inventory_observations, "assert_inventory_scope", lambda *a, **k: None)
    svc = inventory_observations.InventoryObservations(Gw(known, {"K0": "1", "K1": "1"}, {"K2": ("1", "EA")}), Posting())
    svc.count(CountSubmission("INV.FOUND.1", 415, "Найден код", [line("3", CODES)]), "counter")
    counts = posted[0].metadata["counts"]
    assert posted[0].command_type == "INVENTORY_COUNT" and counts[0]["found_unit_keys"] == ["K2"] and counts[0]["unit_keys"] == []
    assert "found_unit_keys" not in posted[0].metadata["requested_counts"][0]  # the operator request (replay comparison) is unchanged


def test_lots_read_shows_open_loss_codes_and_survives_before_apply():
    class Cur:
        def __init__(self, missing):
            self.missing = missing

        def execute(self, sql, params):
            if self.missing:
                raise oracledb.DatabaseError(type("E", (), {"code": 942})())
            assert "RRL_INVENTORY_FOUND_UNIT" in sql and params["cell"] == "A-1"

        def fetchall(self):
            return [("LOT1", "CODE-A"), ("LOT1", "CODE-B")]
    assert inventory_lot_reads.open_losses(Cur(False), "A-1", ["LOT1"]) == {"LOT1": ["CODE-A", "CODE-B"]}
    assert inventory_lot_reads.open_losses(Cur(True), "A-1", ["LOT1"]) == {}


def text(name):
    return (KIT / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def test_native_inventory_count_rules():
    inv = text("004_inventory_cmd_body.sql")
    assert "RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',g.get_string(q))" in inv  # found (issued) units are locked by the plan
    found = inv[inv.index("if marking!=0 and found is null"):inv.index("elsif delta<0 then")]
    order = ["INVENTORY_FOUND_AND_LOST_SEPARATELY", "INVENTORY_FOUND_WAREHOUSE_CONFLICT", "INVENTORY_FOUND_OWNER_REQUIRED",
             "RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,ware,o.OWNER_ID,1)", "RRL_STOCK_UNIT_CORE.restore_inventory_loss(",
             "insert into RRL_INVENTORY_FOUND_UNIT"]
    assert [found.index(x) for x in order] == sorted(found.index(x) for x in order)
    lost = inv[inv.index("elsif delta<0 then"):inv.index("fact:=json_object_t()")]
    order = ["json_arrayagg(PHYSICAL_UNIT_KEY", "RRL_STOCK_UNIT_CORE.issue_free_units(", "INVENTORY_LOSS_ALREADY_OPEN", "insert into RRL_INVENTORY_LOSS_UNIT"]
    assert [lost.index(x) for x in order] == sorted(lost.index(x) for x in order)
    assert "u.UNIT_VERSION,p_actor" in lost and "MARKED_INVENTORY_INCREASE_REQUIRES_CAPTURED_UNITS" in inv
    for stmt in re.findall(r"(?is)\b(?:select|insert|update)\b.*?;", inv[inv.index("C-0166"):]):
        assert not re.search(r"\b[a-z]\.get_(string|number|object|array)\(", stmt), stmt[:120]  # JSON object methods never inside SQL


def test_native_unit_restore_rules():
    spec, body = text("002_unit_core_spec.sql"), text("003_unit_core_body.sql")
    assert "procedure restore_inventory_loss(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob);" in spec
    assert text("before_unit_core_spec.sql").split("accessible by")[1].split(" as")[0] == spec.split("accessible by")[1].split(" as")[0]
    r = body[body.index(" procedure restore_inventory_loss("):body.index(" procedure reserve_units(")]
    order = ["require_context", "COMMAND_TYPE='INVENTORY_COUNT'and STATE='IN_FLIGHT'", "INVENTORY_FOUND_COMPOSITION_CONFLICT", "INVENTORY_FOUND_UNIT_NOT_IN_LOT",
             "INVENTORY_FOUND_UNIT_NOT_LOST", "INVENTORY_FOUND_LOSS_REQUIRED", "INVENTORY_FOUND_UNIT_CHANGED_SINCE_LOSS", "own_unit(k.K)",
             "INVENTORY_FOUND_QUANTITY_CONFLICT", "begin_effect('UNIT',p_uid,p_cell)", "set STOCK_STATUS='AVAILABLE'"]
    assert [r.index(x) for x in order] == sorted(r.index(x) for x in order)
    assert "RRL_TRADE_STOCK_ATTR" not in r and "insert into RRL_WMS_RECEIPT" not in r  # same unit, same owner/MRC/expiry attributes, no new unit


def test_schema_rollback_and_kit():
    s = text("001_schema.sql")
    assert "primary key(PHYSICAL_UNIT_KEY,LOSS_OPERATION_ID)" in s and s.count("RRL_STOCK_OPERATION(OPERATION_ID)") == 2
    assert "references RRL_INVENTORY_LOSS_UNIT(PHYSICAL_UNIT_KEY,LOSS_OPERATION_ID)" in s and "REVISION_ID number not null" in s
    assert "INVENTORY_LOSS_HISTORY_APPEND_ONLY" in s and "INVENTORY_FOUND_HISTORY_APPEND_ONLY" in s
    rb = text("rollback.sql")
    assert rb.index("INVENTORY_LOSS_HISTORY_PRESENT") < rb.index("@@before_unit_core_spec.sql") < rb.index("drop table")
    m = json.loads(text("manifest.json"))
    assert m["status"] in {"NOT_APPLIED", "APPLIED"} and m["applied_by_claude"] is False
    if m["status"] == "APPLIED":
        assert m.get("application_evidence") and m.get("application_result")
    for key, h in m["before_sha256"].items():
        assert h in text("000_preflight.sql") and h in text("rollback_verify.sql")
    for h in m["after_sha256"].values():
        assert h in text("verify.sql")
    for name, before in (("before_unit_core_spec.sql", "RRL_STOCK_UNIT_CORE:PACKAGE"), ("before_unit_core_body.sql", "RRL_STOCK_UNIT_CORE:PACKAGE BODY"),
                         ("before_inventory_cmd_body.sql", "RRL_STOCK_INVENTORY_CMD:PACKAGE BODY")):
        stored = text(name)[len("create or replace "):].rsplit("\n/\n", 1)[0]
        assert hashlib.sha256(stored.encode()).hexdigest().upper() == m["before_sha256"][before]
    for name, sha in m["files_sha256"].items():
        assert hashlib.sha256((KIT / name).read_bytes()).hexdigest() == sha, name
    parse = json.loads((ROOT / "reports/tradecase/2026-10-23/claude/C0166/parse-check.json").read_text(encoding="utf-8"))
    assert all(not v["syntax_error"] for v in parse.values())


def test_unchanged_pre_apply_command_replays_exactly(monkeypatch):
    """A command saved before C-0166 (no found keys anywhere) replays with its stored metadata; requested_counts keep the old shape."""
    req = CountSubmission("INV.OLD.1", 415, "Старый пересчёт", [line("2", [])])
    old_meta = {"reason": req.reason, "counts": [{**req.counts[0].wire(False), "unit_keys": ["K2"]}], "requested_counts": [req.counts[0].wire()]}
    assert set(old_meta["requested_counts"][0]) == {"uid", "cell", "article", "unit", "quantity", "expected_stock_version", "scans", "unit_keys"}
    posted = []

    class Posting:
        def post(self, command):
            posted.append(command); return {"operation_id": command.operation_id}

    class Gw:
        def fetch_all(self, sql, params):
            return [{"canonical_request": json.dumps({"command_type": "INVENTORY_COUNT", "source": {"revision_id": 415}, "metadata": old_meta})}]
    monkeypatch.setattr(inventory_observations, "assert_inventory_scope", lambda *a, **k: None)
    inventory_observations.InventoryObservations(Gw(), Posting()).count(req, "counter")
    assert posted[0].metadata == old_meta  # no re-resolution, no new field: the same bytes reach the coordinator
    changed = CountSubmission("INV.OLD.1", 415, "Другая причина", req.counts)
    with pytest.raises(inventory_observations.InventoryObservationError):
        inventory_observations.InventoryObservations(Gw(), Posting()).count(changed, "counter")
