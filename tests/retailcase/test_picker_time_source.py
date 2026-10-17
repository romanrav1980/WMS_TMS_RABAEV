"""Offline boundary/coverage proof; not Oracle attendance or native concurrency acceptance."""
import hashlib
import json
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from zoneinfo import ZoneInfo
import oracledb
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.wms_api_server.app.modules.resources.contracts_picker_time import PickerTimeCommand, PickerTimeError, picker_time_service
from api.wms_api_server.app.modules.resources.infrastructure.picker_time_native import PickerTimeNative, picker_time_canonical
from api.wms_api_server.app.modules.resources.application.picker_time_service import PickerTimeService
from api.wms_api_server.app.modules.resources.api.picker_time_routes import router
from api.wms_api_server.app.modules.platform.public import get_current_user

ACTOR = "TIME.TEST"
START = datetime(2026, 10, 15, 0, tzinfo=timezone.utc)
FINISH = START + timedelta(hours=8)


def body(**changes):
    data = dict(operation_id="TIME.OP1", action="ACTUAL_SHIFT_START", expected_version=0,
                resource_session_id=7, source_kind=None, source_id=None, reason="Explicit own presence confirmation")
    return PickerTimeCommand(**{**data, **changes})


def state(**changes):
    value = dict(operator_id=ACTOR, stream_version=1, shift_state="OPEN", work_state="IDLE", warehouse_id=99,
                 resource_session_id=7, resource_id=4, source_kind=None, source_id=None,
                 shift_started_at=START.isoformat(), work_started_at=None, pause_started_at=None,
                 last_event_at=START.isoformat(), work_coverage_certified=False, source_mode="MANUAL_CONFIRMED")
    return {**value, **changes}


def ack(request, **changes):
    value = dict(operation_id=request.operation_id, actor=ACTOR, action=request.action,
                 resource_session_id=request.resource_session_id, warehouse_id=99,
                 request_sha256=hashlib.sha256(picker_time_canonical(request).encode("utf-8")).hexdigest().upper(),
                 outcome="APPLIED", outcome_confirmed=True, changed=True, may_create_corrected_operation=False,
                 error_code=None, stock_posted=False, event_at=START.isoformat(), before_version=0, after_version=1, state=state())
    return {**value, **changes}


class Variable:
    def __init__(self, value): self.value = value
    def getvalue(self): return self.value


class Gateway:
    def __init__(self, response, error=None): self.response, self.error, self.events, self.calls = response, error, [], []
    @contextmanager
    def transaction(self, label):
        try: yield self
        except Exception: self.events.append("rollback"); raise
        else: self.events.append("commit")
    def execute(self, sql): self.calls.append(("sql", sql))
    def var(self, kind): return Variable(json.dumps(self.response))
    def callproc(self, method, args):
        self.calls.append((method, args[:-1]))
        if self.error: raise oracledb.DatabaseError(SimpleNamespace(code=self.error, message="Native refusal"))


def client(service):
    app = FastAPI(); app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(username=ACTOR, permissions=set())
    app.dependency_overrides[picker_time_service] = lambda: service
    return TestClient(app)


@pytest.mark.parametrize("changes", [{"actor": "other"}, {"confirmed": True}, {"event_at": START.isoformat()},
                                    {"expected_version": True}, {"resource_session_id": "7"}, {"reason": "        "},
                                    {"source_kind": "CASE_PICK_TASK", "source_id": 2}, {"action": "PLANNED_SHIFT_START"}])
def test_browser_actor_clocks_plans_and_untyped_commands_are_rejected(changes):
    with pytest.raises(ValueError): PickerTimeCommand.model_validate({**body().model_dump(), **changes})


def test_unicode_full_dto_hash_and_authenticated_actor_are_sent_before_commit():
    request = body(reason="Explicit confirmation \u0441\u043c\u0435\u043d\u044b \U0001f600")
    saved = ack(request); gateway = Gateway(saved)
    assert PickerTimeNative(gateway).command(request, ACTOR) == saved
    wire = gateway.calls[0][1][1]
    assert json.loads(wire)["source_kind"] is None and "\\u0441" not in wire
    assert gateway.calls[0][1][0] == ACTOR and gateway.events == ["commit"]


