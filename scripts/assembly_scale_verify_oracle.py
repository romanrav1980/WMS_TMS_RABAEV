"""Read-only assembly migration source/guard/ledger verification; not business acceptance."""
import hashlib
import json
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway


def normalized(value):
    value = re.sub(r"^create\s+or\s+replace\s+", "", value.replace("\r", "").strip(), flags=re.I)
    return value.rstrip("/").strip()


def main():
    gateway = OracleGateway()
    folder = ROOT / "db/migrations/2026-10-15_incremental_assembly"
    sources = []
    names = {"assembly_spec.sql": ("RRL_ASSEMBLY_SCALE_API", "PACKAGE"),
        "assembly_body.sql": ("RRL_ASSEMBLY_SCALE_API", "PACKAGE BODY"),
        "scale_packet_spec.sql": ("RRL_SCALE_PACKET_READ", "PACKAGE"),
        "scale_packet_body.sql": ("RRL_SCALE_PACKET_READ", "PACKAGE BODY"),
        "case_scale_admission_body.sql": ("RRL_CASE_SCALE_ADMISSION", "PACKAGE BODY"),
        "stock_case_pick_body.sql": ("RRL_STOCK_CASE_PICK_CMD", "PACKAGE BODY")}
    recovery = gateway.fetch_all("select STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-assembly-scale-recovery'")
    for filename, (name, kind) in names.items():
        source_folder = ROOT / "db/migrations/2026-10-15_assembly_scale_recovery" if recovery and recovery[0]["status"] == "APPLIED" and filename in ("assembly_spec.sql", "assembly_body.sql") else folder
        source = (source_folder / filename).read_text(encoding="utf-8")
        if filename == "assembly_spec.sql":
            source = source.split("\n/", 1)[0]
        sources.append((name, kind, source))
    guards = (folder / "guards.sql").read_text(encoding="utf-8")
    for source in re.findall(r"create or replace trigger .*?\n/", guards, flags=re.S | re.I):
        name = re.search(r"trigger\s+(\w+)", source, re.I).group(1).upper()
        sources.append((name, "TRIGGER", source))
    checks = []
    for name, kind, expected in sources:
        actual = "".join(row["text"] for row in gateway.fetch_all(
            "select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE", {"n": name, "t": kind}))
        assert normalized(actual) == normalized(expected), (name, kind, "SOURCE_MISMATCH")
        assert not gateway.fetch_all("select LINE,TEXT from USER_ERRORS where NAME=:n", {"n": name}), name
        checks.append({"object": name, "type": kind, "source_exact": True,
            "sha256": hashlib.sha256(normalized(actual).encode()).hexdigest()})
    invalid = gateway.fetch_all("select count(*) N from USER_OBJECTS where STATUS='INVALID'")[0]["n"]
    assert invalid == 0
    ledger = gateway.fetch_all("select MIGRATION_ID,STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-incremental-assembly'")
    assert len(ledger) == 1 and ledger[0]["status"] == "APPLIED"
    constraints = gateway.fetch_all("select TABLE_NAME,CONSTRAINT_NAME,STATUS from USER_CONSTRAINTS where TABLE_NAME like 'RRL_ASSEMBLY_%' order by TABLE_NAME,CONSTRAINT_NAME")
    assert constraints and all(row["status"] == "ENABLED" for row in constraints)
    slow = gateway.fetch_all("""select LOG_ID,ELAPSED_MS,API_PATH,dbms_lob.substr(SQL_TEXT,250,1) SQL_SAMPLE
        from RRL_SQL_SLOW_LOG where CREATED_AT>=systimestamp-interval'1'hour
        order by CREATED_AT desc fetch first 12 rows only""")
    report = {"status": "PASS", "source_checks": checks, "invalid_count": invalid,
        "ledger": ledger, "constraints": constraints, "recent_slow": slow,
        "scope": "Source/guard/DDL only; native business and concurrency acceptance separate",
        "sql_decision": "Bounded indexed identities retained; attributable >1000ms queries require plan review, no speculative index."}
    output = ROOT / "reports/retailcase/2026-10-15/assembly-scale"
    output.mkdir(parents=True, exist_ok=True)
    (output / "oracle-verification.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"status": "PASS", "source_checks": len(checks), "invalid_count": invalid, "recent_slow": slow}, default=str))


if __name__ == "__main__":
    main()
