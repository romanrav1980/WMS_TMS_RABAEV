"""Hardware read ownership is fenced independently of HTTP packet delivery."""
from concurrent.futures import ThreadPoolExecutor
import pytest
from api.wms_api_server.app.modules.integrations.infrastructure.scale_device_lease import SqliteScaleDeviceLease
from api.wms_api_server.app.modules.integrations.contracts_scales import ScaleGatewayError


def test_two_readers_one_owner_and_old_worker_cannot_renew_or_release_new_owner(tmp_path):
    path = tmp_path/"lease.sqlite"
    lease = SqliteScaleDeviceLease(path)
    def acquire(_):
        try:
            return SqliteScaleDeviceLease(path).acquire("physical1", 100, 10)
        except ScaleGatewayError:
            return None
    with ThreadPoolExecutor(max_workers=2) as pool:
        owners = [item for item in pool.map(acquire, range(2)) if item]
    assert len(owners) == 1
    newer = lease.acquire("physical1", 111, 10)
    with pytest.raises(ScaleGatewayError, match="LEASE_LOST"):
        lease.renew("physical1", owners[0], 112, 10)
    lease.release("physical1", owners[0])
    with pytest.raises(ScaleGatewayError, match="BUSY"):
        lease.acquire("physical1", 112, 10)
    lease.release("physical1", newer)
    assert lease.acquire("physical1", 112, 10)


@pytest.mark.parametrize("now,seconds", [(float("nan"),10),(float("inf"),10),(-1,10),(1,0),(1,61)])
def test_invalid_lease_time_cannot_claim_a_device(tmp_path, now, seconds):
    lease = SqliteScaleDeviceLease(tmp_path/"lease.sqlite")
    with pytest.raises(ScaleGatewayError, match="CLOCK_INVALID"):
        lease.acquire("physical1", now, seconds)


def test_same_cached_server_observation_cannot_be_counted_as_two_samples(tmp_path):
    import asyncio
    from datetime import datetime, timezone
    from decimal import Decimal
    from api.wms_api_server.app.modules.integrations.application.scale_opc_capture import OpcStoreCapture
    from api.wms_api_server.app.modules.integrations.contracts_scale_opc import OpcWeightObservation
    now = datetime.now(timezone.utc)
    evidence = {"values":{"current_weight":{"server_timestamp":now.isoformat(timespec="microseconds")}}}
    zero = OpcWeightObservation(Decimal(0),Decimal(0),Decimal(0),True,True,now,evidence)
    value = OpcWeightObservation(Decimal(1),Decimal(1),Decimal(0),True,False,now,evidence)
    class Reader:
        async def read(self):
            return value
    service = OpcStoreCapture(Reader(),SqliteScaleDeviceLease(tmp_path/"lease.sqlite"),{"device_id":"d"},"A"*64)
    service.zero = zero
    with pytest.raises(ScaleGatewayError,match="TIME_NOT_ADVANCING"):
        asyncio.run(service.capture({"device_id":"d","state":"REQUESTED"}))
