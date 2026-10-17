"""Fault injection around local journal commits; no HTTP/native/hardware claim."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timedelta,timezone
import hashlib
import json
import time
import pytest
from api.wms_api_server.app.modules.integrations.infrastructure.scale_bundle_journal import SqliteScaleBundleJournal
from api.wms_api_server.app.modules.integrations.infrastructure.scale_outbox import SqliteScaleOutbox
from api.wms_api_server.app.modules.integrations.infrastructure.scale_device_lease import SqliteScaleDeviceLease
from api.wms_api_server.app.modules.integrations.application.assembly_opc_capture import OpcAssemblyCapture
from api.wms_api_server.app.modules.integrations.contracts_scales import ScaleGatewayError


def pair(weight='1',kind='WAREHOUSE_ASSEMBLY'):
    source=dict(device_id='d',capture_id='c',samples=[dict(weight_kg=weight)])
    canonical=json.dumps(source,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()
    body=json.dumps(source,indent=2).encode() # exact transport bytes survive, digest uses canonical source
    raw=json.dumps(dict(device_id='d',capture_id='c',capture_kind=kind,
        capture_sha256=hashlib.sha256(canonical).hexdigest().upper()),indent=1).encode()
    return body,raw


def boxes(root):
    return (SqliteScaleOutbox(root/'capture.sqlite'),SqliteScaleOutbox(root/'raw.sqlite',max_packet_bytes=131072))


@pytest.mark.parametrize('fail_after_capture',[False,True])
def test_restart_after_bundle_commit_or_between_mirrors_restores_exact_both(tmp_path,fail_after_capture):
    path=tmp_path/'bundle.sqlite';journal=SqliteScaleBundleJournal(path);body,raw=pair()
    journal.stage(body,raw)
    capture,evidence=boxes(tmp_path)
    if fail_after_capture:
        class CrashedRaw:
            def stage(self,_):raise OSError('simulated process crash before second mirror')
        with pytest.raises(OSError):journal.reconcile(capture,CrashedRaw())
        assert capture.has_capture('d','c') and not evidence.has_capture('d','c')
    # New objects model a new worker process with no memory of the measurement.
    restarted=SqliteScaleBundleJournal(path)
    restarted.reconcile(*boxes(tmp_path))
    capture,evidence=boxes(tmp_path)
    assert capture.claim(100).body==body
    assert evidence.claim(100).body==raw
    assert restarted.get('WAREHOUSE_ASSEMBLY','d','c')==(body,raw)


def test_conflicting_body_cannot_replace_either_original(tmp_path):
    journal=SqliteScaleBundleJournal(tmp_path/'bundle.sqlite');original=pair();journal.stage(*original)
    with pytest.raises(ScaleGatewayError,match='IMMUTABLE_CONFLICT'):journal.stage(*pair('2'))
    assert journal.get('WAREHOUSE_ASSEMBLY','d','c')==original


def test_two_journal_workers_same_original_and_mirror_ack_states_independent(tmp_path):
    path=tmp_path/'bundle.sqlite';SqliteScaleBundleJournal(path);original=pair()
    def work(_):
        journal=SqliteScaleBundleJournal(path);journal.stage(*original);journal.reconcile(*boxes(tmp_path))
    with ThreadPoolExecutor(max_workers=2)as pool:list(pool.map(work,range(2)))
    capture,raw=boxes(tmp_path);delivery=capture.claim(100);capture.acknowledge(delivery,b'capture ACK')
    SqliteScaleBundleJournal(path).reconcile(capture,raw)
    assert capture.claim(200)is None
    pending=raw.claim(100);assert pending.body==original[1]
    raw.acknowledge(pending,b'independent raw ACK')
    assert raw.claim(200)is None


@pytest.mark.parametrize('kind',['WAREHOUSE_ASSEMBLY','STORE_RECEIPT'])
def test_legacy_dangling_raw_blocks_new_measurement_until_explicit_reconciliation(tmp_path,kind):
    capture,raw=boxes(tmp_path);body,evidence=pair(kind=kind);raw.stage(evidence)
    journal=SqliteScaleBundleJournal(tmp_path/'bundles.sqlite')
    with pytest.raises(ScaleGatewayError,match='LEGACY_RAW_NEEDS_RECONCILIATION'):
        journal.reconcile(capture,raw)
    assert raw.claim(100).body==evidence # preserved, neither deleted nor acknowledged
    capture.stage(body) # external investigation recovers the actual original, not a new weight
    journal.reconcile(capture,raw)
    assert capture.claim(100).body==body


def test_legacy_capture_without_bundle_is_retained_for_delivery(tmp_path):
    capture,raw=boxes(tmp_path);body,_=pair();capture.stage(body)
    SqliteScaleBundleJournal(tmp_path/'bundles.sqlite').reconcile(capture,raw)
    assert capture.claim(100).body==body


def test_saved_bundle_is_reused_inside_device_lease_without_reading_again(tmp_path):
    journal=SqliteScaleBundleJournal(tmp_path/'bundle.sqlite');original=pair();journal.stage(*original)
    lease=SqliteScaleDeviceLease(tmp_path/'lease.sqlite')
    class Reader:
        async def read(self):raise AssertionError('fixed capture must never be measured again')
    service=OpcAssemblyCapture(Reader(),lease,{'device_id':'d'},'A'*64,journal)
    request=dict(device_id='d',capture_id='c',phase='BEFORE',expires_at=(datetime.now(timezone.utc)+timedelta(minutes=1)).isoformat())
    assert asyncio.run(service.capture(request))==original
    owner=lease.acquire('d',time.time(),10)
    try:
        with pytest.raises(ScaleGatewayError,match='DEVICE_BUSY'):
            asyncio.run(service.capture(request))
    finally:lease.release('d',owner)


@pytest.mark.parametrize('mutate',[lambda raw:raw.update(device_id='other'),lambda raw:raw.update(capture_sha256='0'*64),lambda raw:raw.update(capture_kind='UNKNOWN')])
def test_mismatched_pair_is_rejected_before_commit(tmp_path,mutate):
    body,raw=pair();value=json.loads(raw);mutate(value)
    journal=SqliteScaleBundleJournal(tmp_path/'bundle.sqlite')
    with pytest.raises(ValueError):journal.stage(body,json.dumps(value).encode())
    assert journal.get('WAREHOUSE_ASSEMBLY','d','c')is None

def test_crash_after_second_mirror_before_journal_marker_keeps_independent_raw_ack(tmp_path):
    path=tmp_path/'bundle.sqlite';journal=SqliteScaleBundleJournal(path);original=pair();journal.stage(*original)
    capture,raw=boxes(tmp_path)
    class CrashAfterRawCommit:
        def stage(self,body):
            raw.stage(body)
            raise OSError('crash after both mirrors before journal flag')
    with pytest.raises(OSError):journal.reconcile(capture,CrashAfterRawCommit())
    pending=raw.claim(100);raw.acknowledge(pending,b'raw ACK survived')
    SqliteScaleBundleJournal(path).reconcile(capture,raw)
    assert raw.claim(200)is None
    assert capture.claim(100).body==original[0]


def test_new_legacy_dangling_record_is_detected_after_initial_clean_scan(tmp_path):
    capture,raw=boxes(tmp_path);journal=SqliteScaleBundleJournal(tmp_path/'bundles.sqlite')
    journal.reconcile(capture,raw)
    _,evidence=pair();raw.stage(evidence)
    with pytest.raises(ScaleGatewayError,match='LEGACY_RAW_NEEDS_RECONCILIATION'):
        journal.reconcile(capture,raw)
