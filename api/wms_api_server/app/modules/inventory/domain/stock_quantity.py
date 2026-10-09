"""Exact input arithmetic; Oracle remains authoritative for physical posting."""
from decimal import Decimal
from fractions import Fraction

MAX_QUANTITY = Decimal(10) ** 18


def quantity_text(value: str | Decimal, scale: int = 9) -> str:
    if not isinstance(value, (str, Decimal)):
        raise TypeError("Stock quantity requires a decimal string or Decimal, never float")
    number = Decimal(value)
    if not number.is_finite() or number <= 0 or number >= MAX_QUANTITY:
        raise ValueError("Quantity must be positive, finite and below 10^18")
    if not isinstance(scale, int) or isinstance(scale, bool) or not 0 <= scale <= 9:
        raise ValueError("Invalid permitted quantity scale")
    digits = list(number.as_tuple().digits)
    exponent = number.as_tuple().exponent
    while digits and digits[-1] == 0:
        digits.pop()
        exponent += 1
    if exponent < -scale:
        raise ValueError("Quantity is not exactly representable on the permitted scale")
    text = format(number, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def convert_exact(value: str | Decimal, numerator: int, denominator: int, scale: int) -> Decimal:
    if not isinstance(scale, int) or isinstance(scale, bool) or not 0 <= scale <= 9:
        raise ValueError("Invalid base quantity scale")
    if (isinstance(numerator, bool) or isinstance(denominator, bool)
            or not isinstance(numerator, int) or not isinstance(denominator, int)
            or not 1 <= numerator <= 10**9 or not 1 <= denominator <= 10**9):
        raise ValueError("Conversion requires bounded positive integer factors")
    converted = Fraction(Decimal(quantity_text(value))) * Fraction(numerator, denominator)
    scaled = converted * 10**scale
    if scaled.denominator != 1:
        raise ValueError("Conversion would require rounding")
    digits = str(scaled.numerator)
    if scale:
        digits = digits.zfill(scale + 1)
        digits = digits[:-scale] + "." + digits[-scale:]
    result = Decimal(digits)
    quantity_text(result, scale)
    return result
