"""Protocol vectors and crash/retry ownership; no hardware or Oracle simulation claim."""
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
import json
from pathlib import Path

import pytest

from api.wms_api_server.app.modules.integrations.domain.scale_sma import parse_sma_gross_kg
from api.wms_api_server.app.modules.integrations.infrastructure.scale_outbox import SqliteScaleOutbox


def frame(weight="12.345", status=" ", basis="G", motion=" ", unit="kg "):
    return ("\n" + status + "1" + basis + motion + " " + weight.rjust(10) + unit + "\r").encode("ascii")


def test_sma_preserves_decimal_and_observes_motion_without_inventing_stability():
    stable = parse_sma_gross_kg(frame())
    assert stable.gross_weight_kg == Decimal("12.345")
    assert stable.stable and not stable.center_zero
    assert not parse_sma_gross_kg(frame(motion="M")).stable
    assert parse_sma_gross_kg(frame("0.000", status="Z")).center_zero


@pytest.mark.parametrize("bad", [
    frame(status="O"), frame(status="U"), frame(status="E"), frame(status="I"),
    frame(status="T"), frame(basis="N"), frame(basis="g"), frame(unit="lb "),
    frame("-1"), frame("1", status="Z"), frame("NaN"), frame("1e3"),
    frame("1,25"), frame(motion="?"), b"\n?\r", frame() + frame(), frame()[1:],
])
def test_sma_rejects_faults_unsupported_basis_and_corrupt_frames(bad):
    with pytest.raises(ValueError):
        parse_sma_gross_kg(bad)


def test_capture_body_survives_restart_exactly_and_identity_conflict_is_rejected(tmp_path):
    path = tmp_path / "gateway.sqlite"
    body = b'{"device_id":"s1", "capture_id":"c1", "samples":[]}'
    first = SqliteScaleOutbox(path)
    key = first.stage(body)
    second = SqliteScaleOutbox(path)
    assert second.stage(body) == key
    with pytest.raises(ValueError, match="PAYLOAD_CONFLICT"):
        second.stage(body.replace(b'[]', b'[1]'))
    claimed = second.claim(100)
    assert claimed.body == body
    # Lost response/crash: new process retries original bytes, never a new capture ID.
    assert first.claim(101) is None
    recovered = first.claim(131)
    assert recovered.body == body and recovered.attempts == 2
    with pytest.raises(ValueError, match="LEASE_LOST"):
        second.acknowledge(claimed, b'{}')
    first.acknowledge(recovered, b'{"capture_key":"saved"}')
    assert second.claim(999) is None


def test_two_gateway_workers_have_one_owner_and_retry_has_a_due_time(tmp_path):
    path = tmp_path / "gateway.sqlite"
    outbox = SqliteScaleOutbox(path)
    outbox.stage(b'{"device_id":"s1","capture_id":"c1"}')
    with ThreadPoolExecutor(max_workers=2) as pool:
        claimed = list(pool.map(lambda _: SqliteScaleOutbox(path).claim(100), range(2)))
    owners = [item for item in claimed if item is not None]
    assert len(owners) == 1
    outbox.defer(owners[0], 150, "HTTP_TIMEOUT")
    assert outbox.claim(149) is None
    assert outbox.claim(150).body == owners[0].body


def test_published_wire_schema_matches_existing_authoritative_http_model():
    from api.wms_api_server.app.modules.delivery.api.store_scale_routes import ScalePacket
    root = Path(__file__).resolve().parents[2]
    schema = json.loads((root / "docs/integrations/store-scale-capture-v1.schema.json").read_text(encoding="utf-8"))
    assert schema == ScalePacket.model_json_schema()


@pytest.mark.parametrize("clock", [float("nan"), float("inf"), -1, True])
def test_outbox_rejects_bad_clock_before_it_can_steal_or_stall_a_lease(tmp_path, clock):
    outbox = SqliteScaleOutbox(tmp_path / "gateway.sqlite")
    outbox.stage(b'{"device_id":"s1","capture_id":"c1"}')
    with pytest.raises(ValueError, match="CLOCK_INVALID"):
        outbox.claim(clock)
    owner = outbox.claim(100)
    with pytest.raises(ValueError, match="CLOCK_INVALID"):
        outbox.defer(owner, clock, "bad")
    outbox.acknowledge(owner, b'{}')


def test_duplicate_identity_field_never_enters_the_retry_journal(tmp_path):
    outbox = SqliteScaleOutbox(tmp_path / "gateway.sqlite")
    with pytest.raises(ValueError, match="DUPLICATE_KEY"):
        outbox.stage(b'{"device_id":"other","device_id":"s1","capture_id":"c1"}')
    assert outbox.claim(100) is None
