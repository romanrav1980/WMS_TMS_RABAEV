"""Versioned recipient demand snapshot; quantities are never warehouse movements."""
from datetime import timedelta
from decimal import Decimal
from typing import Annotated,Literal
from pydantic import AwareDatetime,Field,PlainSerializer,model_validator
from .contracts_trade_base import TradeModel,Key

Amount=Annotated[Decimal,Field(ge=0,max_digits=18,decimal_places=6,allow_inf_nan=False),PlainSerializer(lambda v:format(v.normalize(),'f'),return_type=str)]

class ExpectedSupply(TradeModel):
    supply_id:Key
    version:int=Field(strict=True,gt=0)
    quantity:Amount
    uom:Literal['BOX','EA']
    status:Literal['PLANNED','IN_TRANSIT','RECEIVED','CANCELLED']
    confirmed:bool
    current_trip:bool=False
    expected_at:AwareDatetime

class TradeNeed(TradeModel):
    entity_type:Literal['NEED']
    recipient_id:Key
    sku_id:Key
    recipient_version:int=Field(strict=True,gt=0)
    sku_version:int=Field(strict=True,gt=0)
    snapshot_at:AwareDatetime
    period_from:AwareDatetime
    period_until:AwareDatetime
    uom:Literal['BOX','EA']
    forecast_quantity:Amount
    target_quantity:Amount
    available_quantity:Amount
    received_in_available:Literal[True]
    supplies:list[ExpectedSupply]=Field(default_factory=list,max_length=200)

    @model_validator(mode='after')
    def horizon(self)->'TradeNeed':
        if not timedelta(0)<self.period_until-self.period_from<=timedelta(days=31):
            raise ValueError('Demand horizon must be positive and at most31days')
        keys=[(x.supply_id,x.version)for x in self.supplies]
        if len(keys)!=len(set(keys)):raise ValueError('Duplicate supply version')
        return self
