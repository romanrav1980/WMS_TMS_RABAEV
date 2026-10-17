"""Read-only exact-source and metadata verification for the additive OPC evidence archive."""
import hashlib
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway


def normalized(value):
    return re.sub(r"^create\s+or\s+replace\s+", "", value.replace("\r", "").strip(), flags=re.I).rstrip("/").strip()


def main():
    gateway = OracleGateway()
    folder = ROOT / "db/migrations/2026-10-15_opc_scale_evidence"
    extension = gateway.fetch_all("select STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-assembly-evidence-binding'")
    body_folder = ROOT / "db/migrations/2026-10-15_assembly_evidence_binding" if extension and extension[0]["status"] == "APPLIED" else folder
    shape = gateway.fetch_all("select STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-assembly-evidence-shape-fix'")
    if shape and shape[0]["status"] == "APPLIED":
        body_folder = ROOT / "db/migrations/2026-10-15_assembly_evidence_shape_fix"
    reconciliation = gateway.fetch_all("select STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-assembly-reconciliation-evidence'")
    if reconciliation and reconciliation[0]["status"] == "APPLIED":
        body_folder = ROOT / "db/migrations/2026-10-15_assembly_reconciliation_evidence"
    schema = (folder / "schema.sql").read_text(encoding="utf-8")
    expected = [("RRL_OPC_EVIDENCE_API", "PACKAGE BODY", (body_folder / "body.sql").read_text(encoding="utf-8")),
        ("RRL_OPC_EVIDENCE_API", "PACKAGE", re.search(r"create or replace package .*?\n/\n", schema, re.S).group()),
        ("RRL_OPC_EVIDENCE_GUARD", "TRIGGER", re.search(r"create or replace trigger .*?\n/\n", schema, re.S).group())]
    checks = []
    for name, kind, body in expected:
        actual = "".join(row["text"] for row in gateway.fetch_all(
            "select TEXT from USER_SOURCE where NAME=:name and TYPE=:kind order by LINE", dict(name=name, kind=kind)))
        assert normalized(actual) == normalized(body), (name, kind)
        assert not gateway.fetch_all("select LINE,TEXT from USER_ERRORS where NAME=:name", dict(name=name))
        checks.append(dict(object=name, type=kind, source_exact=True,
            sha256=hashlib.sha256(normalized(actual).encode()).hexdigest()))
    invalid = gateway.fetch_all("select count(*) N from USER_OBJECTS where STATUS='INVALID'")[0]["n"]
    assert invalid == 0
    ledger = gateway.fetch_all("""select MIGRATION_ID,STATUS from RRL_SCHEMA_MIGRATIONS
        where MIGRATION_ID='2026-10-15-opc-scale-evidence'""")
    assert len(ledger) == 1 and ledger[0]["status"] == "APPLIED"
    constraints = gateway.fetch_all("""select CONSTRAINT_NAME,STATUS from USER_CONSTRAINTS
        where TABLE_NAME='RRL_OPC_SCALE_EVIDENCE' order by CONSTRAINT_NAME""")
    assert constraints and all(row["status"] == "ENABLED" for row in constraints)
    slow = gateway.fetch_all("""select LOG_ID,to_char(CREATED_AT,'YYYY-MM-DD HH24:MI:SS') CREATED_AT,
        ELAPSED_MS,API_PATH,dbms_lob.substr(SQL_TEXT,250,1) SQL_SAMPLE from RRL_SQL_SLOW_LOG
        where CREATED_AT>=systimestamp-interval'1'hour order by CREATED_AT desc fetch first 12 rows only""")
    result = dict(status="PASS", source_checks=checks, user_errors=0, invalid_count=invalid, ledger=ledger,
        constraints=constraints, recent_slow=slow, decision="Native archive17/8/12ms. Existing unique identity/capture lookups retained; no index added. Repeated >1000ms needs query/plan attribution. Native caller-owned acceptance generates no HTTP API audit.")
    target = ROOT / "reports/retailcase/2026-10-15/scale-evidence/oracle-verification.json"
    target.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(json.dumps(dict(status="PASS", source_checks=len(checks), user_errors=0, invalid_count=invalid, recent_slow=slow), default=str))


if __name__ == "__main__":
    main()
