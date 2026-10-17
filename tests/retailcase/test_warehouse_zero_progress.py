"""Durable zero intent and fail-closed current instruction; no hardware acceptance."""
import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import json
import time
import pytest
from api.wms_api_server.app.modules.integrations.application.warehouse_zero_progress import zero_event, validate_zero_ack
from api.wms_api_server.app.modules.integrations.contracts_scale_opc import OpcWeightObservation
from api.wms_api_server.app.modules.integrations.contracts_scales import ScaleGatewayError
from tests.retailcase.test_warehouse_scale_requests_gateway import capture_service


def sample():
    now = datetime.now(timezone.utc)
    stamp = now.isoformat()
    values = {name: dict(value=value, status_code=0, variant_type='Boolean', source_timestamp=stamp, server_timestamp=stamp)
              for name, value in dict(stable=True, center_zero=True, overload=False, underload=False, tare_mode=0,
                                    engineering_units=dict(namespace_uri='units', unit_id=17),
                                    current_weight=dict(Gross='0.0', Net='0.0', Tare='0.0')).items()}
    return OpcWeightObservation(Decimal(0), Decimal(0), Decimal(0), True, True, now,
                                dict(observed_at=stamp, values=values))


def claim():
    now = datetime.now(timezone.utc)
    return dict(request_id='request1', claim_id='claim1', device_id='scale1', state='CLAIMED',
                current_context='CURRENT', claim_created_at=(now-timedelta(seconds=1)).isoformat(),
                claim_expires_at=(now+timedelta(seconds=29)).isoformat(), zero_progress_required=True)


def ack(body, context):
    event = json.loads(body)
    receipt = {key: event[key] for key in ('claim_id', 'device_id', 'zero_observed_at', 'zero_source_sha256', 'profile_sha256')}
    receipt.update(request_id=context['request_id'], zero_confirmed=True, stock_posted=False,
                   source_sha256=hashlib.sha256(body).hexdigest().upper(), claim_expires_at=context['claim_expires_at'])
    current = dict(context, measurement_stage='ZERO_CONFIRMED', load_allowed=True,
                   zero_source_sha256=event['zero_source_sha256'], zero_confirmed_at=event['zero_observed_at'],
                   server_now=datetime.now(timezone.utc).isoformat())
    return dict(receipt=receipt, current=current)


@pytest.mark.parametrize('change', ['context', 'lease', 'load', 'hash', 'identity', 'stage'])
def test_historical_or_mismatched_receipt_never_instructs_loading(change):
    context = claim()
    body = zero_event(context, sample(), dict(unit_namespace_uri='units', kg_unit_id=17, no_tare_mode=0), 'A'*64)
    response = ack(body, context)
    validate_zero_ack(body, json.dumps(response).encode(), context)
    if change == 'context': response['current']['current_context'] = 'STALE'
    if change == 'lease': response['current']['server_now'] = context['claim_expires_at']
    if change == 'load': response['current']['load_allowed'] = False
    if change == 'hash': response['receipt']['source_sha256'] = 'F'*64
    if change == 'identity': response['current']['claim_id'] = 'foreign'
    if change == 'stage': response['current']['measurement_stage'] = 'INACTIVE'
    with pytest.raises(ScaleGatewayError, match='ZERO_ACK_REJECTED'):
        validate_zero_ack(body, json.dumps(response).encode(), context)


def test_lost_zero_ack_restart_reuses_original_bytes_without_new_opc_read(tmp_path):
    capture, _, _ = capture_service(tmp_path)
    capture.profile.update(unit_namespace_uri='units', kg_unit_id=17, no_tare_mode=0)
    context = claim()
    capture.station = capture.station.model_copy(update=dict(device_id=context['device_id']))
    capture.reader.read = lambda: read_zero()
    calls = []

    async def read_zero():
        calls.append('OPC_READ')
        return sample()

    class Api:
        fail = True
        bodies = []

        def confirm_zero(self, request_id, body):
            self.bodies.append(body)
            if self.fail: raise ScaleGatewayError('LOST_ZERO_ACK', True)
            return json.dumps(ack(body, context)).encode()

    api = Api()
    capture.api = api
    with pytest.raises(ScaleGatewayError, match='LOST_ZERO_ACK'):
        asyncio.run(capture._reported_zero(context, lambda: None, time.time()+29))
    original = capture.claims.zero(context['claim_id'])
    api.fail = False
    restored = asyncio.run(capture._reported_zero(context, lambda: None, time.time()+29))
    assert calls == ['OPC_READ'] and api.bodies == [original, original]
    assert restored.evidence == json.loads(json.loads(original)['zero_evidence_json'])
    with pytest.raises(ScaleGatewayError, match='IMMUTABLE_BODY'):
        capture.claims.stage_zero(context['request_id'], context['claim_id'], b'changed')


@pytest.mark.parametrize('stale_field', ['observed_at', 'current_weight', 'stable', 'center_zero',
                                      'overload', 'underload', 'tare_mode', 'engineering_units'])
def test_preclaim_zero_is_reread_before_durable_stage(tmp_path, monkeypatch, stale_field):
    capture, _, _ = capture_service(tmp_path)
    capture.profile.update(unit_namespace_uri='units', kg_unit_id=17, no_tare_mode=0)
    context = claim()
    fresh = sample()
    stale = sample()
    old = (datetime.fromisoformat(context['claim_created_at'])-timedelta(milliseconds=25)).isoformat()
    if stale_field == 'observed_at': stale.evidence['observed_at'] = old
    else: stale.evidence['values'][stale_field]['server_timestamp'] = old
    stale_before = json.dumps(stale.evidence, sort_keys=True)
    reads = []
    async def read():
        reads.append(1)
        return stale if len(reads) == 1 else fresh
    async def no_wait(_): pass
    monkeypatch.setattr(asyncio, 'sleep', no_wait)
    capture.reader.read = read
    bodies = []
    class Api:
        def confirm_zero(self, request_id, body):
            bodies.append(body)
            return json.dumps(ack(body, context)).encode()
    capture.api = Api()
    result = asyncio.run(capture._reported_zero(context, lambda: None, time.time()+29))
    assert len(reads) == 2 and result.evidence == fresh.evidence
    saved = capture.claims.zero(context['claim_id'])
    assert bodies == [saved]
    assert json.loads(json.loads(saved)['zero_evidence_json']) == fresh.evidence
    assert json.dumps(stale.evidence, sort_keys=True) == stale_before


def test_persistent_preclaim_clock_never_stages_zero(tmp_path, monkeypatch):
    capture, _, _ = capture_service(tmp_path)
    context = claim()
    stale = sample()
    stale.evidence['observed_at'] = (datetime.fromisoformat(context['claim_created_at'])-timedelta(seconds=1)).isoformat()
    reads = []
    async def read(): reads.append(1); return stale
    async def no_wait(_): pass
    monkeypatch.setattr(asyncio, 'sleep', no_wait)
    capture.reader.read = read
    def renew():
        if len(reads) >= 3: raise ScaleGatewayError('WAREHOUSE_CLAIM_LEASE_EXPIRED')
    with pytest.raises(ScaleGatewayError, match='CLAIM_LEASE_EXPIRED'):
        asyncio.run(capture._reported_zero(context, renew, time.time()+29))
    assert capture.claims.zero(context['claim_id']) is None
