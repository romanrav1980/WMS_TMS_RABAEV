"""Bounded deterministic whole-box packing; no database or physical stock effects."""
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from .preparation_quantities import exact_decimal

STRATEGY = "LEGACY_GROUP_WHOLE_BOX_V2"

def positive(value: str) -> Fraction:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("AUTO_LAYOUT_POSITIVE_LOGISTICS_REQUIRED") from exc
    if not number.is_finite() or number <= 0:
        raise ValueError("AUTO_LAYOUT_POSITIVE_LOGISTICS_REQUIRED")
    return Fraction(number)


def temperature(line: dict) -> tuple[Decimal | None, Decimal | None]:
    try:
        lo=Decimal(str(line["temp_min_c"])) if line.get("temp_min_c") is not None else None
        hi=Decimal(str(line["temp_max_c"])) if line.get("temp_max_c") is not None else None
    except InvalidOperation as exc:
        raise ValueError("AUTO_LAYOUT_INVALID_TEMPERATURE_RANGE") from exc
    if any(x is not None and not x.is_finite() for x in (lo,hi)) or (lo is not None and hi is not None and lo>hi):
        raise ValueError("AUTO_LAYOUT_INVALID_TEMPERATURE_RANGE")
    return lo,hi

def merged_temperature(current: dict, lo: Decimal | None, hi: Decimal | None) -> tuple[Decimal | None, Decimal | None] | None:
    known=lo is not None or hi is not None
    if bool(current["temp_min_c"] is not None or current["temp_max_c"] is not None)!=known:
        return None
    lower=[x for x in (lo,current["temp_min_c"]) if x is not None]
    upper=[x for x in (hi,current["temp_max_c"]) if x is not None]
    result=(max(lower) if lower else None,min(upper) if upper else None)
    if result[0] is not None and result[1] is not None and result[0]>result[1]:
        return None
    return result

def automatic_layout(lines: list[dict], sequence: dict[str, tuple], limits: dict) -> dict:
    mass_limit = positive(limits["max_goods_weight_kg"])
    volume_limit = positive(limits["max_goods_volume_m3"])
    bound = limits["max_pallets"]
    if isinstance(bound, bool) or not isinstance(bound, int) or not 1 <= bound <= 100:
        raise ValueError("AUTO_LAYOUT_PALLET_BOUND_100")
    if not lines or len(lines) > 1000:
        raise ValueError("AUTO_LAYOUT_SOURCE_BOUND_1000")
    pallets = []
    statistics = []
    current = None
    ordered = sorted(lines, key=lambda l: (*sequence.get(l["articul"], (101, None))[:1],
                         sequence.get(l["articul"], (101, None))[1] is None,
                         sequence.get(l["articul"], (101, None))[1] or 0, l["articul"]))
    for line in ordered:
        article = line["articul"]
        pack = positive(line["pack_quantity"])
        boxes = positive(line["quantity"]) / pack
        if boxes.denominator != 1:
            raise ValueError("WHOLE_PACKAGING_LAYOUT_REQUIRED")
        norm_boxes = positive(line["pallet_norm"]) // pack
        if norm_boxes < 1:
            raise ValueError("AUTO_LAYOUT_NORM_SMALLER_THAN_BOX: " + article)
        box_mass = positive(line["pack_mass"])
        dx, dy, dz = (positive(x) for x in line["dimensions"])
        box_volume = dx * dy * dz / 1_000_000_000
        group, _ = sequence.get(article, (101, None))
        lo,hi=temperature(line)
        remaining = boxes.numerator
        while remaining:
            if current is not None and (current["group"]!=group or merged_temperature(current,lo,hi) is None):
                current=None
            if current is None:
                if len(pallets) >= bound:
                    raise ValueError("AUTO_LAYOUT_PALLET_LIMIT_EXCEEDED")
                current = {"group": group, "mass": Fraction(0), "volume": Fraction(0),
                           "norm": Fraction(0), "lines": [],"temp_min_c":lo,"temp_max_c":hi}
                pallets.append({"lines": current["lines"]})
                statistics.append(current)
            capacity = min((mass_limit-current["mass"])//box_mass,
                           (volume_limit-current["volume"])//box_volume,
                           (1-current["norm"])*norm_boxes//1)
            count = min(remaining, capacity)
            if count < 1:
                if not current["lines"]:
                    raise ValueError("AUTO_LAYOUT_ONE_BOX_EXCEEDS_LIMITS: " + article)
                current = None
                continue
            current["lines"].append({"articul": article,
                "quantity": format(exact_decimal(pack*count, 6), "f")})
            current["temp_min_c"],current["temp_max_c"]=merged_temperature(current,lo,hi)
            current["mass"] += count*box_mass
            current["volume"] += count*box_volume
            current["norm"] += Fraction(count, norm_boxes)
            remaining -= count
    return {"strategy": STRATEGY, "pallets": pallets, "pallet_statistics": [
        {"pallet": i, "assembly_group": x["group"],
         "goods_weight_kg": format(exact_decimal(x["mass"]), "f"),
         "temp_min_c":str(x["temp_min_c"]) if x["temp_min_c"] is not None else None,
         "temp_max_c":str(x["temp_max_c"]) if x["temp_max_c"] is not None else None,
         "goods_volume_m3": format(exact_decimal(x["volume"], 36), "f"),
         "norm_share": {"numerator": x["norm"].numerator, "denominator": x["norm"].denominator}}
        for i, x in enumerate(statistics, 1)],
        "physical_capacity_verified": False, "stock_changed": False}
