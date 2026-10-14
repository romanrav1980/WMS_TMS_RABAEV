"""Exact legacy pallet shares without decimal-context rounding."""
from decimal import Decimal
from fractions import Fraction

def exact_decimal(value: Fraction,scale: int=9) -> Decimal:
    ticks=value*10**scale
    if ticks.denominator!=1:
        raise ValueError("Pallet logistics share is not representable exactly; correct packaging parameters")
    negative=ticks.numerator<0
    digits=str(abs(ticks.numerator)).zfill(scale+1)
    text=("-"if negative else "")+digits[:-scale]+"."+digits[-scale:]
    return Decimal(text)

def pallet_share(quantity: Decimal,total: Decimal,total_packs: Decimal,total_weight: Decimal) -> tuple[int,Decimal]:
    values=(quantity,total,total_packs,total_weight)
    if any(not v.is_finite()or v<=0 for v in values)or quantity>total:
        raise ValueError("Positive bounded source logistics quantities are required")
    fraction=Fraction(quantity)/Fraction(total)
    packs=Fraction(total_packs)*fraction
    if packs.denominator!=1:
        raise ValueError("Current legacy row writer requires whole packaging units in each pallet layout")
    weight=exact_decimal(Fraction(total_weight)*fraction)
    return packs.numerator,weight
