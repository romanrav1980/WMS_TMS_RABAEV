"""Bounded immutable shortage/return proof for the already authorized pick cohort."""
import json
from collections import defaultdict
from decimal import Decimal
from typing import Any
import oracledb
from ..contracts_picker_kpi import PickerKpiError
from ..domain.picker_kpi_quality import ShortCompletion, ReturnedLine
from .picker_kpi_rows import rows, instant

STAMP = "'YYYY-MM-DD\"T\"HH24:MI:SS.FF6TZH:TZM'"
COHORT = "json_table(:keys,'$[*]' columns(TASK_ID number path '$[0]',LINE_ID number path '$[1]'))"


def quality_snapshot(q: Any, facts: list[Any], warehouse: int, observed: Any) -> tuple[list[ShortCompletion], list[ReturnedLine]]:
    if not facts:
        return [], []
    keys = sorted({(fact.task_id, fact.line_id) for fact in facts})
    key_set = set(keys)
    value = q.var(oracledb.DB_TYPE_CLOB); value.setvalue(0, json.dumps(keys))
    binds = {"keys": value, "warehouse": warehouse, "observed": observed.isoformat(timespec="microseconds")}
    q.execute("""select o.OPERATION_ID,to_char(c.RECORDED_AT_UTC at time zone 'UTC',""" + STAMP + """) APPROVED_AT,
        k.TASK_ID,k.LINE_ID,json_value(o.RESOLVED_PLAN_JSON,'$.domain.picked') PICKED,
        json_value(o.RESOLVED_PLAN_JSON,'$.domain.planned') PLANNED,
        json_value(o.RESOLVED_PLAN_JSON,'$.domain.short') SHORTAGE
        from """ + COHORT + """ k join RRL_CASE_PICK_SHORT s on s.CASE_PICK_TASK_ID=k.TASK_ID and s.CASE_PICK_LINE_ID=k.LINE_ID
        join RRL_STOCK_OPERATION o on o.COMMAND_TYPE='CASE_SHORT_APPROVE'and o.STATE='APPLIED'
          and json_value(o.RESOLVED_PLAN_JSON,'$.domain.short_id' returning number)=s.CASE_PICK_SHORT_ID
        join RRL_STOCK_OP_CLOCK c on c.OPERATION_ID=o.OPERATION_ID
        where json_value(o.RESOLVED_PLAN_JSON,'$.domain.warehouse' returning number)=:warehouse
          and json_value(o.RESOLVED_PLAN_JSON,'$.domain.decision')in('ACCEPT_SHORT','WEIGHT_TOLERANCE')
          and json_value(o.RESOLVED_PLAN_JSON,'$.domain.picked' returning number)>0
          and c.RECORDED_AT_UTC<=to_timestamp_tz(:observed,""" + STAMP + """)
        order by c.RECORDED_AT_UTC,o.OPERATION_ID fetch first 5001 rows only""", binds)
    data = rows(q)
    if len(data) > 5000:
        raise PickerKpiError("KPI_QUALITY_BOUND_5000", 422)
    closures = [ShortCompletion(row["operation_id"], instant(row["approved_at"]), int(row["task_id"]),
        int(row["line_id"]), Decimal(row["picked"]), Decimal(row["planned"]), Decimal(row["shortage"])) for row in data]
    q.execute("""select o.OPERATION_ID,to_char(c.RECORDED_AT_UTC at time zone 'UTC',""" + STAMP + """) RETURNED_AT,
        k.TASK_ID,json_query(o.RESOLVED_PLAN_JSON,'$.domain.before' returning clob) STOCKS
        from(select distinct TASK_ID from """ + COHORT + """)k
        join RRL_STOCK_OPERATION o on o.COMMAND_TYPE='CASE_CARRIER_RETURN'and o.STATE='APPLIED'
          and json_value(o.RESOLVED_PLAN_JSON,'$.domain.task' returning number)=k.TASK_ID
        join RRL_STOCK_OP_CLOCK c on c.OPERATION_ID=o.OPERATION_ID
        where json_value(o.RESOLVED_PLAN_JSON,'$.domain.warehouse' returning number)=:warehouse
          and c.RECORDED_AT_UTC<=to_timestamp_tz(:observed,""" + STAMP + """)
        order by c.RECORDED_AT_UTC,o.OPERATION_ID fetch first 5001 rows only""", binds)
    data = rows(q)
    if len(data) > 5000:
        raise PickerKpiError("KPI_QUALITY_BOUND_5000", 422)
    returned = []
    for row in data:
        stocks = json.loads(row["stocks"])
        if not isinstance(stocks, list) or len(stocks) > 200:
            raise ValueError("Invalid bounded return proof")
        amounts: dict[tuple[int, str, str], Decimal] = defaultdict(Decimal)
        for stock in stocks:
            line = int(stock["case_line"])
            if (int(row["task_id"]), line) in key_set:
                amounts[(line, stock["article"], stock["base"])] += Decimal(stock["quantity"])
        returned.extend(ReturnedLine(row["operation_id"], instant(row["returned_at"]), int(row["task_id"]),
            line, article, unit, quantity) for (line, article, unit), quantity in amounts.items())
        if len(returned) > 5000:
            raise PickerKpiError("KPI_QUALITY_BOUND_5000", 422)
    return closures, returned
