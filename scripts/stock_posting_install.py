"""Preflight first, then install dormant packages. Never activate posting or grant SYS rights."""
import argparse
import hashlib
import json
import subprocess
import sys
import time
import oracledb
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "api/wms_api_server"))
def connect_ready(settings, wait_seconds: float):
    deadline = time.monotonic() + wait_seconds
    waiting_reported = False
    while True:
        try:
            connection = oracledb.connect(user=settings.oracle_user, password=settings.oracle_password,
                                          dsn=settings.oracle_dsn, tcp_connect_timeout=5, retry_count=0)
            connection.call_timeout = 10000
            return connection
        except oracledb.Error as exc:
            detail = exc.args[0] if exc.args else None
            if getattr(detail, "code", None) == 1017 or time.monotonic() >= deadline:
                raise
            if not waiting_reported:
                print("Waiting for existing Oracle service to finish startup; no DDL executed.", flush=True)
                waiting_reported = True
            time.sleep(min(2, max(0, deadline - time.monotonic())))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--wait-ready", type=float, default=0)
    args = parser.parse_args()
    from stock_posting_environment import load_local_oracle_environment
    load_local_oracle_environment()
    from app.config import get_settings
    settings = get_settings()
    directory = ROOT / "db/migrations/2026-10-08_stock_posting_core"
    release_manifest = json.loads((directory / "current_runtime_manifest.json").read_text(encoding="utf-8"))
    files = release_manifest["components"] + release_manifest["additional_scripts"] + [
        release_manifest["bundle"], release_manifest["contracts"], "014b_recompile.sql"]
    for name in files:
        if Path(name).name != name or not (directory / name).is_file():
            raise RuntimeError("Invalid current runtime component: " + name)
    manifest = {"date": datetime.now(timezone.utc).isoformat(), "purpose": release_manifest["purpose"],
        "files": {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in files},
        "applied": False}
    connection = connect_ready(settings, args.wait_ready)
    try:
        with connection.cursor() as cursor:
            cursor.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
            user, service = cursor.fetchone()
            if (user, service.lower()) != ("RABAEV", "orcl"):
                raise RuntimeError("Unexpected Oracle target")
            cursor.execute("select STATE,BASELINE_ID from RRL_STOCK_RELEASE where RELEASE_ID=1")
            if cursor.fetchone() != ("PREPARED", None):
                raise RuntimeError("Runtime refresh requires PREPARED without B0")
            cursor.execute("select count(*) from RRL_STOCK_OPERATION")
            if cursor.fetchone()[0]:
                raise RuntimeError("Runtime refresh is not a recovery of posted operations")
            cursor.execute("select TABLE_NAME from USER_TAB_PRIVS_RECD where OWNER='SYS' and PRIVILEGE='EXECUTE' "
                           "and TABLE_NAME in ('DBMS_LOCK','DBMS_CRYPTO','DBMS_FLASHBACK')")
            missing = sorted({"DBMS_LOCK", "DBMS_CRYPTO", "DBMS_FLASHBACK"} - {row[0] for row in cursor})
            for table, columns in release_manifest["required_columns"].items():
                cursor.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME=:t", t=table)
                if not set(columns).issubset({row[0] for row in cursor}):
                    raise RuntimeError("Apply versioned foundation/handler schema phases first: " + table)
            manifest.update({"schema": user, "service": service, "missing_direct_grants": missing})
            if args.apply and not missing:
                checkpoint = ROOT / "runtime/stock_posting_20261008" / (
                    "current-runtime-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f"))
                checkpoint.mkdir(parents=True, exist_ok=False)
                names = release_manifest["packages"] + [
                    "RRL_REVIZION_CELL_KOR", "RRL_REVIZION_CELL_KOR_SP_OLD",
                    "RRL_INV_CREATE_LINE2", "RRL_INV_CREATE_LINE3", "RRL_INV_CREATE_LINE4",
                    "RRL_INV_CREATE_LINE2_SP_OLD", "RRL_INV_CREATE_LINE3_SP_OLD", "RRL_INV_CREATE_LINE4_SP_OLD",
                    "ARTICULS", "ARTICULS_SP_OLD", "RRL_CLEAR_OTBOR_CELL", "REVIZION", "REVIZION_SP_OLD", "RRL_STORNO_ORDER3", "RRL_STORNO_ORDER3_SP_OLD",
                    "RRL_ACCEPT_ORDER2", "RRL_ACCEPT_ORDER2_SP_OLD", "RRL_ACCEPT_ORDER2_2", "RRL_ACCEPT_ORDER2_2_SP_OLD", "RRL_ACCEPT_ORDER2_3", "RRL_ACCEPT_ORDER2_3_SP_OLD", "RRL_ACCEPT_ORDER3", "RRL_ACCEPT_ORDER3_SP_OLD", "RRL_OTKAT_ORDER2", "RRL_OTKAT_ORDER2_SP_OLD",
                    "RRL_ADD_INV_LINE", "RRL_ADD_INV_LINE_SP_OLD",
                    "RRL_INTERNAL_MOVE2", "RRL_INTERNAL_MOVE3", "RRL_CLOSE_OTHOD_NAKLAD",
                    "RRL_CLOSE_OTHOD_PALLET", "RRL_INTERNAL_MOVE2_SP_OLD",
                    "RRL_INTERNAL_MOVE3_SP_OLD", "RRL_CLOSE_OTHOD_NAKLAD_SP_OLD",
                    "RRL_CLOSE_OTHOD_PALLET_SP_OLD", "BIN$UX1xZvUbS6/gYw8CAAo/Yg==$0",
                    "RRL_REVIZION_CELL", "RRL_REVIZION_CELL_SP_OLD", "REMAINS", "RRL_SET_SCAN_PROOVE", "RRL_SET_SCAN_PROOVE_SP_OLD", "RRL_SET_SCAN_PROOVE2", "RRL_SET_SCAN_PROOVE2_SP_OLD", "RRL_TRIAL_BY_WEIGHT", "RRL_TRIAL_BY_WEIGHT_SP_OLD", "RRL_TRIAL_BY_WEIGHT2", "RRL_TRIAL_BY_WEIGHT2_SP_OLD", "RRL_UPDATE_PALLET_ROW2", "RRL_UPDATE_PALLET_ROW2_SP_OLD", "RRL_UPDATE_PALLET_ROW2_SP_CALC", "RRL_UPDATE_PALLET_ROW3", "RRL_UPDATE_PALLET_ROW3_SP_OLD", "RRL_UPDATE_PALLET_ROW3_SP_CALC",
                    "RRL_STOCK_COMPAT_FLAG_GUARD", "RRL_STOCK_SETTING_AUDIT_GUARD",
                    "RRL_STOCK_REMAINS_GUARD", "RRL_STOCK_JOURNAL_GUARD",
                    "RRL_STOCK_RESERVATION_GUARD", "RRL_STOCK_UNIT_GUARD", "RRL_CASE_CARRIER_LOT_GUARD", "RRL_PALLET_PACK_GUARD"]
                binds = {f"n{i}": name for i, name in enumerate(names)}
                cursor.execute("select NAME,TYPE,TEXT from USER_SOURCE where NAME in ("
                    + ",".join(":" + key for key in binds) + ") order by "
                    "case TYPE when 'PACKAGE' then 0 when 'PACKAGE BODY' then 1 else 2 end,NAME,LINE", binds)
                from itertools import groupby
                chunks = []
                for (name, kind), rows in groupby(cursor, lambda row: (row[0], row[1])):
                    source = "create or replace " + "".join(row[2] for row in rows).rstrip() + "\n/\n"
                    chunks.append(source)
                (checkpoint / "source-rollback.sql").write_text(
                    "declare n number;begin select count(*) into n from RRL_STOCK_OPERATION;"
                    "if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;\n/\n"
                    + "\n".join(chunks) + "\n@@../../../db/migrations/2026-10-08_stock_posting_core/014b_recompile.sql\n",
                    encoding="utf-8")
                manifest["checkpoint"] = str(checkpoint)
                (checkpoint / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    finally:
        connection.close()
    out = ROOT / "runtime/stock_posting_20261008/runtime-install-preflight.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"package_pairs": len(release_manifest["packages"]),
                      "missing_direct_grants": missing, "apply_requested": args.apply}))
    if missing:
        return 2
    if not args.apply:
        return 0
    completed = subprocess.run([sys.executable, str(ROOT / "scripts/stock_posting_apply.py"),
                                str(directory / release_manifest["bundle"])], cwd=ROOT, check=False)
    if completed.returncode:
        return completed.returncode
    connection = connect_ready(settings, 0)
    try:
        with connection.cursor() as cursor:
            binds = {f"n{i}": name for i, name in enumerate(release_manifest["packages"])}
            cursor.execute("select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and OBJECT_NAME in ("
                + ",".join(":" + key for key in binds) + ") order by OBJECT_NAME,OBJECT_TYPE", binds)
            objects = list(cursor)
            manifest["objects"] = objects
            manifest["applied"] = len(objects) == 2 * len(binds) and all(row[2] == "VALID" for row in objects)
            if not manifest["applied"]:
                raise RuntimeError("Current runtime packages are not all VALID")
    finally:
        connection.close()
        out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("Current runtime refreshed; PREPARED, no activation, reset or stock commands.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
