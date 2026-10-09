"""Record only concrete converted native entrypoints; leave the remaining writers unconverted."""
import hashlib
import json
import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment

ROOT = Path(__file__).resolve().parents[1]
ITEMS = (
    ("ARTICULS", "PACKAGE BODY", "174_article_adapter.sql"),
    ("ARTICULS", "PACKAGE BODY", "174_article_adapter.sql"),
    ("REVIZION", "PACKAGE BODY", "152_revision_adapter.sql"),
    ("RRL_REVIZION_CELL_KOR", "FUNCTION", "141_revision_cell_entrypoint.sql"),
    ("RRL_INV_CREATE_LINE2", "FUNCTION", "137_inventory_2_entrypoint.sql"),
    ("RRL_INV_CREATE_LINE3", "FUNCTION", "137_inventory_3_entrypoint.sql"),
    ("RRL_INV_CREATE_LINE4", "FUNCTION", "137_inventory_4_entrypoint.sql"),
    ("RRL_STORNO_ORDER3", "PROCEDURE", "132_storno_entrypoint.sql"),
    ("RRL_ADD_INV_LINE", "FUNCTION", "126_inventory_entrypoint.sql"),
    ("RRL_PICKING_API", "PACKAGE BODY", "116_native_picking.sql"),
    ("RRL_MES_PRODUCTION_API", "PACKAGE BODY", "100_native_mes_production.sql"),
    ("RRL_PICK_WAVE_API", "PACKAGE BODY", "107_native_wave_api.sql"),
    ("RRL_INTERNAL_MOVE2", "FUNCTION", "067_internal_entrypoints.sql"),
    ("RRL_INTERNAL_MOVE3", "FUNCTION", "067_internal_entrypoints.sql"),
    ("RRL_CLOSE_OTHOD_NAKLAD", "FUNCTION", "070_shipping_entrypoints.sql"),
    ("RRL_CLOSE_OTHOD_PALLET", "FUNCTION", "070_shipping_entrypoints.sql"),
    ("RRL_MES_RAW_SUPPLY_API", "PACKAGE BODY", "084_mes_supply_entrypoint.sql"),
    ("BIN$UX1xZvUbS6/gYw8CAAo/Yg==$0", "TRIGGER", "092_event_trigger.sql"),
)


def main():
    load_local_oracle_environment()
    sys.path.insert(0, str(ROOT / "api/wms_api_server"))
    from app.config import get_settings
    settings = get_settings()
    statements = ["declare v varchar2(20);begin select STATE into v from RRL_STOCK_RELEASE where RELEASE_ID=1;"
                  "if v!='PREPARED' then raise_application_error(-20808,'REGISTRY_REQUIRES_PREPARED');end if;end;\n/\n"]
    with oracledb.connect(user=settings.oracle_user, password=settings.oracle_password, dsn=settings.oracle_dsn) as conn:
        cursor = conn.cursor()
        cursor.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
        if cursor.fetchone() != ("RABAEV", "orcl"):
            raise RuntimeError("Unexpected target")
        for name, kind, reference in ITEMS:
            cursor.execute("select STATUS from USER_OBJECTS where OBJECT_NAME=:n and OBJECT_TYPE=:t", n=name, t=kind)
            row = cursor.fetchone()
            if row != ("VALID",):
                raise RuntimeError("Converted entrypoint is not VALID: " + name)
            cursor.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE", n=name, t=kind)
            source = "create or replace " + "".join(row[0] for row in cursor).rstrip() + "\n/\n"
            required_call = ("RRL_STOCK_CONFIG_API.begin_change" if name == "ARTICULS" else
                             "RRL_STOCK_REVISION_ENTRY.count_row" if name == "REVIZION" else
                             "RRL_STOCK_EVENT_BRIDGE.after_event" if kind == "TRIGGER" else
                             "RRL_STOCK_INV_ENTRY.count_lot" if name == "RRL_REVIZION_CELL_KOR" else
                             "RRL_STOCK_INV_ENTRY.register_line" if name in {"RRL_INV_CREATE_LINE2","RRL_INV_CREATE_LINE3","RRL_INV_CREATE_LINE4"} else
                             "return RRL_INTERNAL_MOVE2(" if name == "RRL_INTERNAL_MOVE3" else
                             "RRL_STOCK_NATIVE_API.post")
            if required_call.lower() not in source.lower():
                raise RuntimeError("Missing fixed core entrypoint: " + name)
            digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
            key = "ORACLE:" + kind + ":" + name
            statements.append("update RRL_STOCK_WRITER_REGISTRY set STATE='ADAPTED',SOURCE_HASH='"
                + digest + "',ADAPTER_REFERENCE='db/migrations/2026-10-08_stock_posting_core/"
                + reference + "',UPDATED_AT=systimestamp where WRITER_KEY='" + key.replace("'", "''") + "';")
    statements.append("commit;\n")
    path = ROOT / "db/migrations/2026-10-08_stock_posting_core/099_native_writer_registry.sql"
    if "--emit" in sys.argv:
        print(json.dumps({"099_native_writer_registry.sql":"\n".join(statements)}))
        return
    path.write_text("\n".join(statements), encoding="utf-8")
    print("Prepared registry SQL for " + str(len(ITEMS)) + " concrete native adapters; other candidates remain unconverted")


if __name__ == "__main__":
    main()
