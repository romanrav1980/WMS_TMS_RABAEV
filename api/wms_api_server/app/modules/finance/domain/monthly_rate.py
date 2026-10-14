"""Exact declared monthly cost components for the existing BOX rate."""
from datetime import date
from decimal import Decimal, localcontext, ROUND_HALF_UP
from .amount import rate_value


def monthly_components(month: str, picking: str, common: str, boxes: str) -> dict[str, str]:
    try:
        first = date.fromisoformat(month + "-01")
        base, total = rate_value(picking), rate_value(common)
        count = Decimal(boxes)
    except (ValueError, ArithmeticError) as exc:
        raise ValueError("Укажите месяц YYYY-MM, ставки и положительное число коробок") from exc
    if total.as_tuple().exponent < -2:
        raise ValueError("Общие месячные затраты задаются с точностью до копеек")
    if not count.is_finite() or count <= 0 or count != count.to_integral_value() or count > Decimal("999999999999"):
        raise ValueError("Расчётная база должна быть положительным целым числом коробок")
    with localcontext() as ctx:
        ctx.prec = 50
        share = (total / count).quantize(Decimal("0.000000001"), rounding=ROUND_HALF_UP)
        combined = rate_value(format(base + share, "f"))
    def canonical(value: Decimal) -> str:
        return format(value.normalize(), "f")
    return {"month": first.strftime("%Y-%m"), "picking_rate": canonical(base),
            "common_work_amount": canonical(total), "basis_boxes": canonical(count),
            "common_work_rate": canonical(share), "combined_rate": canonical(combined),
            "basis_provenance": "DECLARED_MONTHLY_BOX_BASE"}
