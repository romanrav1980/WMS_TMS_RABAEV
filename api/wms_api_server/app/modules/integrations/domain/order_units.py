"""C-0175: one normalization of an order line from its input unit to the SKU's single processing unit (owner rule 27.10.2026).

Coefficients come only from the article's published RRL_STOCK_UOM_CONVERSION rows (rational numerator/denominator, policy
version); the arithmetic is exact (Fraction). The processing step is the SKU's explicit setting (in processing units), not the
registry precision. The result is always rounded DOWN to that step. The SKU flag `round_to_processing_unit` decides only whether a
line that came in another unit is an integration error, never the direction: with the flag off such a line is loaded AND carries
the error, even when the conversion is exact. A missing coefficient or setting never produces a quantity: the line is kept as
non-executable. Nothing here reads or writes the database."""
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from math import floor

# Explicit order-unit code -> registry input unit. The source code is always kept as received.
REGISTRY_UNIT = {"EA": "EA", "BOX": "BOX", "BLOCK": "BLK", "BLK": "BLK", "G": "G", "KG": "KG"}


@dataclass(frozen=True)
class Conversion:
    """One published registry row: 1 input unit = numerator/denominator base units."""
    numerator: int
    denominator: int
    base_uom: str
    base_scale: int
    policy_version: int


def _text(value: Fraction) -> str:
    denominator, scale = value.denominator, 0
    for prime in (2, 5):
        exponent = 0
        while denominator % prime == 0:
            denominator //= prime
            exponent += 1
        scale = max(scale, exponent)
    if denominator != 1:
        raise ValueError("A non-terminating fraction has no exact decimal representation")
    with localcontext() as context:
        context.prec = len(str(abs(value.numerator))) + scale + 1
        text = format(Decimal(value.numerator) / Decimal(value.denominator), "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def _kept(source: dict, status: str, error: str, policy: dict) -> dict:
    return dict(source, quantity=None, uom=None, status=status, error_code=error, integration_error=True, executable=False, conversion_policy=policy)


def normalize_line(quantity: Decimal, uom: str, processing_uom: str | None, processing_step: Decimal | None, round_allowed: bool,
                   conversions: dict[str, Conversion]) -> dict:
    source = dict(source_quantity=_text(Fraction(Decimal(quantity))), source_uom=uom)
    if processing_uom is None:
        if uom in ("EA", "BOX"):  # current EA/BOX contract without the new setting: unchanged
            return dict(source, quantity=source["source_quantity"], uom=uom, status="UNCHANGED", error_code=None, integration_error=False,
                        executable=True, conversion_policy={})
        return _kept(source, "PROCESSING_UNIT_REQUIRED", "ORDER_UNIT_PROCESSING_UNIT_REQUIRED", {})
    if processing_step is None or Decimal(processing_step) <= 0:
        return _kept(source, "PROCESSING_STEP_REQUIRED", "ORDER_UNIT_PROCESSING_STEP_REQUIRED", {})
    src_unit, proc_unit = REGISTRY_UNIT.get(uom), REGISTRY_UNIT.get(processing_uom)
    if src_unit is None or proc_unit is None:
        return _kept(source, "COEFFICIENT_MISSING", "ORDER_UNIT_CODE_UNSUPPORTED:" + uom, {})
    wanted = {src_unit, proc_unit}
    missing = sorted(u for u in wanted if u not in conversions)
    policy = {u: conversions[u].policy_version for u in sorted(wanted) if u in conversions}
    if missing:
        return _kept(source, "COEFFICIENT_MISSING", "ORDER_UNIT_COEFFICIENT_MISSING:" + ",".join(missing), policy)
    src, proc = conversions[src_unit], conversions[proc_unit]
    if src.base_uom != proc.base_uom or min(src.numerator, src.denominator, proc.numerator, proc.denominator) <= 0:
        return _kept(source, "COEFFICIENT_MISSING", "ORDER_UNIT_BASE_MISMATCH", policy)
    base = Fraction(Decimal(quantity)) * Fraction(src.numerator, src.denominator)
    per_unit = Fraction(proc.numerator, proc.denominator)
    step = Fraction(Decimal(processing_step))
    processed = floor(base / per_unit / step) * step
    processed_base = processed * per_unit
    difference = base - processed_base
    other_unit = src_unit != proc_unit
    if processed == 0:
        status = "ZERO"
    elif difference:
        status = "ROUNDED_DOWN"
    else:
        status = "CONVERTED" if other_unit else "EXACT"
    error = None
    if other_unit and not round_allowed:
        error = "ORDER_UNIT_ROUNDING_NOT_ALLOWED"  # loaded, but the sender must see the integration error
    elif processed == 0:
        error = "ORDER_LINE_ZERO_AFTER_ROUNDING"
    try:
        quantities = dict(quantity=_text(processed), base_quantity=_text(base),
                          processed_base_quantity=_text(processed_base), base_difference=_text(difference))
    except ValueError:
        return _kept(source, "COEFFICIENT_PRECISION_UNSUPPORTED", "ORDER_UNIT_EXACT_DECIMAL_REQUIRED", policy)
    return dict(source, **quantities, uom=processing_uom, base_uom=src.base_uom, status=status, error_code=error,
                integration_error=other_unit and not round_allowed, executable=processed > 0, conversion_policy=policy)
