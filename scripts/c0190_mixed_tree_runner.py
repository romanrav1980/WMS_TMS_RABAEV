"""C-0190 T06 mixed-tree live acceptance runner (root executes; Claude never runs it).

One isolated warehouse/recipient, two CASE tasks: (a) a KG line picked by manual NET through /weigh-line-manual (C0188/C0189,
no synthetic scale capture) and (b) an EA line picked through the regular /confirm. One parent PALLET HU receives both CASE
carriers through /api/warehouse-hus/attach-case. Checked: the parent composition (each CASE and physical STOCK leaf once, SSCC,
quantities), refusals (stale parent version, foreign carrier scan, other cell, changed body under the same operation) and exact
replays with no second stock event.

Modes: plan (default; no network, no Oracle) | preflight (read only) | run | cleanup. Every write step is journaled before it is
sent; a repeat sends identical bytes; an unknown outcome (5xx/network) blocks every later step until the same step is repeated.
Fixture rows follow scripts/ni042_warehouse_scale_net_case.py under RRL_STOCK_CONFIG_API.begin_change on a new, empty, tagged
warehouse; shared physical stock is never seeded or changed. Control/LOAD/DEPART and the store receipt need the transport fixture
of tests/tradecase/live_nested_shipping.py: the runner stops after TREE/NEGATIVES with TRANSPORT_NOT_WIRED instead of inventing it.
Any unexpected native answer stops the run with the exact code; nothing after it is attempted.
"""
from __future__ import annotations

import argparse
import json
import re
import secrets
import sys
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "runtime/test-evidence/tradecase/2026-10-28/T06/mixed-tree"
MANUAL_ROUTE = "/api/case-pick/tasks/{task}/lines/{line}/weigh-line-manual"
PROTECTED_WAREHOUSES = {225837931, 210069361, 213059748, 225687965, 210564699, 223214750, 225290508}
STAGES = ("FIXTURE", "WAVE", "PICK_KG_MANUAL_NET", "PICK_EA", "TREE", "TRANSPORT")
EA_QTY = "4"


class RunnerStop(RuntimeError):
    """A fail-closed stop: the reason names the exact blocker; nothing after it is attempted."""


# ---------------------------------------------------------------- pure, offline-tested parts

def preflight_findings(snap: dict[str, Any]) -> list[str]:
    """Refusal codes from a read-only snapshot; an empty list means the run may start."""
    out = []
    if not snap.get("api_ready"):
        out.append("API_READY_MISSING")
    if MANUAL_ROUTE not in snap.get("openapi_paths", ()):
        out.append("MANUAL_NET_ROUTE_MISSING")
    if not snap.get("weighted_kg_field"):
        out.append("MARKING_POLICY_WEIGHTED_KG_MISSING")
    if snap.get("tag_rows", 0):
        out.append("FIXTURE_TAG_COLLISION")
    if snap.get("warehouse") in PROTECTED_WAREHOUSES:
        out.append("PROTECTED_WAREHOUSE")
    if snap.get("warehouse_exists") or snap.get("warehouse_stock_rows", 0) or snap.get("warehouse_case_tasks", 0) or snap.get("warehouse_waves", 0):
        out.append("WAREHOUSE_NOT_EMPTY")
    if not snap.get("template_article"):
        out.append("TEMPLATE_ARTICLE_MISSING")
    for name in ("parent_tare_kg", "manual_net_kg"):  # operator measurements; never invented
        if not _positive(snap.get(name)):
            out.append(name.upper() + "_REQUIRED")
    return out


def _positive(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9]{1,18}(\.[0-9]{1,9})?", value)) and Decimal(value) > 0


def manual_net_body(operation: str, net_kg: str, cell: str, carrier: str) -> dict[str, Any]:
    """C0188 contract: no fact_qty, no warehouse_scale_capture; the server derives the cumulative fact."""
    if not _positive(net_kg):
        raise RunnerStop("MANUAL_NET_VALUE_INVALID")
    return {"operation_id": operation, "net_weight_kg": net_kg, "scan_cell": cell, "scan_container": carrier, "unit_scans": []}


def ea_confirm_body(operation: str, fact_qty: str, cell: str, article: str, carrier: str) -> dict[str, Any]:
    return {"operation_id": operation, "fact_qty": fact_qty, "scan_cell": cell, "scan_product": article, "scan_container": carrier, "unit_scans": []}


def attach_case_body(operation: str, parent: str, case: int, parent_version: int, child_version: int, carrier: str, booking: str | None) -> dict[str, Any]:
    body = {"operation_id": operation, "identifier": parent, "child_case_task_id": case, "expected_version": parent_version,
            "expected_child_version": child_version, "scan_container": parent, "scan_child": carrier}
    if booking:
        body["retained_tare_booking_operation_id"] = booking
    return body


@dataclass
class Journal:
    """Write steps keyed by name: stored before sending, replayed byte-for-byte, an unknown outcome blocks the rest."""
    steps: dict[str, dict[str, Any]] = field(default_factory=dict)
    results: dict[str, Any] = field(default_factory=dict)
    unknown: str | None = None

    def record(self, key: str, method: str, path: str, body: Any) -> str:
        wire = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        old = self.steps.get(key)
        if old and (old["method"], old["path"], old["wire"]) != (method, path, wire):
            raise RunnerStop(f"STEP_CONTENT_CHANGED:{key}")
        if self.unknown and self.unknown != key:
            raise RunnerStop(f"UNKNOWN_OUTCOME_PENDING:{self.unknown}")
        self.steps.setdefault(key, {"method": method, "path": path, "wire": wire})
        return self.steps[key]["wire"]

    def outcome(self, key: str, status: int, value: Any) -> Any:
        if status == 0 or status >= 500:
            self.unknown = key
            raise RunnerStop(f"UNKNOWN_OUTCOME:{key}:HTTP{status}")
        if self.unknown == key:
            self.unknown = None
        self.results[key] = {"status": status, "value": value}
        return value

    def to_json(self) -> dict[str, Any]:
        return {"steps": self.steps, "results": self.results, "unknown": self.unknown}

    @classmethod
    def from_json(cls, data: dict[str, Any] | None) -> "Journal":
        data = data or {}
        return cls(dict(data.get("steps", {})), dict(data.get("results", {})), data.get("unknown"))