@pytest.mark.parametrize("changes", [{"actor": "other"}, {"operation_id": "other"}, {"request_sha256": "0" * 64},
                                    {"stock_posted": True}, {"stock_posted": 0}, {"outcome_confirmed": 1},
                                    {"after_version": 8}, {"resource_session_id": 8}, {"changed": 1}])
def test_wrong_or_nonboolean_ack_rolls_back_the_native_uow(changes):
    request = body(); gateway = Gateway(ack(request, **changes))
    with pytest.raises(PickerTimeError) as error: PickerTimeNative(gateway).command(request, ACTOR)
    assert error.value.status == 503 and gateway.events == ["rollback"]


def test_wrong_result_binding_and_action_state_cannot_commit():
    request = body()
    for patch in ({"resource_session_id": 8}, {"shift_state": "OFF", "shift_started_at": None}, {"stream_version": 2}):
        gateway = Gateway(ack(request, state=state(**patch)))
        with pytest.raises(PickerTimeError): PickerTimeNative(gateway).command(request, ACTOR)
        assert gateway.events == ["rollback"]


def test_known_rejected_receipt_commits_and_exact_get_is_readonly():
    request = body(expected_version=999)
    saved = ack(request, outcome="REJECTED", changed=False, may_create_corrected_operation=True,
                error_code="PICKER_TIME_EXPECTED_VERSION_CHANGED", event_at=None, before_version=1, after_version=1)
    gateway = Gateway(saved); api = client(PickerTimeService(PickerTimeNative(gateway)))
    first = api.post("/api/resources/picker-time/me/commands", json=request.model_dump())
    assert first.status_code == 409 and first.json() == saved and gateway.events == ["commit"]
    reread = api.get("/api/resources/picker-time/commands/TIME.OP1")
    assert reread.status_code == 200 and reread.json() == saved
    assert ("sql", "set transaction read only") in gateway.calls


@pytest.mark.parametrize("native,status", [(20882, 403), (20886, 409), (1403, 404), (3113, 503)])
def test_native_exceptions_are_not_definitive_receipts(native, status):
    request = body(); gateway = Gateway({}, native)
    response = client(PickerTimeService(PickerTimeNative(gateway))).post(
        "/api/resources/picker-time/me/commands", json=request.model_dump())
    assert response.status_code == status and response.json()["detail"]["outcome_confirmed"] is False
    assert response.json()["detail"]["operation_id"] == request.operation_id and gateway.events == ["rollback"]


def span(identity, kind, start, finish):
    return dict(span_id=identity, kind=kind, operator_id=ACTOR, warehouse_id=99, resource_session_id=7,
                source_kind="RESOURCE_SESSION" if kind == "ACTUAL_SHIFT" else "CASE_PICK_TASK",
                source_id=7 if kind == "ACTUAL_SHIFT" else 123, start_at=start.isoformat(), finish_at=finish.isoformat(),
                start_operation_id=identity + ".START", finish_operation_id=identity + ".FINISH", source_mode="MANUAL_CONFIRMED")


def snapshot(spans, **changes):
    value = dict(operator_id=ACTOR, report_start=START.isoformat(), report_finish=FINISH.isoformat(),
                 as_of=(FINISH + timedelta(seconds=1)).isoformat(), spans=spans,
                 state=state(stream_version=6, shift_state="OFF", shift_started_at=None, warehouse_id=None,
                             resource_id=None, resource_session_id=None, last_event_at=FINISH.isoformat()),
                 work_coverage_certified=False, actual_shift_coverage="CLOSED_CONFIRMED_WINDOWS_ONLY", snapshot="ORACLE_READ_ONLY")
    return {**value, **changes}


class NativeRead:
    def __init__(self, data): self.data, self.calls = data, []
    def window(self, start, finish, actor): self.calls.append((start, finish, actor)); return self.data


def test_closed_actual_shift_keeps_pause_but_manual_work_is_never_full_kpi_coverage():
    data = snapshot([span("S", "ACTUAL_SHIFT", START, FINISH), span("W", "WORK", START, FINISH),
                     span("P", "PAUSE", START + timedelta(hours=1), START + timedelta(hours=2))])
    result = PickerTimeService(NativeRead(data)).window(START, FINISH, ACTOR)
    assert result["denominators"]["actual_shift"]["hours"] == "8"
    assert result["denominators"]["actual_shift"]["duration_microseconds"] == 8 * 3600 * 1000000
    assert result["denominators"]["assembly"]["status"] == "NO_DATA"
    assert result["denominators"]["assembly"]["hours"] is None
    assert "WORK_OWNER_INSTRUMENTATION_NOT_CERTIFIED" in result["source_limitations"]


