"""Planned dock intervals adapter: every write is one native RRL_YARD_DOCK_PLAN_API command; reads are one READ ONLY snapshot."""
import json
from datetime import datetime, timezone
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_yard_plan import YardError, YardPlanCancel, YardPlanCreate, YardPlanMove, wire

MISSING = (942, 4043, 6550)  # plan objects absent: the dock-plan migration is not applied here
UTC = "%Y-%m-%dT%H:%M:%S+00:00"


def error(exc: oracledb.DatabaseError) -> YardError:
    number = getattr(exc.args[0], "code", 0)
    if number in MISSING:
        return YardError("YARD_PLAN_NOT_AVAILABLE", 503)
    if not 20800 <= number <= 20999:
        return YardError("YARD_RESULT_UNKNOWN", 503)  # outcome unknown: repeat the same operation_id
    code = str(exc.args[0]).split("\n", 1)[0].split(":", 1)[-1].strip()
    return YardError(code, 403 if number == 20882 else 409)


def window(cur: Any, ware: int, actor: str, start: datetime, finish: datetime) -> dict[str, Any]:
    """Also used by the resource timeline inside its own READ ONLY snapshot."""
    return read_oracle_json(cur.callfunc("RRL_YARD_DOCK_PLAN_API.plans", oracledb.DB_TYPE_CLOB,
                                         [ware, actor, start.astimezone(timezone.utc).strftime(UTC),
                                          finish.astimezone(timezone.utc).strftime(UTC)]))


class OracleYardDockPlans:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def plans(self, ware: int, actor: str, start: datetime, finish: datetime) -> dict[str, Any]:
        try:
            with self.gateway.transaction("TRADECASE yard dock plans READ ONLY") as cur:
                cur.execute("set transaction read only")
                return dict(warehouse_id=ware, **window(cur, ware, actor, start, finish))
        except oracledb.DatabaseError as exc:
            raise error(exc) from exc

    def _command(self, ware: int, body: dict[str, Any], actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("TRADECASE yard dock plan command") as cur:
                request = cur.var(oracledb.DB_TYPE_CLOB)
                request.setvalue(0, json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_YARD_DOCK_PLAN_API.command", [ware, request, actor, result])
                receipt = read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            raise error(exc) from exc
        # A receipt is accepted only for this very operation; anything else is an unknown outcome (repeat the same operation_id).
        if not isinstance(receipt, dict) or receipt.get("operation_id") != body["operation_id"]:
            raise YardError("YARD_RESULT_UNKNOWN", 503)
        return receipt

    def plan(self, ware: int, body: YardPlanCreate, actor: str) -> dict[str, Any]:
        return self._command(ware, wire(body, action="PLAN"), actor)

    def move(self, ware: int, plan: int, body: YardPlanMove, actor: str) -> dict[str, Any]:
        return self._command(ware, wire(body, action="MOVE", plan_id=plan), actor)

    def cancel(self, ware: int, plan: int, body: YardPlanCancel, actor: str) -> dict[str, Any]:
        return self._command(ware, wire(body, action="CANCEL", plan_id=plan), actor)
