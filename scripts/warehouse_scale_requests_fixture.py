"""Root-approved shared DEV metadata stage. No goods PICK/TASK_COMPLETE commits.
Explicit opt-in, one fixed namespace, original QA cell unchanged, all journals retained.
"""
import json
import os
import secrets
import sys
from pathlib import Path
from typing import Any
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.inventory.public import StockCommand, StockPosting
from app.modules.platform.public import stock_configuration_transaction
from app.services.picking_service import PickingService
from app.schemas import PickWaveActionRequest
from app.modules.inventory.infrastructure.configuration import ReceiptConfiguration
from app.modules.inventory.infrastructure.case_labels import CaseLabels
from app.modules.inventory.contracts_case_labels import CaseSsccLabelRequest
from app.modules.inventory.infrastructure.tare import Tare
from wave_launch_continuation_case import create_demand

SOURCE = "REUSE.RETURN:e6c16d0bbd"
CELL = "QIPcdbf4c0962"
WARE = 13583852
ARTICLE = "REUSE.QA:cdbf4c0962"
PREFIX = "WHREQ15.AK06"
ACTOR = "WHREQ15.OP"
SENDER = "WHREQ15.GW"
NOTE = "SIMULATED_TEST_NOT_HARDWARE; root-approved isolated shared QA"
REPORT = ROOT / "reports/retailcase/2026-10-15/warehouse-weigh-request/fixture.json"


def save(context: dict[str, Any]) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(context, indent=2, default=str), encoding="utf-8")


def scalar(cursor: Any, sql: str, **binds: Any) -> Any:
    cursor.execute(sql, binds)
    return cursor.fetchone()[0]


def stock(gateway: OracleGateway) -> list[dict[str, Any]]:
    return gateway.fetch_all("select UID_POLETA,CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:lot_id order by CELL", {"lot_id": SOURCE})


def command(kind: str, operation: str, source: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    return StockPosting().post(StockCommand(operation, kind, "admin", (), source, metadata=metadata))


def create_metadata(gateway: OracleGateway, context: dict[str, Any]) -> None:
    assert not gateway.fetch_all("select ID from RUSERS where ID in(:operator,:sender)", {"operator": ACTOR, "sender": SENDER})
    passwords = {actor: secrets.token_urlsafe(24) for actor in (ACTOR, SENDER)}
    private = ROOT / "runtime/warehouse-weigh-qa-secrets.json"
    private.parent.mkdir(parents=True, exist_ok=True)
    private.write_text(json.dumps(passwords), encoding="utf-8")
    with stock_configuration_transaction(gateway, NOTE, "admin", "warehouse_settings_edit") as cursor:
        for key, sequence in (("order", "RRL_CUSTOMER_ORDER_SQ"), ("order_row", "RRL_CUSTOMER_ORDER_ROW_SQ"),
                ("plan", "RRL_PICK_PLAN_SQ"), ("line", "RRL_PICK_PLAN_LINE_SQ"), ("task", "RRL_PICK_TASK_SQ"),
                ("reservation", "RRL_PICK_RESERVATION_SQ"), ("wave", "RRL_PICK_WAVE_SQ"),
                ("wave_order", "RRL_PICK_WAVE_ORDER_SQ"), ("face", "RRL_PICK_FACE_SQ"),
                ("face_article", "RRL_PICK_FACE_ARTICUL_SQ")):
            context[key] = int(scalar(cursor, "select " + sequence + ".nextval from dual"))
        for actor, group in ((ACTOR, "WHREQ15.OP"), (SENDER, "WHREQ15.SENDER")):
            cursor.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:name,:pw,:grp,:ware,0,0)",
                id=actor, name=NOTE, pw=passwords[actor], grp=group, ware=WARE)
        cursor.execute("insert into RIGHTS(RIGHT1,USER_GROUP,DESCR)values('warehouse_scale_ingest','WHREQ15.SENDER',:note)", note=NOTE)
        cursor.execute("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,PICK_FACE_TYPE,MAX_VOLUME,ACTIVE,CREATED_BY)values(:id,:ware,:cell,'REGULAR',1,1,'admin')",
            id=context["face"], ware=WARE, cell=CELL)
        cursor.execute("""insert into RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID,PICK_FACE_ID,ARTICUL,MIN_QTY,MAX_QTY,USE_ARTICUL_REPLENISH_RULE,
            REPLENISHMENT_METHOD,REPLENISHMENT_QTY_MODE,BOXES_PER_PALLET,BOX_VOLUME_M3,ACTIVE,CREATED_BY)
            values(:id,:face,:article,0,24,0,'IMMEDIATE','FULL_PALLET',24,0.001,1,'admin')""",
            id=context["face_article"], face=context["face"], article=ARTICLE)
        create_demand(cursor, context)
    context["metadata_fixture_committed_temporarily"] = True
    save(context)


