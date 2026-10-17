"""Strict native claim ACK before any instrument observation; no fabricated claim timestamp."""
from datetime import datetime, timezone
import json
from typing import Any
from ..contracts_scales import ScaleGatewayError
from ..contracts_warehouse_gateway import WarehouseGatewayProfile
from .warehouse_scale_ack import unique_object


def validate_claim(request: dict[str, Any], body: bytes, response: bytes,
                   profile: WarehouseGatewayProfile) -> dict[str, Any]:
    try:
        claim = json.loads(body, object_pairs_hook=unique_object)
        result = json.loads(response, object_pairs_hook=unique_object)
        context = result['capture_context']
        for key in ('request_id', 'device_id', 'case_task_id', 'purpose'):
            if type(result[key]) is not type(request[key]) or result[key] != request[key]:
                raise ValueError()
        if result['claim_id'] != claim['claim_id'] or claim['device_id'] != profile.device_id:
            raise ValueError()
        if result['stock_posted'] is not False or result['current_context'] != 'CURRENT':
            raise ValueError()
        for key in ('device_id', 'post_cell', 'device_policy_version', 'calibration_ref', 'basis'):
            if type(context[key]) is not type(getattr(profile, key)) or context[key] != getattr(profile, key):
                raise ValueError()
        if context['case_task_id'] != request['case_task_id'] or context['capture_id'] != claim['claim_id']:
            raise ValueError()
        if context['unit'] != 'KG' or context['preset_tare_kg'] != '0':
            raise ValueError()
        purpose = context.get('purpose', 'PICK')
        if purpose != request['purpose'] or purpose not in {'PICK', 'EMPTY_TARE', 'FINAL_GROSS'}:
            raise ValueError()
        fields = {'device_id','capture_id','post_cell','case_task_id','expected_content_version',
                  'scan_container','device_policy_version','calibration_ref','unit','basis','preset_tare_kg'}
        fields.update({'case_line_id','scan_source_cell','scan_product'} if purpose == 'PICK' else {'purpose'})
        if purpose == 'FINAL_GROSS':
            fields.add('tare_capture_key')
        if set(context) != fields or type(context['case_task_id']) is not int or context['case_task_id'] < 1:
            raise ValueError()
        if type(context['expected_content_version']) is not int or context['expected_content_version'] < 0:
            raise ValueError()
        if not isinstance(context['scan_container'], str) or not 1 <= len(context['scan_container']) <= 150:
            raise ValueError()
        for field in ('expires_at', 'claim_expires_at'):
            stamp = datetime.fromisoformat(result[field])
            if stamp.utcoffset() != timezone.utc.utcoffset(stamp):
                raise ValueError()
        if datetime.fromisoformat(result['claim_expires_at']) > datetime.fromisoformat(result['expires_at']):
            raise ValueError()
        if result['claim_active'] is not True or result['state'] != 'CLAIMED':
            raise ScaleGatewayError('WAREHOUSE_CLAIM_EXPIRED_OR_CAPTURED')
        if request.get('zero_progress_required') is True:
            if result.get('zero_progress_required') is not True:
                raise ValueError('zero progress requirement changed')
            created = datetime.fromisoformat(result['claim_created_at'])
            if created.utcoffset() != timezone.utc.utcoffset(created):
                raise ValueError('claim creation time must be UTC')
            if not 0 < (datetime.fromisoformat(result['claim_expires_at'])-created).total_seconds() <= 30:
                raise ValueError('claim creation window')
        return result
    except (ValueError, TypeError, KeyError, AttributeError):
        raise ScaleGatewayError('WAREHOUSE_CLAIM_ACK_INVALID', True) from None
