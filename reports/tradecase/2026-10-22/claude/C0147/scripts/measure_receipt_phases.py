"""C-0147 READ ONLY measurement of the failed 1000-EA marked receipt (operation T3.receive.505b15a0).

No receipt is created: Oracle work runs in `set transaction read only` and is rolled back. Measures
 1) plan_receipt on the exact original body (Python planning + reads, as StockPosting staging does);
 2) round trips persist() would issue for the same marks (counting cursor, no database);
 3) live latency of the per-code duplicate checks persist() issues (same SQL, same 1000 codes).
Credentials come from the serv.bat loader and are never printed.
"""
import json, os, sys, time, pathlib
sys.path.insert(0, "C:/projects/TMS/scripts"); sys.path.insert(0, "C:/projects/TMS/api/wms_api_server")
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.modules.inventory.infrastructure.receipt_commands import plan_receipt
from app.modules.inventory.infrastructure.receiving_marks import ReceivingMarks
from app.modules.inventory.domain.mark_identity import canonical_mark
from hashlib import sha256

EVIDENCE = pathlib.Path("C:/projects/TMS/runtime/test-evidence/tradecase/2026-10-22/T08/topup-live-215266197.json")
fx = json.loads(EVIDENCE.read_text(encoding="utf-8"))["fixture"]
ORDER = "9683535fa2fb471d9214a6a755ec7d42"; N = fx["receipt_quantity"]
units = [dict(unit_id=str(i), quantity="1", codes=[dict(system_code="CRPT", profile_code="TOBACCO", code=fx["gtin"] + fx["tag"][:3] + str(i).zfill(4))]) for i in range(1, N + 1)]
document = {"operation_id": "T3.receive." + fx["tag"], "command_type": "SAP_RECEIPT", "actor": "admin", "source": {"order_id": ORDER},
            "metadata": dict(line_number="1", sscc=fx["pallet"], pallet_identifier=fx["pallet"], quantity=str(N), supplier_batch="TC03." + fx["tag"],
                             expiry_date="2030-01-01", gross_weight=str(N), units=units, aggregations=[])}


class Counting:
    """Stands in for the Oracle cursor inside persist(): counts round trips, answers 'not found / zero'."""
    def __init__(self, gtin):
        self.calls, self.kinds, self.gtin, self.last = 0, {}, gtin, None
    def _hit(self, kind):
        self.calls += 1; self.kinds[kind] = self.kinds.get(kind, 0) + 1
    def execute(self, sql, *a, **k):
        s = " ".join(sql.split()); self._hit(s[:40]); self.last = s
    def fetchone(self):
        return (self.gtin,) if "GTIN" in (self.last or "") else (0,) if "count(*)" in (self.last or "") else None
    def setinputsizes(self, **k): pass
    def executemany(self, sql, rows): self._hit("executemany " + " ".join(sql.split())[:30])
    def callfunc(self, name, *a, **k): self._hit("callfunc " + name); return 1
    def callproc(self, name, *a, **k): self._hit("callproc " + name)


def main():
    e = os.environ
    con = oracledb.connect(user=e["WMS_ORACLE_USER"], password=e["WMS_ORACLE_PASSWORD"], dsn=e.get("WMS_ORACLE_DSN", "127.0.0.1:1521/orcl"))
    cur = con.cursor(); cur.execute("set transaction read only")
    out = {"operation_id": document["operation_id"], "units": N, "read_only": True}
    t = time.perf_counter(); hints, marks = plan_receipt(cur, document); out["plan_receipt_ms"] = round((time.perf_counter() - t) * 1000)
    out["plan_bindings"] = len(hints["unit_bindings"])
    # persist() round trips for the same marks, with the CRPT parent present (as on this pallet).
    import app.modules.inventory.infrastructure.receiving_marks as rm
    rm.create_receipt_parent = lambda c, p, s: (1, "SSCC"); rm.assert_current_mark_policy = lambda *a: None; rm.persist_scanned_aggregates = lambda *a: None
    fake = Counting(fx["gtin"]); t = time.perf_counter()
    ReceivingMarks(fake).persist(fx["pallet"], marks, "admin", bindings=hints["unit_bindings"], base_uom="EA", cell=fx["receive"])
    out["persist_round_trips"] = fake.calls; out["persist_kinds"] = fake.kinds; out["persist_python_ms"] = round((time.perf_counter() - t) * 1000)
    # Live latency of the two per-code duplicate checks persist() issues (exact SQL, exact codes), read only.
    keys = []
    for u in units:
        n = canonical_mark("CRPT", "TOBACCO", u["codes"][0]["code"], fx["gtin"]); keys.append((n["identity"], sha256(n["identity"].encode()).hexdigest()))
    t = time.perf_counter()
    for identity, digest in keys:
        cur.execute("select count(*) from RRL_CRPT_CODES c where c.CIS=:code and nvl(c.UID_PALLET,'#')<>:p", {"code": identity, "p": fx["pallet"]}); cur.fetchone()
        cur.execute("select UID_PALLET from RRL_WMS_RECEIPT_CODE where SYSTEM_CODE=:s and CODE_HASH=:h", {"s": "CRPT", "h": digest}); cur.fetchone()
    per_pair = (time.perf_counter() - t) * 1000 / N
    out["dup_checks_2000_ms"] = round(per_pair * N); out["ms_per_round_trip"] = round(per_pair / 2, 3)
    # Same answer in one set-based query per check (batched form).
    t = time.perf_counter()
    cur.setinputsizes(c=oracledb.DB_TYPE_CLOB)
    cur.execute("select count(*) from RRL_CRPT_CODES c join json_table(:c,'$[*]' columns(CIS varchar2(200) path '$')) j on j.CIS=c.CIS where nvl(c.UID_PALLET,'#')<>:p",
                c=json.dumps([k[0] for k in keys]), p=fx["pallet"]); legacy = cur.fetchone()[0]
    cur.setinputsizes(h=oracledb.DB_TYPE_CLOB)
    cur.execute("select count(*) from RRL_WMS_RECEIPT_CODE r join json_table(:h,'$[*]' columns(H varchar2(64) path '$')) j on j.H=r.CODE_HASH where r.SYSTEM_CODE='CRPT'",
                h=json.dumps([k[1] for k in keys])); dups = cur.fetchone()[0]
    out["batched_dup_checks_ms"] = round((time.perf_counter() - t) * 1000); out["batched_found"] = {"legacy": legacy, "received": dups}
    con.rollback(); con.close()
    out["estimated_persist_round_trip_ms"] = round(out["persist_round_trips"] * out["ms_per_round_trip"])
    path = pathlib.Path(__file__).parent.parent / os.environ.get("C0147_OUT","receipt-phases-before.json"); path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


main()
