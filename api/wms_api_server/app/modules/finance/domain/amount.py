from decimal import Decimal,InvalidOperation,ROUND_HALF_UP

def rate_value(value: str) -> Decimal:
    try:amount=Decimal(value)
    except InvalidOperation as exc:raise ValueError("Некорректная ставка") from exc
    if not amount.is_finite() or amount<0 or amount>=Decimal("1e18") or amount.as_tuple().exponent<-9:
        raise ValueError("Ставка должна быть неотрицательной и иметь не более 9 знаков после запятой")
    return amount

def cost_amount(quantity: int,value: Decimal) -> Decimal:
    return (quantity*value).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)
