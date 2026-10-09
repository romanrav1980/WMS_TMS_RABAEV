from decimal import Decimal, InvalidOperation

PIECE_UNITS = {"PCE", "PCS", "PC", "EA", "ST", "STK", "ШТ", "ШТУКА"}


def unit_quantity(value: object, base_uom: str, fallback: Decimal | None) -> Decimal:
    piece = base_uom.upper() in PIECE_UNITS
    default = Decimal(1) if piece else fallback
    if value is None and default is None:
        raise ValueError("Set the physical unit quantity in warehouse base UoM")
    try:
        quantity = Decimal(str(default if value is None else value))
    except InvalidOperation as exc:
        raise ValueError("Invalid physical unit quantity") from exc
    if not quantity.is_finite() or quantity<=0 or quantity>Decimal('999999999999') or quantity.normalize().as_tuple().exponent < -6:
        raise ValueError("Physical unit quantity must be positive with at most 6 decimals")
    if piece and quantity!=1:
        raise ValueError("Each unique piece code represents exactly one physical piece")
    return quantity