def launch(gateway: OracleGateway, context: dict[str, Any]) -> None:
    picking = PickingService(gateway)
    picking.preview_wave(context["wave"], PickWaveActionRequest(updated_by="admin"))
    context["preview_demand"] = gateway.fetch_all("select *from RRL_PICK_WAVE_DEMAND where PICK_WAVE_ID=:wave", {"wave": context["wave"]})
    assert len(context["preview_demand"]) == 1
    context["launch_operation"] = PREFIX + ".LAUNCH"
    context["launch"] = picking.launch_wave(context["wave"], PickWaveActionRequest(updated_by="admin", operation_id=context["launch_operation"]))
    context["stock_after_launch"] = stock(gateway)
    tasks = gateway.fetch_all("select TASK_ID,STATUS,QTY,UID_PALLET,FROM_CELL,TO_CELL from RRL_WAREHOUSE_TASK where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:wave",
                              {"wave": context["wave"]})
    context["warehouse_tasks"] = tasks
    save(context)
    if tasks:
        context["abort_wave"] = command("WAVE_CANCEL", PREFIX + ".ABORT.WAVE", {"document_type": "PICK_WAVE", "document_id": context["wave"]}, {"reason": NOTE + "; physical replenishment forbidden", "only_cancelled_replenishment": 0, "reservation_kind": None})
        context["abort_plan"] = command("PICK_PLAN_CANCEL", PREFIX + ".ABORT.PLAN", {"document_type": "PICK_PLAN", "document_id": context["plan"]}, {"reason": NOTE, "only_cancelled_replenishment": 0, "reservation_kind": None})
        context["state"] = "ABORTED_PHYSICAL_REPLENISHMENT_REQUIRED"
        save(context)
        raise RuntimeError("Physical warehouse task appeared; canonical wave/plan cancellation recorded")
    cases = gateway.fetch_all("select CASE_PICK_TASK_ID,SSCC,CONTENT_VERSION,PALLET_TYPE_ID,STATUS,PICKED_QTY from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:wave", {"wave": context["wave"]})
    assert len(cases) == 1 and cases[0]["status"] == "NEW" and cases[0]["picked_qty"] == 0, cases
    context["case"] = int(cases[0]["case_pick_task_id"])
    lines = gateway.fetch_all("select CASE_PICK_LINE_ID,CELL_CODE,ARTICUL,PLANNED_QTY,PICKED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:task", {"task": context["case"]})
    assert len(lines) == 1 and lines[0]["cell_code"] == CELL and lines[0]["planned_qty"] == 1, lines
    context["case_line"] = int(lines[0]["case_pick_line_id"])
    context["case_before_type"] = cases[0]
    context["case_lines"] = lines
    assert sum(row["remain"] for row in context["stock_after_launch"]) == 24
    save(context)


def small_container(gateway: OracleGateway, context: dict[str, Any]) -> None:
    old_case = context["case_before_type"]
    context["type_change"] = command("CASE_PALLET_TYPE_CHANGE", PREFIX + ".TYPE", {"case_task_id": context["case"]},
        {"expected_version": old_case["content_version"], "pallet_type_id": 32, "scan_container": old_case["sscc"], "reason": NOTE})
    assert context["type_change"]["stock_changed"] is False
    settings = ReceiptConfiguration(gateway)
    original = settings.get(WARE)
    context["warehouse_settings_before"] = original
    save(context)
    try:
        settings.save(WARE, {**original, "company_prefix": "900000", "extension_digit": 0}, "admin")
        current = gateway.fetch_all("select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:task", {"task": context["case"]})[0]
        labels = CaseLabels(gateway)
        context["label"] = labels.issue(context["case"], CaseSsccLabelRequest(operation_id=PREFIX + ".LABEL",
            scan_container=current["sscc"], expected_content_version=int(current["content_version"])), "admin")
        context["label_confirmation"] = labels.confirm(context["case"], context["label"]["sscc"], "admin")
        save(context)
    finally:
        settings.save(WARE, original, "admin")
    context["state"] = "CASE_NEW_UNASSIGNED_AWAIT_RESOURCE"
    context["goods_pick_committed"] = False
    context["physical_hardware"] = False
    context["stock_staged"] = stock(gateway)
    save(context)


def main() -> None:
    if os.environ.get("RUN_APPROVED_WH_METADATA_STAGE") != "1":
        raise SystemExit("Root-approved metadata stage needs explicit RUN_APPROVED_WH_METADATA_STAGE=1")
    assert not REPORT.exists(), "One shared fixture report exists; resume recorded IDs, never fork the fixture"
    gateway = OracleGateway()
    assert gateway.fetch_all("select STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-warehouse-scale-requests'") == [{"status": "APPLIED"}]
    before = stock(gateway)
    positive = [row for row in before if row["remain"] > 0]
    assert len(positive) == 1 and positive[0]["cell"] == CELL and positive[0]["remain"] == 24 and positive[0]["hard_reserved_base"] == 0 and positive[0]["stock_version"] == 9, before
    context = dict(prefix=PREFIX, cell=CELL, actor=ACTOR, sender=SENDER, source=SOURCE, source_before=before, state="PREPARED")
    create_metadata(gateway, context)
    launch(gateway, context)
    small_container(gateway, context)
    print(json.dumps({key: context[key] for key in ("state", "wave", "case", "case_line", "actor", "sender", "stock_staged")}, default=str))


if __name__ == "__main__":
    main()