def tree_findings(composition: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    """Each expected child CASE once, each physical STOCK leaf once, quantities equal to the picks, no quantity on containers."""
    nodes = composition.get("nodes", [])
    out = []
    cases = [n for n in nodes if n.get("kind") == "CASE"]
    if sorted(str(n.get("case_task_id")) for n in cases) != sorted(str(x) for x in expected["case_tasks"]):
        out.append("CASE_CHILDREN_MISMATCH")
    leaves = [n for n in nodes if n.get("kind") == "STOCK"]
    keys = [n.get("uid") for n in leaves]
    if len(keys) != len(set(keys)):
        out.append("STOCK_LEAF_COUNTED_TWICE")
    by_article: dict[str, Decimal] = {}
    for n in leaves:
        by_article[n.get("article")] = by_article.get(n.get("article"), Decimal(0)) + Decimal(str(n.get("quantity", "0")))
    if {k: v.normalize() for k, v in by_article.items()} != {k: Decimal(v).normalize() for k, v in expected["quantities"].items()}:
        out.append("QUANTITY_MISMATCH")
    if any(n.get("kind") == "CONTAINER" and Decimal(str(n.get("quantity") or 0)) != 0 for n in nodes):
        out.append("CONTAINER_HOLDS_QUANTITY")
    sscc = {str(n.get("case_task_id")): n.get("sscc") for n in cases}
    if any(sscc.get(str(t)) != s for t, s in expected["carriers"].items()):
        out.append("CHILD_SSCC_CHANGED")
    if any(n.get("cell") != expected["cell"] for n in nodes if n.get("kind") in ("CONTAINER", "CASE")):
        out.append("TREE_CELL_MISMATCH")
    return out


# K-0217: each refusal must be the expected native rule, not any 403/409 (an unrelated denial must not look green).
EXPECTED_REFUSALS = {
    "stale_parent_version": "HU_CONTENT_VERSION_CONFLICT",
    "foreign_carrier_scan": "HU_CASE_CARRIER_SCAN_REQUIRED",
    "changed_body_same_operation": "OPERATION_CONTENT_CONFLICT",
    "other_cell": "HU_PACK_SAME_LOCATION_REQUIRED",
}
UNCERTAIN_CODES = {"RESULT_UNCERTAIN", "REQUEST_DEADLINE", "LOCK_RETRY_EXHAUSTED", "CONNECTION_UNUSABLE", "STOCK_RELEASE_NOT_ACTIVE",
                   "POSTED_CONNECTION_RESET_FAILED"}


def refusal_matches(value: Any, expected: str) -> bool:
    """The API puts the native rule either in detail.code or in detail.reason (HU routes: code + rule_reason)."""
    detail = value.get("detail", {}) if isinstance(value, dict) else {}
    if not isinstance(detail, dict):
        return False
    return any(isinstance(detail.get(k), str) and detail[k].split(":")[0].strip() == expected for k in ("code", "reason"))


def check_refusal(name: str, value: Any, before: dict[str, Any], after: dict[str, Any]) -> None:
    if not refusal_matches(value, EXPECTED_REFUSALS[name]):
        raise RunnerStop(f"UNEXPECTED_REFUSAL:{name}:{str(value)[:300]}")
    if after != before:
        raise RunnerStop(f"REFUSAL_CHANGED_PARENT_COMPOSITION:{name}")


def native_status(error: BaseException | None) -> int:
    """200 posted; 409 confirmed native refusal; 0 unknown outcome (must be repeated with the same bytes)."""
    if error is None:
        return 200
    code, oracle = getattr(error, "code", None), getattr(error, "oracle_code", None)
    if code is not None and code not in UNCERTAIN_CODES and oracle not in (20891, 20892, 20893):
        return 409
    return 0


def cleanup_scope_findings(rows: list[tuple], reservations: int, foreign_tasks: int, allowed_uids: set[str], expected: dict[str, str]) -> list[str]:
    """K-0217: INVENTORY_COUNT may zero only this run's own lots (registered lots and its CASE carrier lots) with the exact expected
    remainder per article; anything else on the warehouse stops cleanup before the count."""
    out = []
    totals: dict[str, Decimal] = {}
    for uid, cell, article, unit, version, quantity in rows:
        if uid not in allowed_uids:
            out.append(f"FOREIGN_UID:{uid}")
        if article not in expected:
            out.append(f"FOREIGN_ARTICLE:{article}")
        totals[article] = totals.get(article, Decimal(0)) + Decimal(str(quantity))
    for article, qty in expected.items():
        if totals.get(article, Decimal(0)) != Decimal(qty):
            out.append(f"REMAINDER_MISMATCH:{article}:{totals.get(article, Decimal(0))}!={qty}")
    if reservations:
        out.append(f"ACTIVE_RESERVATIONS:{reservations}")
    if foreign_tasks:
        out.append(f"FOREIGN_OPEN_TASKS:{foreign_tasks}")
    return out


def cleanup_plan(state: dict[str, Any]) -> list[str]:
    """Ordered native reversals for exactly what this run created; journals and history are kept."""
    plan = [f"HU_DETACH_CASE:{t}" for t in state.get("tree_attached", [])]
    tasks = state.get("case_tasks") or [c["task"] for c in state.get("cases", {}).values()]
    plan += [f"CASE_CARRIER_RETURN:{t}" for t in tasks]
    if state.get("wave"):
        plan.append("RESERVATION_RELEASE:wave")
    for t in state.get("tare_bookings", []):
        plan.append(f"TARE_BOOK_CANCEL:{t}")
    if state.get("tare_bookings"):
        plan.append("TARE_COUNT_ZERO")
    if state.get("wave"):
        plan.append("WAVE_EXECUTION_FINISH_OR_CANCEL")
    if state.get("lots"):
        plan.append("INVENTORY_COUNT_ZERO")
    plan.append("ASSERT_WAREHOUSE_ZERO_STOCK_AND_RESERVATION")
    return plan


# ---------------------------------------------------------------- live parts (root executes)

def _password() -> str:
    return re.search(r"PASS=(\S+?)[`,)\s]", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))[1]


