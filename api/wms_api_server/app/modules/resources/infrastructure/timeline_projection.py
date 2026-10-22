"""Adapt existing resource identities to a single event with multiple bindings."""
from typing import Any


class TimelineProjection:
    def __init__(self, warehouse: int) -> None:
        self.warehouse = warehouse
        self.resources: dict[str, dict[str, Any]] = {}
        self.events: list[dict[str, Any]] = []
        self.event_ids: set[str] = set()
        self.bindings: set[tuple[str, str]] = set()
        self.person: dict[str, str] = {}
        self.original: dict[int, str] = {}

    def lane(self, key: str, kind: str, label: str, state: str | None = None) -> str:
        self.resources[key] = {"resource_id": key, "kind": kind, "label": label,
                               "warehouse_id": self.warehouse, "source_state": state, "availability": "UNKNOWN",
                               "zone_code": None, "qualifications": None, "last_signal": None}
        return key

    def registry(self, resources: list[dict[str, Any]], equipment: list[dict[str, Any]]) -> None:
        for row in equipment:
            self.lane(f"EQUIPMENT:{row['equipment_id']}", row["equipment_type"],
                      row["equipment_name"] or row["equipment_code"], row["service_status"])
            self.resources[f"EQUIPMENT:{row['equipment_id']}"]["zone_code"] = row["home_zone_code"]
        for row in resources:
            equipment_key = f"EQUIPMENT:{row['equipment_id']}"
            key = equipment_key if row["equipment_id"] is not None and equipment_key in self.resources else f"RESOURCE:{row['resource_id']}"
            if key not in self.resources:
                self.lane(key, row["resource_type"], row["resource_name"] or row["resource_code"], row["status"])
            self.original[int(row["resource_id"])] = key
            self.resources[key]["zone_code"] = row["zone_code"] or self.resources[key]["zone_code"]
            self.resources[key]["qualifications"] = []
            if row["user_id"]:
                self.person[str(row["user_id"]).strip().lower()] = key

    def qualification(self, row: dict[str, Any]) -> None:
        key = self.original.get(int(row["resource_id"]))
        if key is not None:
            self.resources[key]["qualifications"].append({"source_resource_id": row["resource_id"],
                "task_type": row["task_type"], "current_by_native_policy": True,
                "legacy_valid_from": row["legacy_valid_from"], "legacy_valid_until": row["legacy_valid_until"],
                "time_status": "UNRESOLVED_SERVER_LOCAL"})

    def session(self, row: dict[str, Any]) -> None:
        key = self.original.get(int(row["resource_id"]))
        if key is None:
            key = self.lane(f"RESOURCE:{row['resource_id']}", row["resource_type"], row["resource_name"] or row["resource_code"])
            self.original[int(row["resource_id"])] = key
        self.resources[key]["last_signal"] = {"session_id": row["session_id"], "aware_at": None,
            "legacy_at": row["last_signal_local"], "time_status": "UNRESOLVED_SERVER_LOCAL",
            "recent_by_native_server_clock": bool(row["signal_recent"])}
        self.resources[key]["zone_code"] = row["zone_code"] or self.resources[key]["zone_code"]

    def add(self, event: dict[str, Any], lanes: list[str | None]) -> None:
        if event["event_id"] not in self.event_ids:
            self.events.append(event)
            self.event_ids.add(event["event_id"])
        for key in lanes:
            if key is not None and key in self.resources:
                self.bindings.add((event["event_id"], key))

    def attendance(self, row: dict[str, Any]) -> None:
        self.add({"event_id": "ATTENDANCE:" + row["plan_operation_id"], "kind": "ATTENDANCE",
                  "label": "План выхода", "source": "RRL_WORKLOAD_ATTENDANCE", "source_id": row["plan_operation_id"],
                  "plan_start_at": row["start_at"], "plan_finish_at": row["finish_at"],
                  "fact_start_at": None, "fact_finish_at": None, "time_status": "AWARE_PLAN"},
                 [self.original.get(int(row["resource_id"]))])

    def task(self, row: dict[str, Any]) -> None:
        self.add({"event_id": f"WAREHOUSE_TASK:{row['task_id']}", "kind": "WAREHOUSE_TASK",
                  "label": f"{row['task_type']} · {row['task_id']}", "source": "RRL_WAREHOUSE_TASK", "source_id": row["task_id"],
                  "status": row["status"], "plan_start_at": None, "plan_finish_at": None,
                  "task_source": row["task_source"], "source_task_id": row["source_task_id"],
                  "wave_id": row["source_doc_id"] if row["source_doc_type"] == "PICK_WAVE" else None,
                  "fact_start_at": row["fact_start_at"], "fact_finish_at": row["fact_finish_at"],
                  "time_status": "AWARE_FACT" if row["fact_start_at"] else "TIME_UNRESOLVED",
                  "legacy_time": {"plan_start": row["plan_local_start"], "plan_finish": row["plan_local_finish"]},
                  "blocking_reason": row["blocking_reason"]},
                 [self.original.get(row["resource_id"]), f"EQUIPMENT:{row['equipment_id']}",
                  self.person.get(str(row["assigned_to"] or "").strip().lower())])

    def transport(self, row: dict[str, Any]) -> None:
        lanes: list[str | None] = []
        if row["transport"]:
            lanes.append(self.lane("VEHICLE:" + row["transport"].strip().upper(), "VEHICLE", row["transport"]))
        dock = f"DOCK:{self.warehouse}:{row['dock']}"
        # Only a loading operation consumes the warehouse loading dock; driving does not.
        if row["operation_code"] == "LOADING" and dock in self.resources:
            lanes.append(dock)
        aware = row.get("aware_operation") or {}
        self.add({"event_id": f"TRANSPORT_OPERATION:{row['op_id']}", "kind": "TRANSPORT_OPERATION",
                  "label": f"{row['operation_code']} · рейс {row['tt_id']}", "source": "RRL_TT_OPERATIONS",
                  "source_id": row["op_id"], "trip_id": row["tt_id"], "plan_start_at": aware.get("plan_start_at"),
                  "plan_finish_at": aware.get("plan_end_at"), "fact_start_at": aware.get("fact_start_at"),
                  "fact_finish_at": aware.get("fact_end_at"), "time_status": "AWARE_APPROVED" if aware else "TIME_UNRESOLVED",
                  "approval_status": row.get("clock_status"), "approval_version": row.get("clock_version"),
                  "time_zone_source": row.get("clock_time_zone"),
                  "legacy_time": {"plan_start": row["plan_local_start"], "plan_finish": row["plan_local_finish"],
                                  "fact_start": row["fact_local_start"], "fact_finish": row["fact_local_finish"]}}, lanes)

    def loading(self, row: dict[str, Any]) -> None:
        vehicle = None
        if row["vehicle_number"]:
            vehicle = "VEHICLE:" + row["vehicle_number"].strip().upper()
            if vehicle not in self.resources:
                self.lane(vehicle, "VEHICLE", row["vehicle_number"])
        dock = f"DOCK:{self.warehouse}:{row['dock']}" if row["dock"] else None
        if dock and dock not in self.resources:
            self.lane(dock, "DOCK", row["dock"], "HISTORICAL")
        for kind, operation, at, label, lanes in [
            ("LOAD_CONFIRMATION", row["load_operation_id"], row["loaded_at"], "Погрузка подтверждена", [vehicle, dock]),
            ("TRIP_DEPARTURE", row["departure_operation_id"], row["departed_at"], "Выезд подтверждён", [vehicle]),
        ]:
            if operation and at:
                self.add({"event_id": f"{kind}:{operation}", "kind": kind, "label": f"{label} · рейс {row['tt_id']}",
                          "source": "RRL_TT_HU_LOAD_FACT", "source_id": operation, "trip_id": row["tt_id"],
                          "status": "DONE", "plan_start_at": None, "plan_finish_at": None,
                          "fact_start_at": at, "fact_finish_at": at, "time_status": "AWARE_FACT"}, lanes)

    def case_task(self, row: dict[str, Any]) -> None:
        # The query supplies only aware STARTED_AT_INSTANT; a legacy finish is not an end instant.
        ongoing = bool(row["fact_start_at"]) and row["status"] in {"IN_PROGRESS", "PARTIAL", "WAIT_REPLENISHMENT"}
        self.add({"event_id": f"CASE_PICK_TASK:{row['case_pick_task_id']}", "kind": "CASE_PICK_TASK",
                  "label": f"Сборка {row['case_pick_task_id']} · волна {row['pick_wave_id']}",
                  "source": "RRL_CASE_PICK_TASK", "source_id": row["case_pick_task_id"], "wave_id": row["pick_wave_id"],
                  "status": row["status"], "total_lines": row["total_lines"], "picked_lines": row["picked_lines"],
                  "plan_start_at": None, "plan_finish_at": None, "fact_start_at": row["fact_start_at"], "fact_finish_at": None,
                  "time_status": "AWARE_FACT" if row["fact_start_at"] else "TIME_UNRESOLVED",
                  "legacy_time": {"fact_finish": row["fact_local_finish"]}, "fact_finish_status": "OPEN" if ongoing else "UNRESOLVED"},
                 [self.original.get(row["resource_id"]), f"EQUIPMENT:{row['equipment_id']}",
                  self.person.get(str(row["assigned_to"] or "").strip().lower())])

    def yard(self, row: dict[str, Any]) -> None:
        # Intervals come from the visit's immutable event times. The vehicle is held from ARRIVE to DEPART/CANCEL; each dock from its
        # (re)assignment to the next reassignment, DEPART or CANCEL. Different starts are separate events; an open end stays open
        # (occupied up to the read, never projected into the future).
        visit, state = row["visit_id"], row["state"]
        vehicle = "VEHICLE:" + row["vehicle"] if row.get("vehicle") else None  # stored upper/trim, as the transport lanes
        if vehicle and vehicle not in self.resources:
            self.lane(vehicle, "VEHICLE", row["vehicle"])
        arrived = finished = None
        docks: list[list[Any]] = []
        for event in row["events"]:
            if event["action"] == "ARRIVE":
                arrived = event["at"]
            elif event["action"] in {"ASSIGN_DOCK", "REASSIGN_DOCK"}:
                if docks and docks[-1][2] is None:
                    docks[-1][2] = event["at"]
                docks.append([event["dock"], event["at"], None])
            elif event["action"] in {"DEPART", "CANCEL"}:
                finished = event["at"]
                if docks and docks[-1][2] is None:
                    docks[-1][2] = finished
        plan = row.get("planned_arrival_at") if state == "EXPECTED" else None
        base = {"source": "RRL_YARD_VISIT", "source_id": visit, "trip_id": row["trip_id"], "plan_start_at": None, "plan_finish_at": None}
        self.add({**base, "event_id": f"YARD_VISIT:{visit}", "kind": "YARD_VISIT", "label": f"Визит {visit} · рейс {row['trip_id']}",
                  "status": state, "plan_start_at": plan, "plan_finish_at": plan, "fact_start_at": arrived,
                  "fact_finish_at": finished if arrived else None,
                  "time_status": "AWARE_FACT" if arrived else "AWARE_PLAN" if plan else "TIME_UNRESOLVED",
                  "fact_finish_status": ("CLOSED" if finished else "OPEN") if arrived else "UNRESOLVED"}, [vehicle])
        for number, (dock, start, end) in enumerate(docks, 1):
            lane = f"DOCK:{self.warehouse}:{dock}"
            if lane not in self.resources:
                self.lane(lane, "DOCK", dock, "UNKNOWN")
            self.add({**base, "event_id": f"YARD_DOCK:{visit}:{number}", "kind": "YARD_DOCK", "label": f"Ворота {dock} · визит {visit}",
                      "status": "DONE" if end else state, "fact_start_at": start, "fact_finish_at": end, "time_status": "AWARE_FACT",
                      "fact_finish_status": "CLOSED" if end else "OPEN"}, [lane])
