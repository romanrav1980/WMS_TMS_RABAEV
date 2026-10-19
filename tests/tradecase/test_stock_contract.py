from copy import deepcopy
from hashlib import sha256
import pytest
from pydantic import ValidationError
from api.wms_api_server.app.modules.inventory.contracts_trade_stock import TradeMarkConfirmation,TradeCellPolicy,TradeOwnerGrant
from api.wms_api_server.app.modules.inventory.contracts_trade_planning import TradeOrderBind
from api.wms_api_server.app.modules.integrations.contracts_tradecase import TradeEnvelope
from api.wms_api_server.app.modules.integrations.infrastructure.tradecase_documents import OracleTradecaseDocuments,canonical

def confirmation():
    return dict(operation_id='op',skm_id='L4',external_event_id='biz1',expected_site_version=1,occurred_at='2026-10-19T11:00:00+03:00',items=[dict(physical_unit_key='a'*64,expected_attribute_version=1,verdict='VALID')])

@pytest.mark.parametrize('change',['duplicate','naive','reason','version'])
def test_rejects_unsafe_external_confirmation(change):
    value=confirmation()
    if change=='duplicate':value['items']*=2
    elif change=='naive':value['occurred_at']='2026-10-19T11:00:00'
    elif change=='reason':value['items'][0]['verdict']='REJECTED'
    else:value['expected_site_version']=True
    with pytest.raises(ValidationError):TradeMarkConfirmation.model_validate(value)

def test_rejects_ambiguous_native_line_binding():
    with pytest.raises(ValidationError):TradeOrderBind.model_validate(dict(operation_id='op',expected_order_version=1,customer_order_id=1,lines=[dict(line_id='a',customer_order_row_id=2),dict(line_id='b',customer_order_row_id=2)]))

def test_pick_range_requires_owner():
    with pytest.raises(ValidationError):TradeCellPolicy.model_validate(dict(operation_id='op',expected_version=0,zone_kind='PICK',reason='Configure range'))

def test_operating_grant_requires_visibility():
    with pytest.raises(ValidationError):TradeOwnerGrant.model_validate(dict(operation_id='op',expected_version=0,username='u',owner_id='SNS',can_view=False,can_operate=True,reason='Grant test operation'))

class Capture(OracleTradecaseDocuments):
    def _command(self,procedure,warehouse_id,actor,value):return value

def test_optional_mapping_preserves_unchanged_older_business_hash():
    original=dict(schema_version=1,event_id='e1',source_id='SAP',warehouse_id=1,document_id='A',version=1,occurred_at='2026-10-19T11:00:00+03:00',payload=dict(entity_type='SKU',title='A',base_uom='EA',units_per_box=10,permitted_mrc=['200'],active=True))
    result=Capture(None).receive(TradeEnvelope.model_validate(original),'admin')
    expected={key:original[key]for key in('schema_version','source_id','warehouse_id','document_id','version','payload')}
    assert result['business_hash']==sha256(canonical(expected).encode()).hexdigest()
    assert 'wms_article_id'not in result['payload']
