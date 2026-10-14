from decimal import Decimal,InvalidOperation
from .amount import rate_value

def signed_amount(value: str,correction: bool) -> Decimal:
    try:amount=Decimal(value)
    except InvalidOperation as exc:raise ValueError("Некорректная сумма") from exc
    if not amount.is_finite():raise ValueError("Сумма должна быть конечной")
    rate_value(str(abs(amount)))
    if amount==0 or not correction and amount<0 or amount!=amount.quantize(Decimal("0.01")):
        raise ValueError("Нужна ненулевая сумма с точностью до копейки; отрицательная сумма допустима только для коррекции")
    return amount
