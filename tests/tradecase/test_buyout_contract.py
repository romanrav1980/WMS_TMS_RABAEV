from copy import deepcopy
import pytest
from pydantic import ValidationError
from api.wms_api_server.app.modules.integrations.contracts_tradecase import TradeOrder
from api.wms_api_server.app.modules.inventory.contracts_trade_buyout import TradeBuyoutRequest,TradeBuyoutResult

def basis():return dict(entity_type='ORDER',recipient_id='BLC',order_kind='BUYOUT',buyout_mode='BEFORE_PICK',planned_ship_at='2026-10-19T12:00:00+03:00',lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='BLC',mrc='200',quantity='250',uom='EA',min_osg_days=0)])

@pytest.mark.parametrize('bad',['mode','unit','ordinary_override','trip'])
def test_financial_basis_cannot_be_inferred_from_shipping_order(bad):
    v=basis()
    if bad=='mode':v.pop('buyout_mode')
    elif bad=='unit':v['lines'][0]['uom']='BOX'
    elif bad=='ordinary_override':v['order_kind']='OUTBOUND'
    else:v['parent_trip_id']='R1'
    with pytest.raises(ValidationError):TradeOrder.model_validate(v)

def test_financial_selection_is_a_set_not_a_scan_count():
    value=dict(operation_id='op',buyout_id='B1',basis_order_id='F1',basis_line_id='1',expected_basis_version=1,unit_keys=['a'*64,'a'*64])
    with pytest.raises(ValidationError):TradeBuyoutRequest.model_validate(value)

def test_external_pending_is_distinct_from_refusal():
    value=dict(operation_id='op',buyout_id='B1',expected_version=1,skm_id='L4',external_event_id='e1',external_document_id='d1',occurred_at='2026-10-19T12:00:00+03:00',items=[dict(physical_unit_key='a'*64,outcome='PENDING')])
    assert TradeBuyoutResult.model_validate(value).items[0].outcome=='PENDING'
    value['items'][0]['outcome']='REJECTED'
    with pytest.raises(ValidationError):TradeBuyoutResult.model_validate(value)
