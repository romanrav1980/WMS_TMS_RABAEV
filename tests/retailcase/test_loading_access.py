import pytest
from app.modules.transport.contracts import TransportLoadingError
from app.modules.transport.infrastructure.loading_access import authorized_trip_header


class Snapshot:
    def __init__(self, user=(1, "LOCAL", 0), warehouses=(10,), allowed=(1,), owner="other"):
        self.values = iter([user, (100, "CAR", "DOCK", 1, None, owner), [(w,) for w in warehouses], *[(1, value) for value in allowed]])
        self.queries = []

    def execute(self, sql, **binds):
        self.queries.append((sql, binds))
        self.result = next(self.values)

    def fetchone(self):
        return self.result

    def fetchall(self):
        return self.result


def test_role_on_other_warehouse_does_not_require_legacy_flat_right():
    snapshot = Snapshot()
    assert authorized_trip_header(snapshot, 100, "actor")[0] == 100
    assert snapshot.queries[-1][1] == {"actor": "actor", "ware_id": 10}


def test_composite_trip_requires_every_current_warehouse():
    with pytest.raises(TransportLoadingError) as error:
        authorized_trip_header(Snapshot(warehouses=(10, 20), allowed=(1, 0)), 100, "actor")
    assert error.value.status == 403
    assert authorized_trip_header(Snapshot(warehouses=(10, 20), allowed=(1, 1)), 100, "actor")[0] == 100


def test_legacy_home_view_and_global_compatibility():
    assert authorized_trip_header(Snapshot(user=(10, "LOCAL", 1), allowed=(0,)), 100, "actor")
    assert authorized_trip_header(Snapshot(user=(1, " GLOBAL_ADMIN ", 1), allowed=(0,)), 100, "actor")


def test_empty_trip_does_not_invent_warehouse_for_role():
    with pytest.raises(TransportLoadingError) as error:
        authorized_trip_header(Snapshot(warehouses=(), allowed=(), owner="actor"), 100, "actor")
    assert error.value.code == "LOADING_EMPTY_TRIP_OWNER_REQUIRED"
    assert authorized_trip_header(Snapshot(user=(1, "LOCAL", 1), warehouses=(), allowed=(), owner="actor"), 100, "actor")


def test_missing_actor_stops_before_trip_and_contents():
    snapshot = Snapshot(user=None)
    with pytest.raises(TransportLoadingError):
        authorized_trip_header(snapshot, 100, "actor")
    assert len(snapshot.queries) == 1
