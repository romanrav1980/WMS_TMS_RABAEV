"""One scoped read-only snapshot of immutable picks and registered aware intervals."""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
import json
from ..contracts_picker_kpi import PickerKpiError
from ..domain.picker_kpi import PickFact
from .picker_kpi_rows import rows, instant

STAMP = "'YYYY-MM-DD\"T\"HH24:MI:SS.FF6TZH:TZM'"


def fact(row: dict[str, Any]) -> PickFact:
    proof = json.loads(row["proof"]) if row["proof"] else {}
    previous, cumulative = Decimal(row["previous_qty"]), Decimal(row["fact_qty"])
    delta = cumulative - previous
    if proof and (Decimal(proof["delta_base"]) != delta or proof["base_uom"] != row["base_uom"]):
        raise ValueError("Frozen pick proof does not match quantity")
    return PickFact(row["operation_id"], row["actor"], instant(row["recorded_at"]),
        int(row["task_id"]), int(row["line_id"]), row["article"], row["base_uom"], previous,
        cumulative, Decimal(row["planned_qty"]), None if proof.get("boxes") is None else Decimal(proof["boxes"]),
        proof.get("reason") or ("HISTORICAL_PACKAGING_PROOF_UNAVAILABLE" if not proof else None),
        Decimal(proof["box_size_base"]) if proof.get("box_size_base") is not None else None, proof.get("input_kind"))


class PickerKpiRead:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def snapshot(self, warehouse: int, start: datetime, finish: datetime, actor: str,
                 operator: str | None) -> dict[str, Any]:
        with self.gateway.transaction("Scoped immutable picker KPI window") as q:
            q.execute("set transaction read only")
            selected = self._scope(q, warehouse, actor, operator)
            q.execute("select to_char(systimestamp at time zone 'UTC'," + STAMP + ") AT_UTC from dual")
            observed = instant(q.fetchone()[0])
            binds = {"warehouse": warehouse, "start_at": start.astimezone(timezone.utc).isoformat(timespec="microseconds"),
                "finish_at": min(finish.astimezone(timezone.utc), observed).isoformat(timespec="microseconds"), "operator": selected}
            picks = self._picks(q, binds)
            spans = self._spans(q, binds)
            q.execute("""select OPERATOR_ID,WARE_ID,SHIFT_STATE,WORK_STATE,SOURCE_KIND,SOURCE_ID,
                to_char(SHIFT_START_AT at time zone 'UTC',""" + STAMP + """) SHIFT_START,
                to_char(WORK_START_AT at time zone 'UTC',""" + STAMP + """) WORK_START,
                to_char(PAUSE_START_AT at time zone 'UTC',""" + STAMP + """) PAUSE_START
                from RRL_PICKER_TIME_STREAM where WARE_ID=:warehouse and SHIFT_STATE='OPEN'
                and(:operator is null or OPERATOR_ID=:operator) order by OPERATOR_ID fetch first 501 rows only""",
                warehouse=warehouse, operator=selected)
            active = rows(q)
            if len(active) > 500:
                raise PickerKpiError("KPI_OPERATOR_BOUND_500", 422)
            from .picker_kpi_quality_read import quality_snapshot
            facts = [fact(row) for row in picks]
            closures, returned = quality_snapshot(q, facts, warehouse, observed)
            return {"facts": facts, "closures": closures, "returns": returned, "spans": spans, "active": active,
                "as_of": observed, "selected_operator": selected}

    def _scope(self, q: Any, warehouse: int, actor: str, operator: str | None) -> str | None:
        q.execute("""select count(*) from RRL_WARES where ID=:w and
            RRL_ACCESS_API.allowed(:a,'case_pick_view','WAREHOUSE',:ware)=1""", w=warehouse, a=actor, ware=str(warehouse))
        if q.fetchone()[0] == 1:
            return operator
        if operator not in (None, actor):
            raise PickerKpiError("KPI_WAREHOUSE_FORBIDDEN", 403)
        q.execute("""select count(*) from RRL_WARES where ID=:w and
            RRL_ACCESS_API.allowed(:a,'case_pick_execute','WAREHOUSE',:ware,:a)=1""", w=warehouse, a=actor, ware=str(warehouse))
        if q.fetchone()[0] != 1:
            raise PickerKpiError("KPI_WAREHOUSE_FORBIDDEN", 403)
        return actor

    def _picks(self, q: Any, binds: dict[str, Any]) -> list[dict[str, Any]]:
        q.execute("""select c.OPERATION_ID,c.ACTOR,to_char(c.RECORDED_AT_UTC at time zone 'UTC',""" + STAMP + """) RECORDED_AT,
            json_value(o.RESOLVED_PLAN_JSON,'$.domain.task_id' returning number) TASK_ID,
            json_value(o.RESOLVED_PLAN_JSON,'$.domain.line_id' returning number) LINE_ID,
            json_value(o.RESOLVED_PLAN_JSON,'$.domain.article') ARTICLE,
            json_value(o.RESOLVED_PLAN_JSON,'$.domain.previous_qty') PREVIOUS_QTY,
            json_value(o.RESOLVED_PLAN_JSON,'$.domain.planned_qty') PLANNED_QTY,
            json_value(o.RESULT_JSON,'$.fact_qty') FACT_QTY,
            json_value(o.RESOLVED_PLAN_JSON,'$.domain.chunks[0].base') BASE_UOM,
            json_query(o.RESOLVED_PLAN_JSON,'$.domain.picker_kpi_proof' returning clob) PROOF
            from RRL_STOCK_OP_CLOCK c join RRL_STOCK_OPERATION o on o.OPERATION_ID=c.OPERATION_ID and o.STATE='APPLIED'
            where c.COMMAND_TYPE='CASE_PICK_CONFIRM'and c.RECORDED_AT_UTC>=to_timestamp_tz(:start_at,""" + STAMP + """)
            and c.RECORDED_AT_UTC<to_timestamp_tz(:finish_at,""" + STAMP + """)
            and json_value(o.RESOLVED_PLAN_JSON,'$.domain.warehouse' returning number)=:warehouse
            and(:operator is null or c.ACTOR=:operator)order by c.RECORDED_AT_UTC,c.OPERATION_ID fetch first 5001 rows only""", binds)
        result = rows(q)
        if len(result) > 5000:
            raise PickerKpiError("KPI_PICK_BOUND_5000", 422)
        return result

    def _spans(self, q: Any, binds: dict[str, Any]) -> list[dict[str, Any]]:
        q.execute("""select SPAN_ID,OPERATOR_ID,KIND,SOURCE_KIND,SOURCE_ID,SOURCE_MODE,
            to_char(START_AT at time zone 'UTC',""" + STAMP + """) START_AT,
            to_char(FINISH_AT at time zone 'UTC',""" + STAMP + """) FINISH_AT
            from RRL_PICKER_TIME_SPAN where WARE_ID=:warehouse
            and START_AT<to_timestamp_tz(:finish_at,""" + STAMP + """)and FINISH_AT>to_timestamp_tz(:start_at,""" + STAMP + """)
            and(:operator is null or OPERATOR_ID=:operator)order by START_AT,SPAN_ID fetch first 5001 rows only""", binds)
        result = rows(q)
        if len(result) > 5000:
            raise PickerKpiError("KPI_TIME_BOUND_5000", 422)
        return result