class Live:
    def __init__(self, api: str, state_file: Path):
        sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "api/wms_api_server")]
        from stock_posting_environment import load_local_oracle_environment
        load_local_oracle_environment()
        import httpx
        from tools.mcp.tms_mcp_server import oracle_connection
        self.api, self.file, self.connect = api.rstrip("/"), state_file, oracle_connection
        self.http = httpx.Client(auth=("admin", _password()), timeout=60)
        self.s = json.loads(state_file.read_text(encoding="utf-8")) if state_file.exists() else {"tag": "MT28" + uuid4().hex[:9].upper(), "posts": {}}
        self.journal = Journal.from_json(self.s.get("journal"))

    def save(self) -> None:
        self.s["journal"] = self.journal.to_json()
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.write_text(json.dumps(self.s, indent=1, ensure_ascii=False, default=str), encoding="utf-8")

    def read(self, sql: str, **binds: Any) -> list[tuple]:
        with self.connect() as c:
            q = c.cursor(); q.execute("set transaction read only"); q.execute(sql, binds)
            return [tuple(x.read() if hasattr(x, "read") else x for x in row) for row in q.fetchall()]

    def one(self, sql: str, **binds: Any) -> Any:
        rows = self.read(sql, **binds)
        if len(rows) != 1:
            raise RunnerStop(f"EXPECTED_ONE_ROW:{sql[:60]}:{len(rows)}")
        return rows[0] if len(rows[0]) > 1 else rows[0][0]

    def meta(self, sql: str, **binds: Any) -> None:
        """Fixture metadata only, inside the native configuration boundary (ni042 pattern)."""
        with self.connect() as c:
            q = c.cursor(); q.callproc("RRL_STOCK_CONFIG_API.begin_change", ["admin", "warehouse_settings_edit"])
            try:
                q.execute(sql, binds); c.commit()
            except BaseException:
                c.rollback(); raise
            finally:
                q.callproc("RRL_STOCK_CONFIG_API.end_change")

    def post(self, key: str, kind: str, metadata: dict[str, Any], source: dict[str, Any]) -> Any:
        """Native StockPosting through the same journal (K-0217): the exact serialized command is stored before posting; a repeat
        posts those stored bytes; changed content under the same key stops; an unknown outcome blocks every later step."""
        command = {"operation_id": f"{self.s['tag']}.{key}", "command_type": kind, "actor": "admin", "source": source, "metadata": metadata}
        jkey = "native." + key
        wire = self.journal.record(jkey, "NATIVE", kind, command); self.save()
        if jkey in self.journal.results:
            return self.journal.results[jkey]["value"]
        stored = json.loads(wire)
        error, result = None, None
        try:
            result = self.stock_post(stored)
        except Exception as exc:  # classified below; nothing is swallowed
            error = exc
        status = native_status(error)
        try:
            value = self.journal.outcome(jkey, status, result if error is None else {"code": getattr(error, "code", type(error).__name__),
                                                                                   "reason": getattr(error, "rule_reason", None)})
        finally:
            self.save()
        if status != 200:
            raise RunnerStop(f"NATIVE_REFUSED:{jkey}:{value}")
        return value

    def stock_post(self, command: dict[str, Any]) -> Any:
        from app.modules.inventory.contracts_stock import StockCommand
        from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
        return StockPosting().post(StockCommand(operation_id=command["operation_id"], command_type=command["command_type"], actor=command["actor"],
                                                source=command["source"], metadata=command["metadata"], lines=()))

    def get(self, path: str) -> Any:
        r = self.http.get(self.api + path)
        if r.status_code != 200:
            raise RunnerStop(f"READ_FAILED:{path}:HTTP{r.status_code}:{r.text[:300]}")
        return r.json()

    def send(self, key: str, method: str, path: str, body: Any, expect: tuple[int, ...] = (200,)) -> Any:
        wire = self.journal.record(key, method, path, body); self.save()
        if key in self.journal.results:
            return self.journal.results[key]["value"]
        try:
            r = self.http.request(method, self.api + path, content=wire.encode(), headers={"Content-Type": "application/json"})
            status = r.status_code
            value = r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text[:500]
        except Exception:  # network: outcome unknown
            status, value = 0, None
        try:
            result = self.journal.outcome(key, status, value)
        finally:
            self.save()
        if status not in expect:
            raise RunnerStop(f"UNEXPECTED_STATUS:{key}:HTTP{status}:{str(value)[:300]}")
        return result

    def replay_equal(self, key: str) -> None:
        """Lost-response proof: the identical stored bytes again return the identical result and add no stock events."""
        step = self.journal.steps[key]
        op = json.loads(step["wire"]).get("operation_id")
        before = self.one("select count(*) from RRL_EVENTS where OPERATION_ID=:op", op=op)
        r = self.http.request(step["method"], self.api + step["path"], content=step["wire"].encode(), headers={"Content-Type": "application/json"})
        if r.status_code != 200 or r.json() != self.journal.results[key]["value"]:
            raise RunnerStop(f"REPLAY_NOT_IDENTICAL:{key}:HTTP{r.status_code}")
        if self.one("select count(*) from RRL_EVENTS where OPERATION_ID=:op", op=op) != before:
            raise RunnerStop(f"REPLAY_ADDED_EVENTS:{key}")
        self.s.setdefault("replays", []).append(key); self.save()

    def composition(self, identifier: str) -> dict[str, Any]:
        return self.get("/api/warehouse-hus/composition?identifier=" + identifier)

    def preflight(self, args: argparse.Namespace) -> list[str]:
        tag = self.s["tag"]
        ware = self.s.setdefault("warehouse", 230000000 + int(uuid4().hex[:6], 16) % 9000000)
        paths = set(self.get("/openapi.json").get("paths", {}))
        policy_source = (ROOT / "api/wms_api_server/app/modules/inventory/infrastructure/case_pick_policy.py").read_text(encoding="utf-8")
        snap = dict(api_ready=bool(args.api_ready) and Path(args.api_ready).exists(), openapi_paths=paths,
                    weighted_kg_field='"weighted_kg"' in policy_source,
                    tag_rows=sum(self.one(sql, t=tag + "%") for sql in (
                        "select count(*) from RRL_ARTICULS where ACTICUL like :t", "select count(*) from RRL_PALLETS where UID_PALLET like :t",
                        "select count(*) from RRL_CUSTOMER_ORDER where ORDER_NO like :t", "select count(*) from RRL_PICK_WAVE where WAVE_CODE like :t")),
                    warehouse=ware, warehouse_exists=self.one("select count(*) from RRL_WARES where ID=:w", w=ware) > 0,
                    warehouse_stock_rows=self.one("select count(*) from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w", w=ware),
                    warehouse_case_tasks=self.one("select count(*) from RRL_CASE_PICK_TASK where WARE_ID=:w", w=ware),
                    warehouse_waves=self.one("select count(*) from RRL_PICK_WAVE where WARE_ID=:w", w=ware),
                    template_article=bool(self.read("select ARTICUL from RRL_PALLETS where UID_PALLET='DS-BASE-B1'")),
                    parent_tare_kg=args.parent_tare_kg, manual_net_kg=args.manual_net_kg)
        findings = preflight_findings(snap)
        self.s["preflight"] = {k: v for k, v in snap.items() if k != "openapi_paths"} | {"manual_route_present": MANUAL_ROUTE in paths, "findings": findings}
        self.s.setdefault("measurements", {"parent_tare_kg": args.parent_tare_kg, "manual_net_kg": args.manual_net_kg})
        if self.s["measurements"] != {"parent_tare_kg": args.parent_tare_kg, "manual_net_kg": args.manual_net_kg} and self.s.get("stages_done"):
            findings.append("MEASUREMENTS_CHANGED_AFTER_START")  # a resumed run must keep the original operator values
        self.save()
        return findings

    def stage(self, name: str, fn: Callable[[], None]) -> None:
        done = self.s.setdefault("stages_done", [])
        if name in done:
            return
        self.s["stage"] = name; self.save()
        fn()
        done.append(name); self.s["last_verified_stage"] = name; self.save()

    # -- FIXTURE: new tagged warehouse, KG + EA articles, cells, pick faces, revision (ni042 sequence) --
    def fixture(self) -> None:
        tag, ware = self.s["tag"], self.s["warehouse"]
        template = self.one("select ARTICUL from RRL_PALLETS where UID_PALLET='DS-BASE-B1'")
        kg, ea = tag + "K", tag + "E"
        cells = {"src": tag + "S", "kg": tag + "PK", "ea": tag + "PE", "cpt": "CPT_" + str(ware)}
        self.s.update(articles={"kg": kg, "ea": ea}, cells=cells); self.save()
        barcode = lambda: "046" + str(secrets.randbelow(10 ** 11)).zfill(11)
        self.meta("declare x RRL_ARTICULS%rowtype;begin select *into x from RRL_ARTICULS where ACTICUL=:old;x.ACTICUL:=:a;x.BARCODE_SHT:=:b;"
                  "x.ABC_GROUP:='A';x.TYPE_W:=3;x.UNIT_TYPE:='KG';insert into RRL_ARTICULS values x;end;", old=template, a=kg, b=barcode())
        self.meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE)"
                  "values(:a,'KG','KG',1,1,1,6,'C0190 mixed tree KG')", a=kg)
        self.meta("declare x RRL_ARTICULS%rowtype;begin select *into x from RRL_ARTICULS where ACTICUL=:old;x.ACTICUL:=:a;x.BARCODE_SHT:=:b;"
                  "x.ABC_GROUP:='A';insert into RRL_ARTICULS values x;end;", old=template, a=ea, b=barcode())
        self.meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE)"
                  "select :a,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,'C0190 copy of template EA' from RRL_STOCK_UOM_CONVERSION where ARTICUL=:old", a=ea, old=template)
        if self.one("select count(*) from RRL_ARTICULS where ACTICUL=:a and TYPE_W in(2,3,5,6,7)", a=ea):
            raise RunnerStop("TEMPLATE_ARTICLE_IS_WEIGHTED: the EA child would not be a shelf BOX/EA pick")
        for article in (kg, ea):
            self.meta("insert into RRL_SKU_RECEIPT_POLICY(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,SERIALIZED_WEIGHT_BOXES,UPDATED_BY)values(:a,1,0,0,'admin')", a=article)
            self.meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('SKU',:a),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD", a=article)
        self.meta("insert into RRL_WARES(ID,NAME,PREFIX,SPIS_OTBOR_ON_SCAN_OPALL)values(:w,:n,'Q9',1)", w=ware, n="C0190 mixed tree " + tag)
        self.meta("insert into RRL_RECEIPT_WARE_SETTINGS(WARE_ID,OUTGOING_QC_MODE,OUTGOING_QC_INDEPENDENT)values(:w,'BOTH',1)", w=ware)
        for role, cell in cells.items():
            self.meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM)values(:c,:w,0,0,0,:p,:s)", c=cell, w=ware, p=int(role in ("kg", "ea")), s=int(role == "cpt"))
            self.meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD", c=cell)
        for role, article in (("kg", kg), ("ea", ea)):
            face = self.one("select RRL_PICK_FACE_SQ.nextval from dual")
            self.meta("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,MAX_VOLUME,CREATED_BY)values(:f,:w,:c,null,'admin')", f=face, w=ware, c=cells[role])
            self.meta("insert into RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID,PICK_FACE_ID,ARTICUL,BOX_VOLUME_M3,USE_ARTICUL_REPLENISH_RULE,REPLENISHMENT_QTY_MODE)"
                      "values(RRL_PICK_FACE_ARTICUL_SQ.nextval,:f,:a,.24,0,'FULL_PALLET')", f=face, a=article)
        import oracledb
        with self.connect() as c:
            self.s["revision"] = int(c.cursor().callfunc("REVIZION.create_revizion", oracledb.DB_TYPE_NUMBER, [ware, "admin"])); c.commit()

    # -- WAVE: one recipient, two orders (KG, EA) -> two CASE tasks; tare booked, claimed and started --
    def wave(self) -> None:
        tag, ware, a, cells = self.s["tag"], self.s["warehouse"], self.s["articles"], self.s["cells"]
        net = self.s["measurements"]["manual_net_kg"]
        lots = {"kg": tag + ".LOT.K", "ea": tag + ".LOT.E"}
        self.s["lots"] = lots; self.save()
        for role, qty in (("kg", str(Decimal(net) * 2)), ("ea", str(int(EA_QTY) * 2))):
            self.post("register." + role, "INVENTORY_REGISTER_LOT", {"uid": lots[role], "cell": cells[role], "article": a[role], "quantity": qty,
                      "expiry_date": "2030-01-01", "price": 0, "reason": "C0190 mixed tree isolated lot"}, {"revision_id": self.s["revision"]})
        from app.services.picking_service import PickingService
        from app.schemas import PickingPlanCreateRequest, PickWaveCreateRequest, PickWaveAddPlanRequest, PickWaveActionRequest
        customer = self.one("select min(CUSTOMER_ID) from RRL_CUSTOMER")
        picking, plans = PickingService(), []
        for role, qty, unit in (("kg", net, "KG"), ("ea", EA_QTY, self.one("select nvl(max(UNIT_CODE),'EA') from RRL_CUSTOMER_ORDER_ROW where ARTICUL=(select ARTICUL from RRL_PALLETS where UID_PALLET='DS-BASE-B1')"))):
            order = self.one("select RRL_CUSTOMER_ORDER_SQ.nextval from dual")
            self.meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID)values(:o,:n,:c,:w)", o=order, n=f"{tag}.ORD.{role}", c=customer, w=ware)
            self.meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE)values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:o,1,:a,:q,:u)",
                      o=order, a=a[role], q=Decimal(qty), u=unit)
            plans.append(picking.create_plan(PickingPlanCreateRequest(customer_order_id=order, created_by="admin")))
        wave = picking.create_wave(PickWaveCreateRequest(wave_code=tag + ".WAVE", ware_id=ware, created_by="admin"))
        self.s["wave"] = wave; self.save()
        for plan in plans:
            picking.add_wave_plan(wave, PickWaveAddPlanRequest(pick_plan_id=plan, created_by="admin"))
        picking.preview_wave(wave, PickWaveActionRequest(updated_by="admin"))
        picking.launch_wave(wave, PickWaveActionRequest(updated_by="admin", operation_id=f"{tag}.LAUNCH"))
        for task, uid, frm, to, qty in self.read("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE' and SOURCE_DOC_ID=:w and STATUS not in('DONE','CANCELLED')", w=wave):
            self.post(f"task.{task}", "TASK_COMPLETE", {"fact_qty": str(qty), "scanned_pallet": uid, "scanned_from_cell": frm, "scanned_to_cell": to}, {"task_id": int(task)})
        self.post("release", "WAVE_PICK_RELEASE", {}, {"wave_id": wave})
        rows = self.read("select t.CASE_PICK_TASK_ID,l.CASE_PICK_LINE_ID,t.SSCC,l.CELL_CODE,l.ARTICUL,t.PALLET_TYPE_ID from RRL_CASE_PICK_TASK t join RRL_CASE_PICK_LINE l on l.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID where t.PICK_WAVE_ID=:w", w=wave)
        by_article = {r[4]: r for r in rows}
        if len(rows) != 2 or set(by_article) != {a["kg"], a["ea"]} or len({r[0] for r in rows}) != 2:
            raise RunnerStop(f"EXPECTED_TWO_SEPARATE_CASE_TASKS:{rows}")
        self.s["cases"] = {role: dict(task=int(by_article[a[role]][0]), line=int(by_article[a[role]][1]), carrier=by_article[a[role]][2],
                                      cell=by_article[a[role]][3], pallet_type=by_article[a[role]][5]) for role in ("kg", "ea")}
        self.save()
        for role, case in self.s["cases"].items():
            current = next(r for r in self.get(f"/api/inventory/tare/warehouses/{ware}/availability") if r["pallet_type_id"] == case["pallet_type"])
            self.send(f"tare.count.{role}", "POST", "/api/inventory/tare/count", {"operation_id": f"{tag}.TARE.COUNT.{role}", "owner_ware_id": ware,
                      "pallet_type_id": case["pallet_type"], "condition": "GOOD", "observed_quantity": str(int(Decimal(str(current.get("available_quantity") or 0))) + 1),
                      "expected_version": current.get("balance_version") or 0, "reason": "C0190 isolated software fixture container", "decision_reference": f"{tag}.{role}"})
            self.send(f"tare.book.{role}", "POST", "/api/inventory/tare/book", {"operation_id": f"{tag}.TARE.BOOK.{role}", "place_kind": "CASE", "place_id": str(case["task"])})
            self.s.setdefault("tare_bookings", []).append(f"{tag}.TARE.BOOK.{role}"); self.save()
            self.send(f"claim.{role}", "POST", f"/api/case-pick/tasks/{case['task']}/claim", {})
            self.send(f"start.{role}", "POST", f"/api/case-pick/tasks/{case['task']}/start", {})

    # -- PICK_KG_MANUAL_NET: the only weighed route is the manual one; the KG line policy must say weighted_kg --
    def pick_kg(self) -> None:
        case, net = self.s["cases"]["kg"], self.s["measurements"]["manual_net_kg"]
        policy = self.get(f"/api/case-pick/tasks/{case['task']}/lines/{case['line']}/marking-policy")
        if not policy.get("weighted_kg") or policy.get("serialized_weight_boxes"):
            raise RunnerStop(f"KG_LINE_NOT_WEIGHTED_KG:{policy}")
        path = MANUAL_ROUTE.format(task=case["task"], line=case["line"])
        result = self.send("pick.kg", "POST", path, manual_net_body(f"{self.s['tag']}.PICK.KG", net, case["cell"], case["carrier"]))
        self.replay_equal("pick.kg")
        meta = json.loads(self.one("select CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID=:op", op=f"{self.s['tag']}.PICK.KG"))["metadata"]
        if meta.get("measurement", {}).get("origin") != "MANUAL_OPERATOR_ENTRY" or "warehouse_scale_capture" in meta:
            raise RunnerStop("KG_PROVENANCE_NOT_MANUAL")
        if Decimal(str(self.one("select PICKED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:l", l=case["line"]))) != Decimal(net):
            raise RunnerStop("KG_PICKED_QTY_MISMATCH")
        self.s["kg_result"] = result

    def pick_ea(self) -> None:
        case, a = self.s["cases"]["ea"], self.s["articles"]["ea"]
        policy = self.get(f"/api/case-pick/tasks/{case['task']}/lines/{case['line']}/marking-policy")
        if policy.get("weighted_kg") or policy.get("marking_required"):
            raise RunnerStop(f"EA_LINE_NOT_PLAIN:{policy}")
        self.send("pick.ea", "POST", f"/api/case-pick/tasks/{case['task']}/lines/{case['line']}/confirm",
                  ea_confirm_body(f"{self.s['tag']}.PICK.EA", EA_QTY, case["cell"], a, case["carrier"]))
        self.replay_equal("pick.ea")

    # -- TREE: one parent pallet in the carriers' cell; refusals first, then both attachments, then the composition --
    def tree(self) -> None:
        tag, ware, cases = self.s["tag"], self.s["warehouse"], self.s["cases"]
        cell = {self.one("select CURRENT_CELL from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t", t=c["task"]) for c in cases.values()}
        if len(cell) != 1 or None in cell:
            raise RunnerStop(f"CARRIERS_NOT_IN_ONE_CELL:{cell}")  # a carrier move is not invented here
        cell = cell.pop(); parent, other = tag + ".PAL", tag + ".PAL.OTHER"
        tare = self.s["measurements"]["parent_tare_kg"]
        create = lambda uid, at: self.send("create." + uid, "POST", "/api/warehouse-hus/create", {"operation_id": uid + ".CREATE", "identifier": uid, "cell": at,
                                            "warehouse": ware, "container_type": "PALLET", "tare_weight_kg": tare, "scan_container": uid, "scan_cell": at})
        create(parent, cell)
        version = lambda uid: self.composition(uid)["nodes"][0]["version"]
        booking = {role: f"{tag}.TARE.BOOK.{role}" for role in cases}
        kg, ea = cases["kg"], cases["ea"]
        self.send("attach.kg", "POST", "/api/warehouse-hus/attach-case",
                  attach_case_body(f"{tag}.ATTACH.KG", parent, kg["task"], version(parent), version("CASE:" + str(kg["task"])), kg["carrier"], booking["kg"]))
        self.s["tree_attached"] = [kg["task"]]; self.save()
        self.replay_equal("attach.kg")
        before = self.composition(parent)
        negatives = {
            "stale_parent_version": attach_case_body(f"{tag}.NEG.STALE", parent, ea["task"], version(parent) - 1, version("CASE:" + str(ea["task"])), ea["carrier"], booking["ea"]),
            "foreign_carrier_scan": attach_case_body(f"{tag}.NEG.SCAN", parent, ea["task"], version(parent), version("CASE:" + str(ea["task"])), kg["carrier"], booking["ea"]),
            "changed_body_same_operation": attach_case_body(f"{tag}.ATTACH.KG", parent, kg["task"], version(parent), version("CASE:" + str(kg["task"])), kg["carrier"] + ".CHANGED", booking["kg"]),
        }
        create(other, self.s["cells"]["src"])
        negatives["other_cell"] = attach_case_body(f"{tag}.NEG.CELL", other, ea["task"], version(other), version("CASE:" + str(ea["task"])), ea["carrier"], booking["ea"])
        refusals = {}
        for name, body in negatives.items():
            refusals[name] = self.send("neg." + name, "POST", "/api/warehouse-hus/attach-case", body, expect=(409,))
            check_refusal(name, refusals[name], before, self.composition(parent))  # per refusal: exact rule + parent unchanged
        self.s["refusals"] = refusals; self.save()
        self.send("attach.ea", "POST", "/api/warehouse-hus/attach-case",
                  attach_case_body(f"{tag}.ATTACH.EA", parent, ea["task"], version(parent), version("CASE:" + str(ea["task"])), ea["carrier"], booking["ea"]))
        self.s["tree_attached"].append(ea["task"]); self.save()
        snapshot = self.composition(parent)
        findings = tree_findings(snapshot, {"case_tasks": [kg["task"], ea["task"]], "cell": cell,
                                            "quantities": {self.s["articles"]["kg"]: self.s["measurements"]["manual_net_kg"], self.s["articles"]["ea"]: EA_QTY},
                                            "carriers": {kg["task"]: kg["carrier"], ea["task"]: ea["carrier"]}})
        self.s["tree"] = {"snapshot": snapshot, "findings": findings}; self.save()
        if findings:
            raise RunnerStop("TREE_FINDINGS:" + ",".join(findings))

    def transport(self) -> None:
        raise RunnerStop("TRANSPORT_NOT_WIRED: control/LOAD/DEPART and the store receipt need the trip/vehicle/document fixture of "
                         "tests/tradecase/live_nested_shipping.py; stopped after the verified tree")

    # -- CLEANUP: ordered native reversals for exactly what this run created --
    def cleanup(self) -> None:
        tag, ware = self.s["tag"], self.s["warehouse"]
        self.s["cleanup_plan"] = cleanup_plan(self.s); self.save()
        parent = tag + ".PAL"
        for task in list(reversed(self.s.get("tree_attached", []))):
            case = next(c for c in self.s["cases"].values() if c["task"] == task)
            role = next(r for r, c in self.s["cases"].items() if c["task"] == task)
            self.send(f"detach.{role}", "POST", "/api/warehouse-hus/detach-case", {**attach_case_body(f"{tag}.DETACH.{role}", parent, task,
                      self.composition(parent)["nodes"][0]["version"], self.composition("CASE:" + str(task))["nodes"][0]["version"], case["carrier"], None),
                      "reason": "C0190 mixed tree cleanup"})
            self.s["tree_attached"].remove(task); self.save()
        for role, case in self.s.get("cases", {}).items():
            carrier_lots = [r[0] for r in self.read("select LOT_UID from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=:t", t=case["task"])]
            self.s.setdefault("carrier_lots", {})[role] = sorted(set(self.s.get("carrier_lots", {}).get(role, [])) | set(carrier_lots)); self.save()
            lots = [r[0] for r in self.read("select h.LOT_UID from RRL_CASE_CARRIER_LOT h where h.CASE_PICK_TASK_ID=:t and exists(select 1 from RRL_REMAINS r where r.UID_POLETA=h.LOT_UID and r.REMAIN>0)", t=case["task"])]
            version = self.one("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t", t=case["task"])
            self.post(f"return.{role}", "CASE_CARRIER_RETURN", {"destinations": {uid: case["cell"] for uid in lots}, "allow_empty": not lots,
                      "scan_container": case["carrier"], "expected_content_version": int(version), "reason": "C0190 cleanup"}, {"case_task_id": case["task"]})
        if self.s.get("wave"):
            for (reservation,) in self.read("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:w and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0", w=self.s["wave"]):
                self.post(f"release.{reservation}", "RESERVATION_RELEASE", {"reason": "C0190 cleanup"}, {"reservation_id": int(reservation)})
        for role, case in self.s.get("cases", {}).items():
            if f"tare.book.{role}" in self.journal.results:
                self.send(f"tare.cancel.{role}", "POST", "/api/inventory/tare/book-cancel", {"operation_id": f"{tag}.TARE.CANCEL.{role}", "booking_operation_id": f"{tag}.TARE.BOOK.{role}"})
        for pallet_type in {c["pallet_type"] for c in self.s.get("cases", {}).values()}:
            current = next(r for r in self.get(f"/api/inventory/tare/warehouses/{ware}/availability") if r["pallet_type_id"] == pallet_type)
            self.send(f"tare.zero.{pallet_type}", "POST", "/api/inventory/tare/count", {"operation_id": f"{tag}.TARE.ZERO.{pallet_type}", "owner_ware_id": ware,
                      "pallet_type_id": pallet_type, "condition": "GOOD", "observed_quantity": "0", "expected_version": current.get("balance_version") or 0,
                      "reason": "C0190 retire isolated fixture container", "decision_reference": f"{tag}.END"})
        if self.s.get("wave"):
            status = self.one("select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=:w", w=self.s["wave"])
            if status == "LAUNCHED":
                self.post("wave.finish", "WAVE_EXECUTION_FINISH", {"disposition": "RETURNED_TO_PLANNING", "reason": "C0190 native return; demand remains"}, {"wave_id": self.s["wave"]})
            elif status not in ("CANCELLED", "DONE"):
                self.post("wave.cancel", "WAVE_CANCEL", {"reason": "C0190 retire fixture"}, {"document_type": "PICK_WAVE", "document_id": self.s["wave"]})
        rows = self.read("select r.UID_POLETA,r.CELL,p.ARTICUL,r.BASE_UOM,r.STOCK_VERSION,r.REMAIN from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA "
                         "join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w and r.REMAIN>0", w=ware)
        allowed = set(self.s.get("lots", {}).values()) | {uid for uids in self.s.get("carrier_lots", {}).values() for uid in uids}
        a = self.s.get("articles", {})
        registered = {"kg": str(Decimal(self.s["measurements"]["manual_net_kg"]) * 2), "ea": str(int(EA_QTY) * 2)} if a else {}
        expected = {a[role]: qty for role, qty in registered.items() if "native.register." + role in self.journal.results}  # only lots this run posted
        reservations = self.one("select count(*) from RRL_STOCK_RESERVATION r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w and r.STATUS in('ACTIVE','ALLOCATED','PICKING') and r.BASE_QTY>0", w=ware)
        own = [c["task"] for c in self.s.get("cases", {}).values()] or [-1]
        foreign_tasks = self.one("select count(*) from RRL_CASE_PICK_TASK where WARE_ID=:w and CASE_PICK_TASK_ID not in(" + ",".join(str(int(t)) for t in own) + ")", w=ware) + \
            self.one("select count(*) from RRL_WAREHOUSE_TASK t join RRL_CELLS c on c.CELL=t.FROM_CELL where c.WARE_ID=:w and t.STATUS not in('DONE','CANCELLED')", w=ware)
        findings = cleanup_scope_findings(rows, reservations, foreign_tasks, allowed, expected)
        self.s["cleanup_scope"] = {"rows": rows, "findings": findings}; self.save()
        if findings:
            raise RunnerStop("CLEANUP_SCOPE_REFUSED:" + ",".join(findings))  # nothing is counted when anything else is present
        counts = [{"uid": uid, "cell": cell, "article": article, "unit": unit, "quantity": "0", "expected_stock_version": int(version), "unit_keys": [
                    r[0] for r in self.read("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and CURRENT_CELL=:c and STOCK_STATUS='AVAILABLE'", u=uid, c=cell)]}
                  for uid, cell, article, unit, version, _ in rows]
        if counts:
            self.post("count.zero", "INVENTORY_COUNT", {"reason": "C0190 end isolated mixed tree", "counts": counts}, {"revision_id": self.s["revision"]})
        left = self.one("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0) from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w", w=ware)
        self.s["cleanup_final"] = {"remain": str(left[0]), "hard": str(left[1])}; self.save()
        if Decimal(str(left[0])) != 0 or Decimal(str(left[1])) != 0:
            raise RunnerStop(f"CLEANUP_LEFT_STOCK:{left}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", choices=["plan", "preflight", "run", "cleanup"], nargs="?", default="plan")
    ap.add_argument("--api", help="target API base that passed API_READY (shared 8088 is stale for C0188 until root restarts it)")
    ap.add_argument("--api-ready", help="path of the API_READY file for the target runtime")
    ap.add_argument("--parent-tare-kg", help="operator-measured empty parent pallet weight, kg")
    ap.add_argument("--manual-net-kg", help="operator-entered NET kg for the KG line (also its order quantity)")
    ap.add_argument("--state", default=str(EVIDENCE / "mixed-tree.json"))
    args = ap.parse_args()
    if args.mode == "plan":
        print(json.dumps({"stages": STAGES, "manual_route": MANUAL_ROUTE, "transport": "TRANSPORT_NOT_WIRED (stop after TREE)",
                          "cleanup": cleanup_plan({"tree_attached": ["<case_kg>", "<case_ea>"], "case_tasks": ["<case_kg>", "<case_ea>"], "wave": 1,
                                                   "tare_bookings": ["<case_kg>", "<case_ea>"], "lots": 2})}, ensure_ascii=False, indent=1))
        return 0
    if not args.api:
        raise SystemExit("--api is required for preflight/run/cleanup")
    live = Live(args.api, Path(args.state))
    try:
        if args.mode == "cleanup":
            live.cleanup()
            print(json.dumps({"cleanup": live.s.get("cleanup_final")}, ensure_ascii=False))
            return 0
        findings = live.preflight(args)
        if args.mode == "preflight" or findings:
            print(json.dumps({"findings": findings, "warehouse": live.s["warehouse"], "tag": live.s["tag"]}, ensure_ascii=False))
            return 0 if not findings else 2
        for name, fn in zip(STAGES, (live.fixture, live.wave, live.pick_kg, live.pick_ea, live.tree, live.transport)):
            live.stage(name, fn)
    except RunnerStop as stop:
        live.s["stopped"] = str(stop); live.save()
        print(json.dumps({"stopped": str(stop), "last_verified_stage": live.s.get("last_verified_stage"), "cleanup_next": cleanup_plan(live.s)}, ensure_ascii=False))
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
