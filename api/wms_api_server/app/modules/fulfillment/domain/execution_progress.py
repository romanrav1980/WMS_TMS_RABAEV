"""Physical order progress is derived independently from prepared shipment status."""
from decimal import Decimal, localcontext
from fractions import Fraction
from typing import Any


def _text(number: Decimal) -> str:
    value = format(number, "f")
    return value.rstrip("0").rstrip(".") if "." in value else value


def line_progress(row: dict[str, Any]) -> dict[str, Any]:
    result = {key: row[key] for key in ("customer_order_row_id", "line_no", "articul", "unit_code", "row_status")}
    with localcontext() as context:
        context.prec = 96
        picked = Decimal(row["case_fact"]) + Decimal(row["pallet_fact"])
        reserved = Decimal(row["hard_quantity"])
        result.update(picked_quantity=_text(picked), hard_quantity=_text(reserved), base_uom=row["base_uom"], requested_uom=row["unit_code"])
        if row["numerator"] is None or row["denominator"] is None or row["base_scale"] is None:
            result.update(status="REQUIRES_UOM", reason="Нет однозначного перевода единицы заказа в базовую",
                          requested_quantity=row["order_quantity"], remaining_quantity=None)
            return result
        numerator, denominator, scale = int(row["numerator"]), int(row["denominator"]), int(row["base_scale"])
        if numerator <= 0 or denominator <= 0 or not 0 <= scale <= 9:
            raise ValueError("Invalid order unit conversion")
        exact = Fraction(Decimal(row["order_quantity"])) * Fraction(numerator, denominator)
        scaled = exact * 10 ** scale
        if scaled.denominator != 1:
            result.update(status="REQUIRES_UOM", reason="Перевод заказа требует недопустимого округления",
                          requested_quantity=row["order_quantity"], remaining_quantity=None)
            return result
        requested = Decimal(scaled.numerator).scaleb(-scale)
        if requested <= 0 or picked < 0 or reserved < 0:
            raise ValueError("Invalid requested/physical quantity")
        remaining = max(Decimal(0), requested - picked)
        if picked > requested:
            status, reason = "OVER_PICKED", "Подтверждённый отбор превышает строку заказа"
        elif row["row_status"] == "CANCELLED":
            status, reason = "CANCELLED", "Строка заказа отменена; физический факт показан отдельно"
        elif remaining == 0:
            status, reason = "PICKED", "Количество подтверждено физическим отбором"
        elif row["refused_lines"]:
            status, reason = "PARTIAL_REFUSED" if picked else "REFUSED", row["refusal_reason"] or "Остаток отбора закрыт с недостачей"
        elif picked:
            status, reason = "PARTIAL", "Ожидается подтверждение оставшегося отбора"
        elif reserved:
            status, reason = "RESERVED", "Запас закреплён, физический отбор ещё не подтверждён"
        else:
            status, reason = "WAIT_STOCK", "Нет подтверждённого отбора и действующего жёсткого резерва"
        result.update(status=status, reason=reason, requested_quantity=_text(requested), requested_uom=row["base_uom"], remaining_quantity=_text(remaining))
    return result


def line_is_cancelled(line: dict[str, Any]) -> bool:
    return line.get("row_status") == "CANCELLED" or line["status"] == "CANCELLED"


def order_progress_status(lines: list[dict[str, Any]]) -> str:
    """Never hide excess, unresolved units or closed shortage behind PARTIAL."""
    if any(line["status"] == "OVER_PICKED" for line in lines):
        return "OVER_PICKED"
    if any(line["status"] == "REQUIRES_UOM" for line in lines):
        return "REQUIRES_UOM"
    active = [line for line in lines if not line_is_cancelled(line)]
    if not active:
        return "CANCELLED" if lines else "PENDING"
    if all(line["status"] == "PICKED" for line in active):
        return "PICKED"
    if any(line["status"] in {"REFUSED", "PARTIAL_REFUSED"} for line in active):
        return ("SHORT_CLOSED" if all(line["status"] in {"PICKED", "REFUSED", "PARTIAL_REFUSED"}
                                      for line in active) else "PARTIAL_REFUSED")
    if any(Decimal(line["picked_quantity"]) > 0 for line in active):
        return "PARTIAL"
    if any(line["status"] == "RESERVED" for line in active):
        return "RESERVED"
    return "PENDING"
