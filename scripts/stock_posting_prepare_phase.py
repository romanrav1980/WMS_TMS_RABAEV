"""Checkpoint only affected Oracle packages and build a dependency-safe dormant bundle."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "db/migrations/2026-10-08_stock_posting_core"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase")
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9]{3}_[a-z_]+", args.phase):
        raise ValueError("Invalid phase name")
    files = [DIRECTORY / name for name in args.files]
    if any(path.parent != DIRECTORY or path.suffix != ".sql" for path in files):
        raise ValueError("Only local versioned SQL components")
    load_local_oracle_environment()
    sys.path.insert(0, str(ROOT / "api/wms_api_server"))
    from app.config import get_settings
    settings = get_settings()
    checkpoint = ROOT / "runtime/stock_posting_20261008" / (args.phase + "-checkpoint")
    checkpoint.mkdir(parents=True, exist_ok=False)
    sources = {}
    specs = []
    names = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        spec = text.split("\n/\n", 1)[0]
        match = re.search(r"create or replace package\s+(\w+)\s", spec, re.I)
        if not match:
            raise ValueError("Expected package component")
        names.append(match.group(1).upper())
        specs.append(spec + "\n/\n")
        sources[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    rollback = []
    with oracledb.connect(user=settings.oracle_user, password=settings.oracle_password, dsn=settings.oracle_dsn) as conn:
        with conn.cursor() as cursor:
            cursor.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
            if cursor.fetchone() != ("RABAEV", "orcl"):
                raise RuntimeError("Unexpected target")
            cursor.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
            if cursor.fetchone()[0] != "PREPARED":
                raise RuntimeError("Dormant install requires PREPARED")
            for kind in ("PACKAGE", "PACKAGE BODY"):
                for name in names:
                    cursor.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE", n=name, t=kind)
                    original = "".join(row[0] for row in cursor)
                    if original:
                        original = "create or replace " + original.rstrip() + "\n/\n"
                        (checkpoint / (name + "_" + kind.replace(" ", "_") + ".sql")).write_text(original, encoding="utf-8")
                        rollback.append(original)
    (checkpoint / "manifest.json").write_text(json.dumps(sources, indent=2), encoding="utf-8")
    contracts = args.phase + "_contracts.sql"
    (DIRECTORY / contracts).write_text("\n".join(specs), encoding="utf-8")
    (DIRECTORY / (args.phase + "_rollback.sql")).write_text(
        "declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; "
        "if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;\n/\n"
        + "\n".join(rollback), encoding="utf-8")
    (DIRECTORY / (args.phase + "_apply.sql")).write_text(
        "@@" + contracts + "\n" + "\n".join("@@" + path.name for path in files) + "\n@@014b_recompile.sql\n",
        encoding="utf-8")
    print(json.dumps({"phase": args.phase, "packages": names, "checkpoint": str(checkpoint)}))


if __name__ == "__main__":
    main()
