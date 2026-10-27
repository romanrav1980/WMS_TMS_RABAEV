"""C-0177 offline: competing resource session openings get a confirmed answer, never an unknown 500."""
import sys
from pathlib import Path
from types import SimpleNamespace

import oracledb
import pytest
from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "api/wms_api_server"))
from app.modules.resources.infrastructure import session_lifecycle as lifecycle


class Cursor:
    def __init__(self, shift, twin=(None, None), capacity_count=0):
        self.shift, self.twins, self.count, self.sql = shift, list(twin), capacity_count, []

    def execute(self, sql, binds=None):
        self.sql.append(sql); self.last = sql

    def fetchone(self):
        if "from RRL_RESOURCE_SHIFT" in self.last:
            return self.shift
        if "select EQUIPMENT_ID,USER_ID" in self.last:
            return (7, "OP1")
        if "select WARE_ID,ACTIVE" in self.last:
            return (1, 1)
        if "count(*)" in self.last:
            return (self.count,)
        twin = self.twins.pop(0)
        return (twin,) if twin else None


class Gateway:
    def __init__(self, cursor):
        self.cursor = cursor

    def transaction(self, name):
        cursor = self.cursor

        class Scope:
            def __enter__(self): return cursor
            def __exit__(self, *exc): return False
        return Scope()


REQUEST = SimpleNamespace(shift_id=10, resource_id=20, equipment_id=None, operator_user_id="op1")


def violation(index, code=1):
    error = type("E", (), {"code": code, "__str__": lambda self: f"ORA-00001: unique constraint (TMS.{index}) violated"})()
    return oracledb.DatabaseError(error)


def failing(index, code=1):
    def create(gateway, body):
        raise violation(index, code)
    return create


@pytest.mark.parametrize("index,code", [("RRL_RESOURCE_SESSION_U3", "OPERATOR_ALREADY_IN_SESSION"),
                                        ("RRL_RESOURCE_SESSION_U2", "EQUIPMENT_ALREADY_IN_SESSION"),
                                        ("RRL_RESOURCE_SESSION_U1", "RESOURCE_ALREADY_IN_SESSION"), ("OTHER_PK", "RESOURCE_SESSION_CONFLICT")])
def test_losing_request_is_a_confirmed_409_naming_the_occupied_object(index, code):
    with pytest.raises(HTTPException) as refused:
        lifecycle.open_session(Gateway(Cursor((1, None, None, "OPEN"))), REQUEST, failing(index))
    assert refused.value.status_code == 409
    assert refused.value.detail == {"code": code, "outcome_confirmed": True}


def test_exact_repeat_returns_the_opened_session_without_a_second_insert():
    cursor = Cursor((1, None, None, "OPEN"), twin=(55,))
    assert lifecycle.open_session(Gateway(cursor), REQUEST, failing("RRL_RESOURCE_SESSION_U3")) == 55
    twin_binds = [s for s in cursor.sql if "upper(:op_user)" in s]
    assert len(twin_binds) == 1


def test_concurrent_identical_request_that_lost_the_index_returns_the_winner():
    assert lifecycle.open_session(Gateway(Cursor((1, None, None, "OPEN"), twin=(None, 56))), REQUEST, failing("RRL_RESOURCE_SESSION_U1")) == 56


def test_other_database_errors_are_not_masked():
    with pytest.raises(oracledb.DatabaseError):
        lifecycle.open_session(Gateway(Cursor((1, None, None, "OPEN"))), REQUEST, failing("X", code=60))


def test_reach_shift_repeat_of_a_seated_driver_is_not_refused_as_capacity():
    full = Cursor((1, "MAIN", 1, "OPEN"), twin=(57,), capacity_count=1)
    assert lifecycle.open_session(Gateway(full), REQUEST, failing("X")) == 57
    with pytest.raises(HTTPException) as refused:
        lifecycle.open_session(Gateway(Cursor((1, "MAIN", 1, "OPEN"), capacity_count=1)), REQUEST, failing("X"))
    assert refused.value.detail == "REACH_SHIFT_DRIVER_CAPACITY_REACHED"
