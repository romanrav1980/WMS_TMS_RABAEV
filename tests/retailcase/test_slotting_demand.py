from decimal import Decimal
import pytest
from api.wms_api_server.app.modules.inventory.domain.slotting_demand import quantity_scenario,unpicked_demand

def test_received_order_consumes_matching_forecast_not_adds_it_twice():
    result=quantity_scenario(Decimal(40),Decimal(100),Decimal(0),Decimal(0),Decimal(100))
    assert result["scenario_required_quantity"]=="100"
    assert result["forecast_consumed_by_orders"]=="40"

def test_old_stock_and_assigned_whole_pallet_are_not_extra_demand():
    result=quantity_scenario(Decimal(150),None,Decimal(50),Decimal(0),Decimal(100))
    assert result["nominal_additional_quantity"]=="100"
    assert result["nominal_additional_pallets"]=="1"

def test_pool_hard_and_picked_overlap_keep_only_unpicked_need():
    assert unpicked_demand({"quantity":"80","hard_quantity":"20","picked_hard_overlap":"10"})==Decimal(90)
    with pytest.raises(ValueError):
        unpicked_demand({"quantity":"0","hard_quantity":"2","picked_hard_overlap":"3"})

def test_no_history_is_a_firm_lower_bound_and_no_layout_admission():
    result=quantity_scenario(Decimal(0),None,Decimal(0),Decimal(0),None)
    assert result["source_basis"]=="FIRM_WORK_MINIMUM"
    assert not result["zero_unobserved_demand_assumed"]
    assert not result["physical_layout_admission"]
    assert result["nominal_additional_quantity"]is None