def test_open_shift_is_displayed_but_does_not_fabricate_a_finish_or_complete_coverage():
    data = snapshot([], state=state())
    result = PickerTimeService(NativeRead(data)).window(START, FINISH, ACTOR)
    assert result["state"]["shift_state"] == "OPEN" and result["spans"] == []
    assert result["denominators"]["actual_shift"]["status"] == "NO_DATA"


def test_maximum_operation_identity_keeps_native_span_trace_and_bounded_kernel_identity():
    identity = "X" * 100 + ":ACTUAL_SHIFT"
    data = snapshot([span(identity, "ACTUAL_SHIFT", START, FINISH)])
    result = PickerTimeService(NativeRead(data)).window(START, FINISH, ACTOR)
    assert result["denominators"]["actual_shift"]["status"] == "AVAILABLE"
    assert result["spans"][0]["span_id"] == identity


def test_gap_between_confirmed_shift_windows_is_not_silently_filled_as_off_duty():
    split = START + timedelta(hours=4)
    data = snapshot([span("S1", "ACTUAL_SHIFT", START, split),
                     span("S2", "ACTUAL_SHIFT", split + timedelta(microseconds=1), FINISH)])
    result = PickerTimeService(NativeRead(data)).window(START, FINISH, ACTOR)
    assert result["denominators"]["actual_shift"]["status"] == "NO_DATA"


@pytest.mark.parametrize("patch", [{"work_coverage_certified": True}, {"work_coverage_certified": 0},
                                 {"operator_id": "other"}, {"as_of": START.isoformat()}])
def test_wrong_actor_future_facts_or_fake_certification_are_not_source_coverage(patch):
    data = snapshot([span("S", "ACTUAL_SHIFT", START, FINISH)], **patch)
    with pytest.raises(PickerTimeError) as error: PickerTimeService(NativeRead(data)).window(START, FINISH, ACTOR)
    assert error.value.status == 503


def test_naive_or_unbounded_report_never_queries_source():
    source = NativeRead({}); service = PickerTimeService(source)
    for start, finish in ((START.replace(tzinfo=None), FINISH), (START, START + timedelta(days=32))):
        with pytest.raises(PickerTimeError) as error: service.window(start, finish, ACTOR)
        assert error.value.status == 422
    assert source.calls == []


def test_snapshot_bound_and_readonly_are_enforced_before_projection():
    data = snapshot([span("S", "ACTUAL_SHIFT", START, FINISH)])
    gateway = Gateway(data)
    assert PickerTimeNative(gateway).window(START, FINISH, ACTOR) == data
    assert ("sql", "set transaction read only") in gateway.calls
    oversized = deepcopy(data); oversized["spans"] *= 5001
    with pytest.raises(PickerTimeError): PickerTimeNative(Gateway(oversized)).window(START, FINISH, ACTOR)


def test_source_window_normalizes_dst_fold_before_order_and_elapsed_bound():
    berlin = ZoneInfo("Europe/Berlin")
    start = datetime(2026, 10, 25, 2, 30, tzinfo=berlin, fold=0)
    finish = datetime(2026, 10, 25, 2, 15, tzinfo=berlin, fold=1)
    left, right = start.astimezone(timezone.utc), finish.astimezone(timezone.utc)
    data = snapshot([span("DST", "ACTUAL_SHIFT", start, finish)], report_start=left.isoformat(),
                    report_finish=right.isoformat(), as_of=(right + timedelta(seconds=1)).isoformat(),
                    state=state(stream_version=2, shift_state="OFF", shift_started_at=None, warehouse_id=None,
                                resource_session_id=None, resource_id=None, last_event_at=right.isoformat()))
    source = NativeRead(data)
    result = PickerTimeService(source).window(start, finish, ACTOR)
    assert source.calls == [(left, right, ACTOR)]
    assert result["denominators"]["actual_shift"]["duration_microseconds"] == 45 * 60 * 1000000
