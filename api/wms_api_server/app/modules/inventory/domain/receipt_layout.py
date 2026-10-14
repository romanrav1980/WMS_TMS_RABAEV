"""Quantity-only pallet layout proposal; physical receipt remains authoritative in Oracle."""
from decimal import Decimal
from fractions import Fraction
from typing import Any
from .unit_quantity import PIECE_UNITS


def propose_receipt_layout(remaining: str, base_uom: str, norm: str | None,
                           pallet_count: int | None, quantities: list[str] | None,
                           quantity_step: str | None = None) -> dict[str, Any]:
    total = Decimal(remaining)
    step = Decimal(quantity_step or ("1" if base_uom.upper() in PIECE_UNITS else "0.000001"))
    if not total.is_finite() or total <= 0 or not step.is_finite() or step <= 0:
        raise ValueError("RECEIPT_LAYOUT_POSITIVE_QUANTITY_REQUIRED")
    if step.normalize().as_tuple().exponent < -6 or step > total:
        raise ValueError("RECEIPT_LAYOUT_QUANTITY_STEP_INVALID")
    if base_uom.upper() in PIECE_UNITS and step != 1:
        raise ValueError("RECEIPT_LAYOUT_PIECE_STEP_MUST_BE_ONE")
    capacity = Decimal(norm or "0")
    ticks = Fraction(total) / Fraction(step)
    if ticks.denominator != 1:
        raise ValueError("RECEIPT_LAYOUT_REMAINING_NOT_MULTIPLE_OF_STEP")
    if pallet_count is not None and quantities is not None:
        raise ValueError("RECEIPT_LAYOUT_COUNT_OR_QUANTITIES")
    if quantities is not None:
        if not 1 <= len(quantities) <= 200:
            raise ValueError("RECEIPT_LAYOUT_PALLET_BOUND_200")
        amounts = [Decimal(q) for q in quantities]
        for value in amounts:
            if not value.is_finite() or value <= 0 or value.normalize().as_tuple().exponent < -6:
                raise ValueError("RECEIPT_LAYOUT_PALLET_QUANTITY_INVALID")
            if (Fraction(value) / Fraction(step)).denominator != 1:
                raise ValueError("RECEIPT_LAYOUT_PALLET_NOT_MULTIPLE_OF_STEP")
    elif pallet_count is not None:
        if isinstance(pallet_count, bool) or not 1 <= pallet_count <= 200:
            raise ValueError("RECEIPT_LAYOUT_PALLET_BOUND_200")
        per, extra = divmod(ticks.numerator, pallet_count)
        if per == 0:
            raise ValueError("RECEIPT_LAYOUT_EMPTY_PALLETS_NOT_ALLOWED")
        amounts = [step * (per + int(i < extra)) for i in range(pallet_count)]
    else:
        if not capacity.is_finite() or capacity <= 0:
            raise ValueError("RECEIPT_LAYOUT_SET_COUNT_OR_QUANTITIES_WITHOUT_NORM")
        size = Fraction(capacity) / Fraction(step)
        if size.denominator != 1:
            raise ValueError("RECEIPT_LAYOUT_NORM_NOT_MULTIPLE_OF_STEP")
        count = (ticks.numerator + size.numerator - 1) // size.numerator
        if count > 200:
            raise ValueError("RECEIPT_LAYOUT_PALLET_BOUND_200")
        amounts = [capacity] * (count - 1) + [total - capacity * (count - 1)]
    planned = sum(amounts, Decimal(0))
    if planned > total:
        raise ValueError("RECEIPT_LAYOUT_EXCEEDS_CURRENT_ORDER_REMAINING")
    return {"pallet_count": len(amounts), "quantities": [format(q, "f") for q in amounts],
            "planned_quantity": format(planned, "f"), "unplanned_quantity": format(total - planned, "f"),
            "quantity_step": format(step, "f"), "base_uom": base_uom,
            "above_norm_pallets": [i + 1 for i, q in enumerate(amounts) if capacity > 0 and q > capacity],
            "physical_receipt_confirmed": False, "stock_changed": False,
            "placement_capacity_verified": False, "reservation_created": False}
