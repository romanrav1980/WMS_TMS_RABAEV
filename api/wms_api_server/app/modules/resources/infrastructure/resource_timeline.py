"""Native scoped admission and bounded existing source projections, no business writes."""
from datetime import datetime, timedelta, timezone
from typing import Any
import oracledb
from ..contracts_timeline import TimelineError, TimelineClockReader
from ..domain.timeline_intervals import overlap_candidates, overlaps
from ...platform.public import read_oracle_json
from .timeline_projection import TimelineProjection
from .timeline_queries import resource_rows, attendance_rows, task_rows, dock_rows, transport_rows, case_rows
from .timeline_queries import qualification_rows, session_rows, loading_rows


class ResourceTimeline:
    def __init__(self, gateway: Any, clock_reader: TimelineClockReader | None = None) -> None:
        self.gateway = gateway
        self.clock_reader = clock_reader

    def read(self, warehouse: int, start: datetime, finish: datetime, actor: str) -> dict[str, Any]:
        if start.tzinfo is None or finish.tzinfo is None or finish <= start or finish - start > timedelta(days=7):
            raise TimelineError("RESOURCE_TIMELINE_INVALID_WINDOW", 422)
        projection = TimelineProjection(warehouse)
        try:
            with self.gateway.transaction("Resource timeline native scoped read") as cur:
                if not getattr(self.gateway, "transaction_bound", False):
                    cur.execute("set transaction read only")
                cur.execute("select RRL_ACCESS_API.allowed(:actor,'resource_gantt_view','WAREHOUSE',:ware) from dual",
                            actor=actor, ware=str(warehouse))
                if cur.fetchone()[0] != 1:
                    raise TimelineError("RESOURCE_TIMELINE_ACCESS_DENIED", 403)
                cur.execute("select count(*) from RRL_WARES where ID=:ware", ware=warehouse)
                if cur.fetchone()[0] != 1:
                    raise TimelineError("WAREHOUSE_NOT_FOUND", 404)
                sources = self._sources(cur, warehouse, actor)
                self._read_sources(cur, projection, sources, start, finish, actor)
                cur.execute("select REVISION from RRL_ACCESS_REV where ID=1")
                revision = cur.fetchone()[0]
        except oracledb.DatabaseError as error:
            code = getattr(error.args[0], "code", 0)
            raise TimelineError("RESOURCE_TIMELINE_ACCESS_DENIED" if code in (20851,20882) else "RESOURCE_TIMELINE_UNAVAILABLE",
                                403 if code in (20851,20882) else 503) from error
        now = datetime.now(timezone.utc)
        events, unscheduled = [], []
        for event in projection.events:
            if overlaps(event.get("plan_start_at"), event.get("plan_finish_at"), start, finish) or overlaps(
                    event.get("fact_start_at"), event.get("fact_finish_at"), start, finish):
                events.append(event)
            elif event["time_status"] == "TIME_UNRESOLVED":
                unscheduled.append(event)
        bindings = [{"event_id": event, "resource_id": resource} for event, resource in sorted(projection.bindings)]
        return {"warehouse_id": warehouse, "start_at": start.isoformat(), "finish_at": finish.isoformat(),
                "observed_at": now.isoformat(), "access_revision": revision, "warehouse_time_zone": None,
                "resources": list(projection.resources.values()), "events": events, "unscheduled": unscheduled,
                "assignments": bindings, "sources": sources,
                "overlap_candidates": overlap_candidates(events, bindings, now, finish), "overlap_limit": 200,
                "time_policy": "AWARE_ONLY_LEGACY_LOCAL_UNRESOLVED", "snapshot": "ORACLE_READ_ONLY",
                "commands_executed": False}

    @staticmethod
    def _sources(cur: Any, warehouse: int, actor: str) -> list[dict[str, Any]]:
        permissions = {"registry": "resource_management_view", "attendance": "resource_shift_view",
                       "warehouse_tasks": "warehouse_task_view", "case_tasks": "case_pick_view", "transport": "transport_dispatch_view",
                       "sessions": "resource_session_view", "yard": "tradecase_view"}
        result = []
        for name, permission in permissions.items():
            cur.execute("select RRL_ACCESS_API.allowed(:actor,:permission,'WAREHOUSE',:ware) from dual",
                        actor=actor, permission=permission, ware=str(warehouse))
            result.append({"source_id": name, "status": "READY" if cur.fetchone()[0] == 1 else "FORBIDDEN",
                           "permission": permission, "limit": 500 if name in {"registry", "attendance"} else 2000})
        return result

    def _read_sources(self, cur: Any, projection: TimelineProjection, sources: list[dict[str, Any]],
                      start: datetime, finish: datetime, actor: str) -> None:
        allowed = {source["source_id"] for source in sources if source["status"] == "READY"}
        warehouse = projection.warehouse
        if "registry" in allowed:
            projection.registry(*resource_rows(cur, warehouse))
            for row in qualification_rows(cur, warehouse):
                projection.qualification(row)
        if "sessions" in allowed:
            for row in session_rows(cur, warehouse):
                projection.session(row)
        if "attendance" in allowed:
            for row in attendance_rows(cur, warehouse, start, finish):
                projection.attendance(row)
        if "warehouse_tasks" in allowed:
            for row in task_rows(cur, {"ware": warehouse, "actor": actor, "start_at": start, "finish_at": finish}):
                projection.task(row)
        if "case_tasks" in allowed:
            for row in case_rows(cur, {"ware": warehouse, "finish_at": finish, "view_actor": actor,
                                      "local_start": start.replace(tzinfo=None) - timedelta(days=1)}):
                projection.case_task(row)
        if "transport" in allowed:
            for row in dock_rows(cur, warehouse):
                projection.lane(f"DOCK:{warehouse}:{row['dock']}", "DOCK", row["dock"],
                                "BLOCKED" if row["dock_is_blocked"] else "UNKNOWN")
            # Broad candidate window only: local dates are never asserted to be UTC instants.
            params = {"ware": warehouse, "actor": actor, "local_start": start.replace(tzinfo=None) - timedelta(days=1),
                      "local_finish": finish.replace(tzinfo=None) + timedelta(days=1)}
            transport = transport_rows(cur, params)
            approved_trips = {int(row["tt_id"]) for row in transport if row["approval_version"] is not None}
            if len(approved_trips) > 50:
                raise TimelineError("TIMELINE_APPROVAL_BOUND_50_NARROW_WINDOW", 409)
            clocks = {trip: self.clock_reader(cur, trip, actor) for trip in sorted(approved_trips)} if self.clock_reader else {}
            for row in transport:
                clock = clocks.get(int(row["tt_id"]), {})
                row["clock_status"] = clock.get("status", "NO_APPROVAL")
                row["clock_time_zone"] = clock.get("time_zone")
                row["clock_version"] = clock.get("version")
                row["aware_operation"] = clock.get("operations", {}).get(int(row["op_id"]))
                projection.transport(row)
            for row in loading_rows(cur, {"ware": warehouse, "actor": actor, "start_at": start, "finish_at": finish}):
                projection.loading(row)
        if "yard" in allowed:
            # Active visits only, through the owner-filtered native read; absent before the migration is applied.
            try:
                rows = read_oracle_json(cur.callfunc("RRL_YARD_VISIT_API.visits", oracledb.DB_TYPE_CLOB, [warehouse, actor, 1]))
            except oracledb.DatabaseError as error:
                if getattr(error.args[0], "code", 0) not in (4043, 6550):
                    raise
                next(source for source in sources if source["source_id"] == "yard")["status"] = "NOT_MAPPED"
            else:
                for row in rows["visits"]:
                    projection.yard(row)
        completed_at = datetime.now(timezone.utc).isoformat()
        for source in sources:
            source["observed_at"] = completed_at if source["status"] == "READY" else None
