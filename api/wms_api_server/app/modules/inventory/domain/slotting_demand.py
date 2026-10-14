"""Forecast consumption and whole-pallet scenario quantities; no placement admission."""
from decimal import Decimal,localcontext,ROUND_CEILING
from typing import Any

def unpicked_demand(order: dict[str,Any]) -> Decimal:
    unallocated=Decimal(order["quantity"])
    hard=Decimal(order["hard_quantity"])
    overlap=Decimal(order["picked_hard_overlap"])
    if min(unallocated,hard,overlap)<0 or overlap>hard:
        raise ValueError("SLOTTING_DEMAND_OVERLAP_INVALID")
    with localcontext()as ctx:
        ctx.prec=80
        return unallocated+hard-overlap

def quantity_scenario(
    firm: Decimal,forecast: Decimal|None,old_credit: Decimal,
    inbound: Decimal,pallet_multiple: Decimal|None,
) -> dict[str,Any]:
    if min(firm,old_credit,inbound)<0 or forecast is not None and forecast<0:
        raise ValueError("SLOTTING_QUANTITY_NEGATIVE")
    with localcontext()as ctx:
        ctx.prec=80
        consumed=min(firm,forecast)if forecast is not None else Decimal(0)
        total=firm if forecast is None else firm+forecast-consumed
        deficit=max(Decimal(0),total-old_credit-inbound)
        valid_multiple=pallet_multiple is not None and pallet_multiple>0
        pallets=(deficit/pallet_multiple).to_integral_value(rounding=ROUND_CEILING)if valid_multiple else None
        additional=pallets*pallet_multiple if pallets is not None else None
        return {"firm_unpicked_quantity":format(firm,"f"),
            "declared_period_forecast":None if forecast is None else format(forecast,"f"),
            "forecast_consumed_by_orders":format(consumed,"f"),
            "scenario_required_quantity":format(total,"f"),"old_stock_credit":format(old_credit,"f"),
            "scheduled_inbound_credit":format(inbound,"f"),"unrounded_additional_quantity":format(deficit,"f"),
            "nominal_additional_pallets":None if pallets is None else format(pallets,"f"),
            "nominal_additional_quantity":None if additional is None else format(additional,"f"),
            "source_basis":"FIRM_WORK_MINIMUM"if forecast is None else"DECLARED_PERIOD_TOTAL_SCENARIO",
            "zero_unobserved_demand_assumed":False,"physical_layout_admission":False}
