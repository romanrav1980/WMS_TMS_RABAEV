"""No stale-basis write, no straight-line fallback, and no provider call on replay."""
from contextlib import contextmanager
import pytest
from app.modules.transport.infrastructure import road_refresh as road
from app.modules.transport.contracts_plan import TransportPlanError


class Gateway:
    @contextmanager
    def transaction(self, label):
        yield self

    def execute(self, *args, **kwargs):
        pass


def basis(**changes):
    return dict(source_hash="a" * 64, route_input_version=0, source_issues=[], depot_basis="CONFIGURED_WAREHOUSE_REFERENCE",
                depot_address="DEPOT", stops=["STORE"], **changes)


BODY = dict(trip_id=1, expected_version=0, source_hash="a" * 64)


@pytest.fixture
def setup(monkeypatch):
    monkeypatch.setattr(road, "read_snapshot", lambda *args: basis())
    monkeypatch.setattr(road, "replay", lambda *args: None)
    monkeypatch.setattr(road, "coordinates", lambda *args, **kwargs: [(55.7, 37.6), (55.8, 37.7)])


def test_changed_source_prevents_provider_call(setup, monkeypatch):
    monkeypatch.setattr(road, "read_snapshot", lambda *args: dict(basis(), source_hash="b" * 64))
    with pytest.raises(TransportPlanError, match="изменились"):
        road.refresh_road(Gateway(), "op", BODY, "actor", lambda _: pytest.fail("stale provider call"))


def test_exact_replay_does_not_recompute_or_write(setup, monkeypatch):
    receipt = {"operation_id": "op", "trip_id": 1}
    monkeypatch.setattr(road, "replay", lambda *args: receipt)
    assert road.refresh_road(Gateway(), "op", BODY, "actor", lambda _: pytest.fail("recomputed replay")) == receipt


@pytest.mark.parametrize("provider", [None, lambda _: ("haversine", [[0, 1], [1, 0]], [[0, 2], [2, 0]]),
                                      lambda _: ("osrm", [[0, 1], [1, 0]], [[0, None], [2, 0]])])
def test_missing_or_invalid_provider_does_not_publish(setup, monkeypatch, provider):
    monkeypatch.setattr(road, "publish", lambda *args: pytest.fail("published invalid road data"))
    with pytest.raises(TransportPlanError) as error:
        road.refresh_road(Gateway(), "op", BODY, "actor", provider)
    assert error.value.status == 503


def test_only_a_configured_current_route_is_accepted():
    assert road.check_basis(basis(), BODY) == ["DEPOT", "STORE"]
    with pytest.raises(TransportPlanError):
        road.check_basis(dict(basis(), depot_basis="DISPATCHER_EXPLICIT_ADDRESS"), BODY)
