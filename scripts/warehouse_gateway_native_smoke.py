"""Cross-check native archived warehouse packets and replay, with caller rollback only."""
import json
import sys
from pathlib import Path
import oracledb

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.db import oracle_connection
from api.wms_api_server.app.modules.integrations.application.warehouse_scale_ack import validate_warehouse_ack
from api.wms_api_server.app.modules.integrations.contracts_warehouse_gateway import WarehouseGatewayProfile


def text(value):
    return value.read() if hasattr(value, "read") else value


def main():
    checks = []
    with oracle_connection() as connection:
        cur = connection.cursor()
        cur.execute("""select SOURCE_JSON,RESULT_JSON,CAPTURE_KEY,CAPTURE_PURPOSE,WARE_ID,DEVICE_MODE,RECORDED_BY
            from(select c.*,row_number()over(partition by CAPTURE_PURPOSE order by RECEIVED_AT desc) rn
            from RRL_WH_SCALE_CAPTURE c join RRL_WH_SCALE_DEVICE d on d.DEVICE_ID=c.DEVICE_ID
            join RUSERS u on u.ID=d.SENDER_ID and nvl(u.DELETED,0)=0
            where c.RECORDED_BY=d.SENDER_ID)where rn=1 order by CAPTURE_PURPOSE""")
        records = [(text(row[0]), text(row[1]), *row[2:]) for row in cur.fetchall()]
        assert {row[3] for row in records} == {"PICK", "EMPTY_TARE", "FINAL_GROSS"}
        cur.execute("select count(*) from RRL_WH_SCALE_CAPTURE")
        before_count = cur.fetchone()[0]
        try:
            for source, ack, key, purpose, warehouse, mode, actor in records:
                packet = json.loads(source)
                profile = WarehouseGatewayProfile(device_id=packet["device_id"], warehouse_id=int(warehouse),
                    post_cell=packet["post_cell"], device_mode=mode,
                    device_policy_version=packet["device_policy_version"],
                    calibration_ref=packet["calibration_ref"], basis=packet["basis"])
                validate_warehouse_ack(source.encode(), ack.encode(), profile)
                out = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_WH_SCALE_API.capture", [source, actor, out])
                repeated = text(out.getvalue())
                assert repeated == ack
                validate_warehouse_ack(source.encode(), repeated.encode(), profile)
                changed = dict(packet, scan_container=packet["scan_container"] + "CONFLICT")
                try:
                    cur.callproc("RRL_WH_SCALE_API.capture", [json.dumps(changed), actor, out])
                except oracledb.DatabaseError as exc:
                    assert "SCALE_CAPTURE_PAYLOAD_CONFLICT" in str(exc), str(exc)
                else:
                    raise AssertionError("Changed archived identity accepted")
                checks.append(dict(purpose=purpose, capture_key=key, original_ack="VALID",
                    exact_native_replay="ORIGINAL", changed_body="CONFLICT", device_mode=mode))
        finally:
            connection.rollback()
        cur.execute("select count(*) from RRL_WH_SCALE_CAPTURE")
        assert cur.fetchone()[0] == before_count
        cur.execute("select count(*) from USER_OBJECTS where STATUS='INVALID'")
        assert cur.fetchone()[0] == 0
        connection.rollback()
    report = dict(status="PASS", checks=checks, archive_count_unchanged=True, stock_effect="NONE",
        new_measurements=0, business_commit=False, physical_weighing_verified=False,
        note="Existing development native archives; no newly manufactured mass or hardware claim")
    target = ROOT / "reports/retailcase/2026-10-15/warehouse-scale-gateway"
    target.mkdir(parents=True, exist_ok=True)
    (target / "native-ack.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
