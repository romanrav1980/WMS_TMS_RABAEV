"""Keep physical quantities by SKU/base unit; mixed units have no scalar total."""
from decimal import Decimal, localcontext
from .stock_quantity import quantity_text


def physical_composition(rows: list[tuple]) -> tuple[list[dict], str | None, str | None]:
    if not 1 <= len(rows) <= 200:
        raise ValueError("Physical composition exceeds the supported bound or is empty")
    quantities: dict[tuple[str, str], Decimal] = {}
    with localcontext() as context:
        context.prec = 96
        for article, base, quantity in rows:
            if not article or not base:
                raise ValueError("Physical SKU/base unit required")
            key = (article, base)
            quantities[key] = quantities.get(key, Decimal(0)) + Decimal(quantity_text(quantity))
        composition = [{"article": article, "base_uom": base, "quantity": quantity_text(qty)}
                       for (article, base), qty in sorted(quantities.items())]
        units = {key[1] for key in quantities}
        if len(units) == 1:
            return composition, quantity_text(sum(quantities.values(), Decimal(0))), next(iter(units))
    return composition, None, None
