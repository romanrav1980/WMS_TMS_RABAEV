"""READ ONLY paper snapshot of one existing CASE pick task (C-0156, BP15): what to pick per line, the native line version and its barcode.

Printing executes nothing. The fact goes through the existing CASE_PICK_CONFIRM with expected_case_signature; the native command refuses
an old sheet (CASE_PAPER_LINE_CHANGED). Lines whose fact needs a scanned code (marking, weight label) are flagged and not entered from paper;
loose kg lines stay on the existing manual-scale channel (the reading is the quantity). SQL: scope, head, lines, one policy projection."""
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any
import oracledb
from ....transaction_gateway import TransactionGateway
from ..contracts_case_paper import CasePaperError
from ..domain.case_paper import case_line_barcode

LINE_LIMIT = 200  # a pallet task far above any real CASE task; more is refused, not cut


# Same projection as case_pick_policy (marking-policy endpoint), once per distinct article of the task in this READ ONLY snapshot.
POLICY = """select l.ARTICUL,
          case when exists(select 1 from RRL_ARTICULS a where a.ACTICUL=l.ARTICUL and a.TYPE_W in(2,3,5,6,7))
            and exists(select 1 from RRL_STOCK_UOM_CONVERSION c where c.ARTICUL=l.ARTICUL and c.INPUT_UOM='KG'and c.BASE_UOM='KG'and c.NUMERATOR=1 and c.DENOMINATOR=1)then 1 else 0 end WEIGHTED_KG,
          nvl((select SERIALIZED_WEIGHT_BOXES from RRL_SKU_RECEIPT_POLICY p where p.ARTICUL=l.ARTICUL),0) SERIALIZED_WEIGHT_BOXES,
          greatest(nvl((select MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY p where p.ARTICUL=l.ARTICUL),0),
            nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU g where g.ARTICUL=l.ARTICUL),0),
            case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE p where p.ARTICUL=l.ARTICUL) then 1 else 0 end) MARKING_REQUIRED
          from (select distinct ARTICUL from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:task and (:line is null or CASE_PICK_LINE_ID=:line)) l"""


def _device(policy: dict[str, Any]) -> str | None:
    if policy["marking_required"]:
        return "MARKING_SCAN_REQUIRED"
    if policy["serialized_weight_boxes"]:
        return "WEIGHT_LABEL_SCAN_REQUIRED"
    return None


class OracleCasePaper:
    def __init__(self, gateway: Any, assert_scope: Callable[[Any, int, str, str], None]) -> None:
        self.gateway, self.assert_scope = gateway, assert_scope  # existing native CASE scope, wired by the composition

    def snapshot(self, task: int, actor: str, line: int | None = None, expected_signature: str | None = None) -> dict[str, Any]:
        with self.gateway.transaction("CASE paper READ ONLY snapshot") as cur:
            cur.execute("set transaction read only")
            self.assert_scope(cur, task, actor, "case_pick_execute")
            bound = TransactionGateway(cur)
            head = bound.fetch_all(
                "select t.CASE_PICK_TASK_ID TASK_ID,t.WARE_ID,w.WAVE_CODE,co.ORDER_NO,c.CUSTOMER_NAME,t.SSCC,t.STATUS,t.ASSIGNED_TO,"
                "t.ASSIGNMENT_VERSION,t.CONTENT_VERSION from RRL_CASE_PICK_TASK t join RRL_PICK_WAVE w on w.PICK_WAVE_ID=t.PICK_WAVE_ID "
                "join RRL_CUSTOMER_ORDER co on co.CUSTOMER_ORDER_ID=t.CUSTOMER_ORDER_ID left join RRL_CUSTOMER c on c.CUSTOMER_ID=t.CUSTOMER_ID "
                "where t.CASE_PICK_TASK_ID=:task", {"task": task})
            if not head:
                raise CasePaperError("CASE_TASK_NOT_FOUND", 404)
            try:
                lines = bound.fetch_all(
                    "select CASE_PICK_LINE_ID LINE_ID,ARTICUL,PRODUCT_NAME,CELL_CODE,PICK_SEQUENCE,"
                    "to_char(PLANNED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PLANNED_QTY,"
                    "to_char(nvl(PICKED_QTY,0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PICKED_QTY,STATUS,REQUIRED_SCAN_MODE,"
                    "RRL_CASE_PICK_PAPER.line_signature(CASE_PICK_LINE_ID) SIGNATURE from RRL_CASE_PICK_LINE "
                    "where CASE_PICK_TASK_ID=:task and (:line is null or CASE_PICK_LINE_ID=:line) "
                    "order by PICK_SEQUENCE nulls last,CASE_PICK_LINE_ID fetch first :limit rows only",
                    {"task": task, "line": line, "limit": LINE_LIMIT + 1})
            except oracledb.DatabaseError as exc:  # NOT_APPLIED package: no version, so no sheet
                if getattr(exc.args[0], "code", 0) in {904, 4063, 4067, 6508, 6550}:
                    raise CasePaperError("CASE_PAPER_NOT_AVAILABLE", 503) from exc
                raise
            if line is not None and not lines:
                raise CasePaperError("CASE_LINE_NOT_FOUND", 404)
            if len(lines) > LINE_LIMIT:
                raise CasePaperError("CASE_PAPER_LINE_BOUND", 409)
            if expected_signature is not None and (line is None or lines[0]["signature"] != expected_signature):
                raise CasePaperError("CASE_PAPER_LINE_CHANGED", 409)
            policy = {row["articul"]: row for row in bound.fetch_all(POLICY, {"task": task, "line": line})}
            for item in lines:
                item["reference"], item["barcode_svg"] = case_line_barcode(task, item["line_id"], item["signature"])
                p = policy[item["articul"]]
                item["device_required"] = _device(p)
                item["scale_reading"] = bool(p["weighted_kg"]) and item["device_required"] is None  # manual scale: the reading is the fact
            return {"task": head[0], "lines": lines, "prepared_at": datetime.now(timezone.utc).isoformat()}
