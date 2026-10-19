from datetime import datetime,timedelta,timezone
from decimal import Decimal
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'api/wms_api_server'))
from app.modules.integrations.contracts_trade_need import TradeNeed
from app.modules.integrations.domain.trade_need import net_need as calculate

def net_need(body,units,now,age):return calculate(body.model_dump(),units,now,age)
from app.modules.integrations.contracts_tradecase import TradecaseError,TradeEnvelope
NOW=datetime(2026,10,19,10,tzinfo=timezone.utc)

def body(**changes):
    value=dict(entity_type='NEED',recipient_id='C2',sku_id='A',recipient_version=1,sku_version=1,snapshot_at=NOW,period_from=NOW,period_until=NOW+timedelta(days=1),uom='BOX',forecast_quantity='100',target_quantity='20',available_quantity='30',received_in_available=True,supplies=[])
    value.update(changes);return TradeNeed.model_validate(value)

def supply(id,**changes):
    value=dict(supply_id=id,version=1,quantity='20',uom='BOX',status='IN_TRANSIT',confirmed=True,current_trip=False,expected_at=NOW+timedelta(hours=1));value.update(changes);return value

def test_control_and_transition_do_not_double_count():
    planned=supply('S',status='PLANNED',current_trip=True,quantity='50')
    transit=supply('S',version=2,status='IN_TRANSIT',current_trip=True,quantity='50')
    b=body(supplies=[planned,transit]);r=net_need(b,10,NOW,60)
    assert r['additional_quantity']=='400' and r['current_trip_quantity']=='500' and r['in_transit_quantity']=='0'
    assert len(r['supplies'])==1 and r['supplies'][0]['version']==2

def test_received_only_in_stock_and_exclusions():
    r=net_need(body(available_quantity='80',supplies=[supply('R',status='RECEIVED',quantity='50'),supply('L',expected_at=NOW+timedelta(days=2)),supply('U',confirmed=False),supply('C',status='CANCELLED'),supply('P',status='PLANNED')]),10,NOW,60)
    assert r['additional_quantity']=='400' and r['in_transit_quantity']=='0'
    assert {x['accounted_as']for x in r['supplies']}=={'IN_AVAILABLE','AFTER_HORIZON','UNCONFIRMED','CANCELLED','PLANNED_OTHER_TRIP'}

def test_mixed_units_and_zero_floor():
    r=net_need(body(forecast_quantity='10',target_quantity='0',available_quantity='1',supplies=[supply('EA',quantity='90',uom='EA')]),10,NOW,60)
    assert Decimal(r['additional_quantity'])==0

def test_freshness_explicit_threshold_and_future_rejected():
    assert net_need(body(snapshot_at=NOW-timedelta(minutes=61)),10,NOW,60)['expired'] is True
    assert net_need(body(snapshot_at=NOW-timedelta(minutes=60)),10,NOW,60)['expired'] is False
    with pytest.raises(ValueError,match='NEED_SNAPSHOT_IN_FUTURE'):net_need(body(snapshot_at=NOW+timedelta(seconds=1)),10,NOW,60)

def test_duplicate_version_and_invalid_horizon_rejected():
    with pytest.raises(ValueError):body(supplies=[supply('X'),supply('X')])
    with pytest.raises(ValueError):body(period_until=NOW+timedelta(days=32))
    with pytest.raises(ValueError):body(uom='KG')
    with pytest.raises(ValueError):body(received_in_available=False)

def test_zero_forecast_is_preserved_in_exchange():
    b=body(forecast_quantity='0');e=TradeEnvelope(schema_version=1,event_id='E',source_id='S',warehouse_id=1,document_id='N',version=2,occurred_at=NOW,payload=b)
    assert Decimal(e.model_dump(mode='json')['payload']['forecast_quantity'])==0


def test_offset_changes_do_not_change_snapshot_period_identity():
    local=timezone(timedelta(hours=3))
    a=body(supplies=[supply('S')])
    b=body(snapshot_at=NOW.astimezone(local),period_from=NOW.astimezone(local),period_until=(NOW+timedelta(days=1)).astimezone(local),supplies=[supply('S',expected_at=(NOW+timedelta(hours=1)).astimezone(local))])
    assert a.model_dump(mode='json')==b.model_dump(mode='json')
    assert isinstance(b.model_dump()['snapshot_at'],datetime)
