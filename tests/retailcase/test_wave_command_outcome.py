"""A lost stock-command response must not be reported as a confirmed rejection."""
import pytest
from fastapi import HTTPException
from api.wms_api_server.app.services.picking_service import PickingService
from api.wms_api_server.app.schemas import PickWaveActionRequest
from api.wms_api_server.app.modules.inventory import public


@pytest.mark.parametrize('code,status,confirmed', [
    ('RESULT_UNCERTAIN',503,False), ('REQUEST_DEADLINE',503,False),
    ('CONNECTION_UNUSABLE',503,False), ('LOCK_RETRY_EXHAUSTED',503,False),
    ('STOCK_RULE_REJECTED',409,True), ('RESOURCE_NOT_FOUND',409,True),
])
def test_wave_command_keeps_original_key_and_classifies_outcome(monkeypatch,code,status,confirmed):
    error=public.StockPostingError(code,'wave.test.original',20886,'WAVE_SOURCE_CHANGED')
    class Posting:
        def post(self,command):
            assert command.operation_id=='wave.test.original'
            assert command.command_type=='WAVE_LAUNCH'
            raise error
    monkeypatch.setattr(public,'StockPosting',Posting)
    monkeypatch.setattr(public,'require_active_stock_release',lambda *args:None)
    with pytest.raises(HTTPException)as caught:
        PickingService(object())._post_wave_command('WAVE_LAUNCH',561,
            PickWaveActionRequest(operation_id='wave.test.original',updated_by='fixture'))
    assert caught.value.status_code==status
    assert caught.value.detail['operation_id']=='wave.test.original'
    assert caught.value.detail['outcome_confirmed']is confirmed
    assert caught.value.detail['retry_same_operation_id']is (not confirmed)
    assert caught.value.detail['rule_reason']=='WAVE_SOURCE_CHANGED'


def test_lost_launch_response_never_runs_followup_steps():
    from api.wms_api_server.app.modules.inventory.public import continue_launched_wave
    calls=[]
    def post():
        raise public.StockPostingError('RESULT_UNCERTAIN','original')
    with pytest.raises(public.StockPostingError):
        continue_launched_wave(post,[('TASKS',lambda:calls.append('tasks'))],'original')
    assert calls==[]


def test_committed_launch_reports_failed_step_and_stops_later_effects():
    from api.wms_api_server.app.modules.inventory.public import continue_launched_wave, WaveLaunchContinuationError
    calls=[]
    def fail():
        calls.append('reserve')
        raise RuntimeError('source timeout')
    with pytest.raises(WaveLaunchContinuationError)as caught:
        continue_launched_wave(lambda:calls.append('receipt'),[
            ('SETTINGS',lambda:calls.append('settings')),('RESERVE_SOURCES',fail),
            ('CASE_TASKS',lambda:calls.append('case'))],'original')
    assert caught.value.operation=='original'and caught.value.step=='RESERVE_SOURCES'
    assert calls==['receipt','settings','reserve']


def test_wave_service_keeps_original_launch_and_injects_projection_factory(monkeypatch):
    from api.wms_api_server.app.modules.fulfillment import public as fulfillment
    service=PickingService(object())
    calls=[]
    monkeypatch.setattr(service,'_post_wave_command',lambda *args:calls.append(args))
    def resume(gateway,wave,operation,actor,post,factory):
        assert gateway is service.gateway and (wave,operation,actor)==(561,'original','fixture')
        assert factory is PickingService
        post()
        raise HTTPException(503,detail={'launch_outcome':'APPLIED','continuation_state':'FAILED',
            'operation_id':operation,'read_before_retry':True,
            'receipt_url':f'/api/picking/waves/{wave}/launch-receipts/{operation}'})
    monkeypatch.setattr(fulfillment,'resume_wave_launch',resume)
    with pytest.raises(HTTPException)as caught:
        service.launch_wave(561,PickWaveActionRequest(operation_id='original',updated_by='fixture'))
    assert calls[0][:2]==('WAVE_LAUNCH',561)
    assert caught.value.detail['launch_outcome']=='APPLIED'
    assert caught.value.detail['continuation_state']=='FAILED'


@pytest.mark.parametrize('oracle,reason,status',[(20882,'WAVE_LAUNCH_SCOPE_REQUIRED',403),(20845,'OPERATION_CONFLICT',409)])
def test_wave_denied_or_changed_body_does_not_confirm_new_outcome(monkeypatch,oracle,reason,status):
    class Posting:
        def post(self,command):raise public.StockPostingError('STOCK_RULE_REJECTED','original',oracle,reason)
    monkeypatch.setattr(public,'StockPosting',Posting)
    monkeypatch.setattr(public,'require_active_stock_release',lambda *args:None)
    with pytest.raises(HTTPException)as caught:
        PickingService(object())._post_wave_command('WAVE_LAUNCH',561,
            PickWaveActionRequest(operation_id='original',updated_by='fixture'))
    assert caught.value.status_code==status
    assert caught.value.detail['outcome_confirmed']is False
    assert caught.value.detail['operation_id']=='original'
