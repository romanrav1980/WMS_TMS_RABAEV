"""C-0147: set-based ReceivingMarks.persist keeps the effects and errors of the per-unit version on the exact
1000-EA body of operation T3.receive.505b15a0, with a bounded number of round trips. No Oracle: recording cursor."""
import json
import pathlib
import pytest
from app.modules.inventory.infrastructure import receiving_marks as new_module

ROOT = pathlib.Path(__file__).resolve().parents[2]
GTIN, TAG, PALLET = "29013481465928", "505b15a0", "690000000481465926"


def _old_module():
    source = (ROOT / "reports/tradecase/2026-10-22/claude/C0147/scripts/receiving_marks_before.py").read_text(encoding="utf-8")
    module = type(new_module)("receiving_marks_before")
    module.__dict__["__package__"] = new_module.__package__
    exec(compile(source, "receiving_marks_before.py", "exec"), module.__dict__)
    return module


class Recorder:
    """Records the database effects persist() asks for; answers lookups from a tiny scripted state."""
    def __init__(self, legacy=(), received=(), gtin=GTIN):
        self.legacy, self.received, self.gtin = set(legacy), set(received), gtin
        self.trips, self.units, self.codes, self.crpt, self.aggregation, self.journal, self.last = 0, [], [], [], [], [], None

    def setinputsizes(self, **kw):
        pass

    def execute(self, sql, params=None, **kw):
        self.trips += 1; p = dict(params or {}, **kw); s = " ".join(sql.split()); self.last = (s, p)
        if s.startswith("insert into RRL_WMS_RECEIPT_UNIT"): self.units.append(tuple(sorted(p.items())))
        elif s.startswith("insert into RRL_WMS_RECEIPT_CODE"): self.codes.append(tuple(sorted(p.items())))
        elif s.startswith("declare v number;begin"):
            for c in json.loads(p["codes"]):
                self.crpt.append((None, p["p"], c["gtin"], c["cis"], c["serial"], c["raw"], p["sscc"]))
                if p["parent"] is not None: self.aggregation.append((p["parent"], "CIS", c["cis"], None, c["gtin"], None))

    def executemany(self, sql, rows):
        self.trips += 1; s = " ".join(sql.split())
        target = self.units if s.startswith("insert into RRL_WMS_RECEIPT_UNIT") else self.codes
        target.extend(tuple(sorted(r.items())) for r in rows)

    def fetchone(self):
        s, p = self.last
        if "nvl(f.GTIN,a.BARCODE_SHT)" in s: return (self.gtin,)
        if "from RRL_CRPT_CODES c join json_table" in s: return (len(self.legacy & set(json.loads(p["codes"]))),)
        if "from RRL_CRPT_CODES c where c.CIS=" in s: return (1 if p["code"] in self.legacy else 0,)
        if "from RRL_WMS_RECEIPT_CODE r join json_table" in s: return (len(self.received & set(json.loads(p["hashes"]))),)
        if "from RRL_WMS_RECEIPT_CODE where SYSTEM_CODE=" in s: return ("X",) if p["h"] in self.received else None
        raise AssertionError(s)

    def callfunc(self, name, kind, args=None, keywordParameters=None):
        self.trips += 1
        if name == "RRL_PRODUCTION_API.ADD_CRPT_CODE": self.crpt.append(tuple(args))
        else: self.journal.append((name, tuple(sorted((keywordParameters or {}).items()))))
        return 1

    def callproc(self, name, args):
        self.trips += 1; self.aggregation.append(tuple(args))

    def effects(self):
        return dict(units=self.units, codes=self.codes, crpt=self.crpt, aggregation=self.aggregation, journal=self.journal)


def _marks(n=1000, extra_code=None):
    profile = ("CRPT", "TOBACCO")
    units = {str(i): {profile: GTIN + TAG[:3] + str(i).zfill(4)} for i in range(1, n + 1)}
    if extra_code:
        units[str(n + 1)] = {profile: extra_code}
    q = {u: new_module.Decimal(1) for u in units}
    return {"policy_version": 3, "profiles": {profile: {"version": 1, "mode": "UNIT"}}, "units": units, "unit_quantities": q, "scanned": []}


def _bindings(marks):
    return [{"unit_id": u, "key": f"k{u:0>64}"[:64], "quantity": "1"} for u in marks["units"]]


def _run(module, cur, marks, bindings, monkeypatch):
    monkeypatch.setattr(module, "create_receipt_parent", lambda c, p, s: (77, "SSCC77"))
    monkeypatch.setattr(module, "assert_current_mark_policy", lambda *a: None)
    monkeypatch.setattr(module, "persist_scanned_aggregates", lambda *a: None)
    module.ReceivingMarks(cur).persist(PALLET, marks, "admin", bindings=bindings, base_uom="EA", cell="T3R505b15a0")


@pytest.mark.parametrize("with_bindings", [True, False])
def test_same_effects_on_exact_1000_unit_body_with_bounded_round_trips(monkeypatch, with_bindings):
    marks = _marks(); bindings = _bindings(marks) if with_bindings else None
    old, new = Recorder(), Recorder()
    _run(_old_module(), old, marks, bindings, monkeypatch); _run(new_module, new, marks, bindings, monkeypatch)
    assert new.effects() == old.effects()
    assert len(new.units) == len(new.codes) == len(new.crpt) == len(new.aggregation) == 1000
    assert old.trips == 6002 and new.trips <= 8, (old.trips, new.trips)


@pytest.mark.parametrize("state,message", [
    (dict(legacy="LEGACY"), "legacy CRPT registry"),
    (dict(received="RECEIVED"), "already been received"),
    (dict(gtin="04600000000001"), "GTIN does not match"),
])
def test_same_refusals(monkeypatch, state, message):
    marks = _marks(50)
    cis = [new_module.canonical_mark("CRPT", "TOBACCO", c[("CRPT", "TOBACCO")], GTIN)["identity"] for c in marks["units"].values()]
    digest = new_module.sha256(cis[17].encode()).hexdigest()
    kw = {"legacy": {cis[17]}} if "legacy" in state else {"received": {digest}} if "received" in state else {"gtin": state["gtin"]}
    for module in (_old_module(), new_module):
        with pytest.raises(ValueError, match=message):
            _run(module, Recorder(**kw), marks, _bindings(marks), monkeypatch)


def test_one_code_for_two_units_is_refused_before_any_write(monkeypatch):
    marks = _marks(10, extra_code=GTIN + TAG[:3] + "0003")
    cur = Recorder()
    with pytest.raises(ValueError, match="different physical units"):
        _run(new_module, cur, marks, _bindings(marks), monkeypatch)
    assert cur.units == [] and cur.codes == [] and cur.crpt == []


def test_no_marked_units_does_no_set_queries(monkeypatch):
    marks = {"policy_version": 3, "profiles": {}, "units": {}, "unit_quantities": {}, "scanned": []}
    cur = Recorder()
    _run(new_module, cur, marks, [], monkeypatch)
    assert cur.trips == 0 and cur.effects() == dict(units=[], codes=[], crpt=[], aggregation=[], journal=[])
