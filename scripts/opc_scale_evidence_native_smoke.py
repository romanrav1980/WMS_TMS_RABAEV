"""Native raw provenance acceptance; all raw observations are labelled test fixtures and rolled back."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
from time import perf_counter
from uuid import uuid4
import oracledb

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.db import oracle_connection
from app.modules.integrations.contracts_scale_evidence import ScaleEvidence


def fixture_envelope():
    spec = importlib.util.spec_from_file_location("raw_evidence_fixture", ROOT / "tests/test_scale_evidence_api.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.envelope()


def text(value):
    return value.read() if hasattr(value, "read") else value


def native(cursor, method, arguments):
    output = cursor.var(oracledb.DB_TYPE_CLOB)
    cursor.callproc("RRL_OPC_EVIDENCE_API." + method, [*arguments, output])
    return json.loads(text(output.getvalue()))


def rejected(callback, marker):
    try:
        callback()
    except oracledb.DatabaseError as exc:
        assert marker in str(exc), str(exc)
    else:
        raise AssertionError("Native rule did not reject " + marker)


def sources(cursor):
    selected = []
    for kind, table, devices, purpose in (
        ("STORE_RECEIPT", "RRL_STORE_SCALE_CAPTURE", "RRL_STORE_SCALE_DEVICE", "1=1"),
        ("WAREHOUSE_PICK", "RRL_WH_SCALE_CAPTURE", "RRL_WH_SCALE_DEVICE", "c.CAPTURE_PURPOSE='PICK'"),
        ("WAREHOUSE_FINAL", "RRL_WH_SCALE_CAPTURE", "RRL_WH_SCALE_DEVICE", "c.CAPTURE_PURPOSE='FINAL_GROSS'")):
        test_filter = "c.DEVICE_MODE='TEST'" if kind != "STORE_RECEIPT" else "c.RECORDED_BY like 'QS%'"
        cursor.execute(f"""select c.DEVICE_ID,c.CAPTURE_ID,c.SOURCE_SHA256,c.RECORDED_BY,u.DELETED
            from {table} c join {devices} d on d.DEVICE_ID=c.DEVICE_ID
            join RUSERS u on u.ID=c.RECORDED_BY where c.RECORDED_BY=d.SENDER_ID
            and {test_filter} and {purpose} order by c.RECEIVED_AT desc fetch first 1 row only""")
        row = cursor.fetchone()
        assert row and row[3].startswith("QS"), (kind, row)
        selected.append(dict(kind=kind, device=row[0], capture=row[1], sha=row[2], actor=row[3], deleted=row[4]))
    return selected


def body_for(source):
    body = fixture_envelope()
    body.update(capture_kind=source["kind"], device_id=source["device"], capture_id=source["capture"],
        capture_sha256=source["sha"], station_id="TEST.NATIVE.FIXTURE.NOT.HARDWARE")
    # Archive must retain bad raw quality for diagnostics, not treat it as physical acceptance.
    body["observations"][0]["values"]["current_weight"]["status_code"] = 2147483648
    body["observations"][0]["values"]["current_weight"]["source_timestamp"] = None
    return ScaleEvidence.model_validate(body).canonical_bytes().decode()


def original_sender_negative(source):
    with oracle_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""select d.SENDER_ID,u.DELETED,d.POLICY_VERSION from RRL_STORE_SCALE_DEVICE d join RUSERS u on u.ID=d.SENDER_ID
            where d.DEVICE_ID=:device""", device=source["device"])
        before = cursor.fetchone()
        cursor.execute("""select distinct u.ID,u.DELETED from RRL_STORE_SCALE_DEVICE d join RUSERS u on u.ID=d.SENDER_ID
            where u.ID!=:actor and u.ID like 'QS%' and u.WARE_ID=1 order by u.ID fetch first 1 row only""", actor=source["actor"])
        alternate = cursor.fetchone()
        assert alternate
        connection.rollback()
        try:
            cursor.callproc("RRL_STOCK_CONFIG_API.begin_change", ["admin", "warehouse_settings_edit"])
            cursor.execute("update RUSERS set DELETED=0 where ID=:actor", actor=alternate[0])
            cursor.execute("update RRL_STORE_SCALE_DEVICE set SENDER_ID=:actor,POLICY_VERSION=POLICY_VERSION+1 where DEVICE_ID=:device",
                actor=alternate[0], device=source["device"])
            rejected(lambda: native(cursor, "archive", [body_for(source), alternate[0]]), "OPC_EVIDENCE_ORIGINAL_SENDER_REQUIRED")
        finally:
            cursor.callproc("RRL_STOCK_CONFIG_API.end_change")
            connection.rollback()
        cursor.execute("""select d.SENDER_ID,u.DELETED,d.POLICY_VERSION from RRL_STORE_SCALE_DEVICE d join RUSERS u on u.ID=d.SENDER_ID
            where d.DEVICE_ID=:device""", device=source["device"])
        assert cursor.fetchone() == before
        cursor.execute("select DELETED from RUSERS where ID=:actor", actor=alternate[0])
        assert cursor.fetchone()[0] == alternate[1]
        connection.rollback()


