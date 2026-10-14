"""Adapt the weighted label to the existing CASE_PICK_CONFIRM single writer."""
import oracledb
from decimal import Decimal
from typing import Any
from ....oracle_gateway import OracleGateway
from ...platform.public import read_oracle_json
from ..contracts_weighted_case import WeightedCaseRequest, WeighedLineRequest
from ..contracts_stock import StockCommand, StockPostingError
from .weighted_box_capture import decode_box
from .case_pick_commands import resolve_case_codes
from .stock_posting_uow import StockPosting


class WeightedCasePick:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def short_weight_preview(self, short: int, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("CASE short approver weight source READ ONLY") as q:
                q.execute("set transaction read only")
                q.execute("select CASE_PICK_TASK_ID,CASE_PICK_LINE_ID from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:p_short", p_short=short)
                row = q.fetchone()
                if row is None:
                    raise StockPostingError("ORDER_WEIGHT_SHORT_NOT_FOUND", None, 20886)
                q.callproc("RRL_CASE_TASK_ACCESS.assert_scope", [int(row[0]), actor, "case_pick_short_approve"])
                return read_oracle_json(q.callfunc("RRL_ORDER_WEIGHT_READ.snapshot_json", oracledb.DB_TYPE_CLOB, [int(row[0]), int(row[1]), actor]))
        except oracledb.DatabaseError as exc:
            code = exc.args[0].code
            if code in {20882, 20886, 20881, 1403, 1422}:
                raise StockPostingError("ORDER_WEIGHT_PREVIEW_REJECTED", None, code) from exc
            raise

    def weight_preview(self, task: int, line: int, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Order SKU weight admission READ ONLY") as q:
                q.execute("set transaction read only")
                return read_oracle_json(q.callfunc("RRL_ORDER_WEIGHT_READ.snapshot_json", oracledb.DB_TYPE_CLOB, [task, line, actor]))
        except oracledb.DatabaseError as exc:
            code = exc.args[0].code
            if code in {20882, 20886, 20881, 1403, 1422}:
                raise StockPostingError("ORDER_WEIGHT_PREVIEW_REJECTED", None, code) from exc
            raise

    def weigh_line(self, task: int, line: int, request: WeighedLineRequest, actor: str) -> dict[str, Any]:
        submitted = request.model_dump(mode="json")
        source = {"case_task_id": task, "case_line_id": line}
        saved = self.gateway.fetch_all("select CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID=:p_op",
                                      {"p_op": request.operation_id})
        if saved:
            old = read_oracle_json(saved[0]["canonical_request"])
            if (old["actor"] != actor or old["command_type"] != "CASE_PICK_CONFIRM" or old["source"] != source
                    or old["metadata"].get("weighed_confirmation") != submitted):
                raise StockPostingError("OPERATION_CONTENT_CONFLICT", request.operation_id)
            metadata = old["metadata"]
        else:
            try:
                with self.gateway.transaction("Weighed CASE current source READ ONLY") as q:
                    q.execute("set transaction read only")
                    q.callproc("RRL_CASE_TASK_ACCESS.assert_scope", [task, actor, "case_pick_execute"])
                    q.execute("""select c.WEIGHT_KG,c.SCANNED_PRODUCT,nvl(l.PICKED_QTY,0)
                        from RRL_WH_SCALE_CAPTURE c join RRL_CASE_PICK_LINE l
                          on l.CASE_PICK_TASK_ID=c.CASE_PICK_TASK_ID and l.CASE_PICK_LINE_ID=c.CASE_PICK_LINE_ID
                        where c.CAPTURE_KEY=:p_key and c.CASE_PICK_TASK_ID=:p_task and c.CASE_PICK_LINE_ID=:p_line
                          and c.MEASUREMENT_BASIS='NET'""",
                        p_key=request.warehouse_scale_capture,p_task=task,p_line=line)
                    row = q.fetchone()
                    if row is None:
                        raise ValueError("The NET capture belongs to another CASE line or is missing")
                    weight, product, previous = row
                    metadata = {"fact_qty": format(Decimal(str(previous))+Decimal(str(weight)), "f"),
                        "scan_cell": request.scan_cell, "scan_container": request.scan_container,
                        "scan_product": product, "offline_event_id": None,
                        "warehouse_scale_capture": request.warehouse_scale_capture,
                        "weighed_confirmation": submitted}
            except oracledb.DatabaseError as exc:
                code = exc.args[0].code
                if code in {20882, 20886, 1403, 1422}:
                    raise StockPostingError("WEIGHED_CASE_SOURCE_REJECTED", request.operation_id, code) from exc
                raise
        return StockPosting().post(StockCommand(operation_id=request.operation_id, command_type="CASE_PICK_CONFIRM",
            actor=actor, source=source, lines=(), units=(), metadata=metadata))

    def confirm(self, task: int, line: int, request: WeightedCaseRequest, actor: str) -> dict[str, Any]:
        submitted = request.model_dump(mode="json", exclude_none=True)
        source = {"case_task_id": task, "case_line_id": line}
        saved = self.gateway.fetch_all("select CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID=:p_op",
                                      {"p_op": request.operation_id})
        if saved:
            old = read_oracle_json(saved[0]["canonical_request"])
            if (old["actor"] != actor or old["command_type"] != "CASE_PICK_CONFIRM" or old["source"] != source
                    or old["metadata"].get("weighted_confirmation") != submitted):
                raise StockPostingError("OPERATION_CONTENT_CONFLICT", request.operation_id)
            metadata, units = old["metadata"], tuple(old["units"])
        else:
            try:
                metadata, units = prepare_weighted_case(self.gateway, task, line, request, actor)
            except oracledb.DatabaseError as exc:
                code = exc.args[0].code
                if code in {20882, 20886, 1403, 1422}:
                    raise StockPostingError("WEIGHTED_BOX_SCAN_REJECTED", request.operation_id, code) from exc
                raise
        return StockPosting().post(StockCommand(operation_id=request.operation_id, command_type="CASE_PICK_CONFIRM",
            actor=actor, source=source, lines=(), units=units, metadata=metadata))


def prepare_weighted_case(gateway: OracleGateway, task: int, line: int,
                          request: WeightedCaseRequest, actor: str) -> tuple[dict[str, Any], tuple[str, ...]]:
    with gateway.transaction("Weighted CASE label current READ ONLY snapshot") as cur:
        cur.execute("set transaction read only")
        cur.callproc("RRL_CASE_TASK_ACCESS.assert_scope", [task, actor, "case_pick_execute"])
        box = decode_box(cur, request.weighted_box_barcode)
        cur.execute("""select l.ARTICUL,nvl(l.PICKED_QTY,0),p.POLICY_VERSION,p.MARKING_REQUIRED,
            u.PHYSICAL_UNIT_KEY,u.BASE_QTY,u.BASE_UOM
            from RRL_CASE_PICK_LINE l join RRL_SKU_RECEIPT_POLICY p on p.ARTICUL=l.ARTICUL
            join RRL_WMS_RECEIPT_UNIT u on u.UNIT_ID=:p_identity and u.CURRENT_CELL=l.CELL_CODE
            join RRL_PALLETS lot on lot.UID_PALLET=u.CURRENT_UID and lot.ARTICUL=l.ARTICUL
            join RRL_STOCK_RESERVATION r on r.RESERVATION_ID=u.HARD_RESERVATION_ID
                and r.UID_PALLET=u.CURRENT_UID and r.CELL=u.CURRENT_CELL
                and r.SOURCE_DOC_TYPE='PICK_WAVE'and r.SOURCE_DOC_ID=l.PICK_WAVE_ID and r.SOURCE_LINE_ID=l.PICK_TASK_ID
            where l.CASE_PICK_TASK_ID=:p_task and l.CASE_PICK_LINE_ID=:p_line
                and p.SERIALIZED_WEIGHT_BOXES=1 and u.STOCK_STATUS!='ISSUED'
                and r.RESERVATION_KIND='HARD'and r.STATUS in('ACTIVE','ALLOCATED','PICKING')
            fetch first 2 rows only""", p_identity=box["identity"], p_task=task, p_line=line)
        rows = cur.fetchall()
        if len(rows) != 1:
            raise ValueError("The weighted physical box is not reserved for this CASE line")
        article, picked, version, marked, key, mass, base = rows[0]
        cur.callproc("RRL_WEIGHT_BOX_READ.assert_sku", [article, box["gtin"]])
        if base != "KG" or Decimal(str(mass)) != Decimal(box["net_weight_kg"]):
            raise ValueError("The registered physical box and scanned net KG differ")
        cur.execute("select SYSTEM_CODE,PROFILE_CODE from RRL_SKU_RECEIPT_PROFILE where ARTICUL=:p_article",
                    p_article=article)
        profiles = set(cur.fetchall())
        scanned = {(s.system_code, s.profile_code) for s in request.unit_scans}
        if bool(profiles) != bool(marked) or profiles != scanned or len(scanned) != len(request.unit_scans):
            raise ValueError("Scan every applicable government unit profile for the same physical box")
        fact = format(Decimal(str(picked)) + Decimal(box["net_weight_kg"]), "f")
    if request.unit_scans and resolve_case_codes(gateway, task, line, request.unit_scans) != (key,):
        raise ValueError("The government scans identify another physical unit")
    metadata = {"fact_qty": fact, "scan_cell": request.scan_cell, "scan_product": article,
        "scan_container": request.scan_container, "offline_event_id": None,
        "weighted_box_scan": request.weighted_box_barcode, "weighted_policy_version": int(version),
        "weighted_confirmation": request.model_dump(mode="json", exclude_none=True)}
    if request.warehouse_scale_capture is not None:
        metadata["warehouse_scale_capture"] = request.warehouse_scale_capture
    return metadata, (key,)
