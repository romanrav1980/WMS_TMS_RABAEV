"""Explain a recipient snapshot without allocating sender stock or creating an order."""
from datetime import datetime,timezone
from decimal import Decimal
from typing import Any


def net_need(body:dict[str,Any],units_per_box:int,now:datetime,max_age_minutes:int)->dict:
    def base(value:Decimal|str,uom:str)->Decimal:return Decimal(value)*(units_per_box if uom=='BOX'else 1)
    selected={}
    for supply in body['supplies']:
        old=selected.get(supply['supply_id'])
        if old is None or supply['version']>old['version']:selected[supply['supply_id']]=supply
    incoming=Decimal(0);primary=Decimal(0);evidence=[]
    for key,supply in sorted(selected.items()):
        quantity=base(supply['quantity'],supply['uom']);category='EXCLUDED'
        if supply['status']=='RECEIVED':category='IN_AVAILABLE'
        elif supply['status']=='CANCELLED':category='CANCELLED'
        elif supply['expected_at']>body['period_until']:category='AFTER_HORIZON'
        elif not supply['confirmed']:category='UNCONFIRMED'
        elif supply['current_trip']:primary+=quantity;category='CURRENT_TRIP'
        elif supply['status']=='IN_TRANSIT':incoming+=quantity;category='IN_TRANSIT'
        else:category='PLANNED_OTHER_TRIP'
        evidence.append(dict(supply_id=key,version=supply['version'],status=supply['status'],base_quantity=str(quantity),accounted_as=category))
    forecast=base(body['forecast_quantity'],body['uom']);target=base(body['target_quantity'],body['uom']);available=base(body['available_quantity'],body['uom'])
    age=(now-body['snapshot_at']).total_seconds()/60
    if age<0:raise ValueError('NEED_SNAPSHOT_IN_FUTURE')
    value=max(Decimal(0),forecast+target-available-incoming-primary)
    return dict(base_uom='EA',forecast_quantity=str(forecast),target_quantity=str(target),available_quantity=str(available),in_transit_quantity=str(incoming),current_trip_quantity=str(primary),
                additional_quantity=str(value),additional_boxes=str(value/units_per_box),supplies=evidence,snapshot_at=body['snapshot_at'].isoformat(),
                age_minutes=round(age,3),max_age_minutes=max_age_minutes,expired=age>max_age_minutes,physical_execution=False,approval_available=False)