def main():
    checks, timings = [], []
    with oracle_connection() as connection:
        cursor = connection.cursor()
        selected = sources(cursor)
        cursor.execute("select count(*) from RRL_OPC_SCALE_EVIDENCE")
        before_count = cursor.fetchone()[0]
        connection.rollback()
        try:
            for source in selected:
                cursor.execute("update RUSERS set DELETED=0 where ID=:actor", actor=source["actor"])
                wire = body_for(source)
                wrong = json.loads(wire)
                wrong["capture_sha256"] = "D" * 64
                rejected(lambda: native(cursor, "archive", [json.dumps(wrong), source["actor"]]), "OPC_EVIDENCE_CAPTURE_HASH_CONFLICT")
                missing_protocol = json.loads(wire)
                missing_protocol["protocol_version"] = None
                rejected(lambda: native(cursor, "archive", [json.dumps(missing_protocol), source["actor"]]), "OPC_EVIDENCE_PROTOCOL_REQUIRED")
                started = perf_counter()
                first = native(cursor, "archive", [wire, source["actor"]])
                timings.append(dict(kind=source["kind"], archive_ms=round((perf_counter()-started)*1000, 2)))
                assert first["binding"] == "MATCHED" and first["stock_posted"] is False
                assert first["provenance"] == "GATEWAY_REPORTED" and first["capture_sha256"] == source["sha"]
                assert first["evidence_sha256"] == ScaleEvidence.model_validate_json(wire).digest()
                assert native(cursor, "archive", [wire, source["actor"]]) == first
                assert native(cursor, "describe", [source["kind"], source["device"], source["capture"], source["actor"]]) == first
                changed = json.loads(wire)
                changed["profile_sha256"] = "E" * 64
                rejected(lambda: native(cursor, "archive", [json.dumps(changed), source["actor"]]), "OPC_EVIDENCE_PAYLOAD_CONFLICT")
                rejected(lambda: native(cursor, "describe", [source["kind"], source["device"], source["capture"], "admin"]), "OPC_EVIDENCE_DEVICE_SENDER_REQUIRED")
                cursor.execute("update RUSERS set DELETED=1 where ID=:actor", actor=source["actor"])
                rejected(lambda: native(cursor, "archive", [wire, source["actor"]]), "OPC_EVIDENCE_CURRENT_SENDER_REQUIRED")
                rejected(lambda: native(cursor, "describe", [source["kind"], source["device"], source["capture"], source["actor"]]), "OPC_EVIDENCE_CURRENT_SENDER_REQUIRED")
                cursor.execute("update RUSERS set DELETED=0 where ID=:actor", actor=source["actor"])
                checks.append(dict(kind=source["kind"], archive="MATCHED", read_replay="EXACT", wrong_hash="REJECTED",
                    changed_body="CONFLICT", null_protocol="REJECTED", foreign="DENIED", revoked="DENIED"))
            source = selected[0]
            pending = json.loads(body_for(source))
            pending["capture_id"] = "TEST.PENDING." + uuid4().hex
            first = native(cursor, "archive", [json.dumps(pending), source["actor"]])
            assert first["binding"] == "PENDING"
            assert native(cursor, "describe", [source["kind"], source["device"], pending["capture_id"], source["actor"]])["binding"] == "PENDING"
            checks.append(dict(case="missing_capture", binding="PENDING", no_capture_created=True))
            for verb in ("update RRL_OPC_SCALE_EVIDENCE set RECORDED_BY=RECORDED_BY", "delete from RRL_OPC_SCALE_EVIDENCE"):
                rejected(lambda: cursor.execute(verb), "OPC_EVIDENCE_APPEND_ONLY")
            rejected(lambda: cursor.execute("insert into RRL_OPC_SCALE_EVIDENCE select * from RRL_OPC_SCALE_EVIDENCE fetch first 1 row only"), "OPC_EVIDENCE_NATIVE_CONTEXT_REQUIRED")
            checks.append(dict(case="direct_dml", insert="DENIED", update="DENIED", delete="DENIED"))
        finally:
            connection.rollback()
        cursor.execute("select count(*) from RRL_OPC_SCALE_EVIDENCE")
        assert cursor.fetchone()[0] == before_count
        for source in selected:
            cursor.execute("select DELETED from RUSERS where ID=:actor", actor=source["actor"])
            assert cursor.fetchone()[0] == source["deleted"]
        connection.rollback()
    original_sender_negative(selected[0])
    checks.append(dict(case="changed_current_device_sender", original_sender_binding="DENIED", all_metadata_rolled_back=True))
    report = dict(status="PASS", checks=checks, timings=timings, raw_observations="TEST_FIXTURE_NOT_HARDWARE",
        business_commit=False, stock_effect="NONE", source_capture_changes=0, evidence_count_restored=True,
        historical_QA_senders_temporarily_undeleted_then_restored=True)
    target = ROOT / "reports/retailcase/2026-10-15/scale-evidence/native-acceptance.json"
    target.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
