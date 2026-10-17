from datetime import timedelta
import pytest
from pydantic import ValidationError
from fastapi import HTTPException
from app.modules.delivery.api.delivery_time_routes import WindowCommand, ArrivalCommand, canonical, plan_window


def body(**changes):
    return dict(operation_id="T.W1", load_operation_id="T.LOAD", store_address="STORE",
        reason="Confirmed planning", expected_version=0, window_start="2026-10-16T13:00:00+03:00",
        window_finish="2026-10-16T14:00:00+03:00", **changes)


def test_same_instants_have_same_canonical_retry_payload():
    first = WindowCommand(**body())
    second = first.model_copy(update={"window_start": first.window_start - timedelta(0)})
    assert canonical(first) == canonical(second)
    assert canonical(first)["window_start"] == "2026-10-16T10:00:00.000000+00:00"


def test_naive_time_and_client_actor_are_rejected():
    values = body(); values["window_start"] = "2026-10-16T13:00:00"
    with pytest.raises(ValidationError):
        WindowCommand(**values)
    with pytest.raises(ValidationError):
        ArrivalCommand(operation_id="A", load_operation_id="L", store_address="S", reason="Confirmed arrival", actor="admin")


def test_unknown_arrival_time_stays_absent_for_native_database_clock():
    request = ArrivalCommand(operation_id="A", load_operation_id="L", store_address="S", reason="Confirmed arrival")
    assert "arrived_at" not in canonical(request)


def test_reversed_window_never_reaches_native_command():
    values = body(); values["window_finish"] = "2026-10-16T12:00:00+03:00"
    with pytest.raises(HTTPException) as caught:
        plan_window(WindowCommand(**values), None, None)
    assert caught.value.status_code == 422
