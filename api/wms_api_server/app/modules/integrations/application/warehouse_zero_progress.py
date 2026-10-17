"""Report the original instrument zero before the operator is told to load it."""
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from typing import Any
from ..contracts_scale_opc import OpcWeightObservation
from ..contracts_scales import ScaleGatewayError
from .warehouse_scale_ack import unique_object


def zero_event(claim: dict[str, Any], zero: OpcWeightObservation,
               profile: dict[str, Any], digest: str) -> bytes:
    evidence = json.dumps(zero.evidence, ensure_ascii=True, sort_keys=True, separators=(',', ':'))
    body = dict(claim_id=claim['claim_id'], device_id=claim['device_id'],
                zero_observed_at=zero.evidence['values']['current_weight']['server_timestamp'],
                zero_source_sha256=hashlib.sha256(evidence.encode()).hexdigest().upper(),
                zero_evidence_json=evidence, profile_sha256=digest.upper(),
                unit_namespace_uri=profile['unit_namespace_uri'], kg_unit_id=profile['kg_unit_id'],
                no_tare_mode=profile['no_tare_mode'])
    return json.dumps(body, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode()


def restore_zero(body: bytes, claim: dict[str, Any], profile_digest: str) -> OpcWeightObservation:
    event = json.loads(body)
    if event['claim_id'] != claim['claim_id'] or event['device_id'] != claim['device_id']:
        raise ScaleGatewayError('WAREHOUSE_SAVED_ZERO_CLAIM_CONFLICT')
    if event['profile_sha256'] != profile_digest.upper():
        raise ScaleGatewayError('WAREHOUSE_SAVED_ZERO_PROFILE_CHANGED')
    evidence = json.loads(event['zero_evidence_json'])
    if hashlib.sha256(event['zero_evidence_json'].encode()).hexdigest().upper() != event['zero_source_sha256']:
        raise ScaleGatewayError('WAREHOUSE_SAVED_ZERO_HASH_CONFLICT')
    values = evidence['values']
    mass = [Decimal(values['current_weight']['value'][name]) for name in ('Gross', 'Net', 'Tare')]
    if any(mass) or values['stable']['value'] is not True or values['center_zero']['value'] is not True:
        raise ScaleGatewayError('WAREHOUSE_SAVED_ACTUAL_ZERO_REQUIRED')
    return OpcWeightObservation(*mass, True, True, datetime.fromisoformat(evidence['observed_at']), evidence)


def validate_zero_ack(body: bytes, response: bytes, claim: dict[str, Any]) -> None:
    """A historical receipt alone never enables a physical instruction."""
    try:
        event, result = json.loads(body, object_pairs_hook=unique_object), json.loads(response, object_pairs_hook=unique_object)
        receipt, current = result['receipt'], result['current']
        for field in ('claim_id', 'device_id', 'zero_observed_at', 'zero_source_sha256', 'profile_sha256'):
            if receipt[field] != event[field]:
                raise ValueError(field)
        if receipt['request_id'] != claim['request_id'] or receipt['stock_posted'] is not False:
            raise ValueError('receipt identity')
        if receipt['zero_confirmed'] is not True or receipt['source_sha256'] != hashlib.sha256(body).hexdigest().upper():
            raise ValueError('receipt source')
        if any(current[field] != claim[field] for field in ('request_id', 'device_id', 'claim_id')):
            raise ValueError('current identity')
        if current['state'] != 'CLAIMED' or current['current_context'] != 'CURRENT':
            raise ValueError('current context')
        if current['measurement_stage'] != 'ZERO_CONFIRMED' or current['load_allowed'] is not True:
            raise ValueError('load instruction')
        if current['zero_source_sha256'] != event['zero_source_sha256'] or datetime.fromisoformat(current['zero_confirmed_at']) != datetime.fromisoformat(event['zero_observed_at']):
            raise ValueError('current zero identity')
        expiry = datetime.fromisoformat(receipt['claim_expires_at'])
        if expiry != datetime.fromisoformat(claim['claim_expires_at']) or expiry != datetime.fromisoformat(current['claim_expires_at']):
            raise ValueError('lease identity')
        server_now = datetime.fromisoformat(current['server_now'])
        if expiry.utcoffset() != timezone.utc.utcoffset(expiry) or server_now.utcoffset() != timezone.utc.utcoffset(server_now):
            raise ValueError('server UTC clock')
        if server_now >= expiry:
            raise ValueError('expired lease')
    except (KeyError, TypeError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        raise ScaleGatewayError('WAREHOUSE_ZERO_ACK_REJECTED', True) from exc
