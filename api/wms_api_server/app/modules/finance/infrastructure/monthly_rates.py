"""Monthly composition shares the original rate transaction and version history."""
from typing import Any
from ..contracts import LogisticsCostError
from ..domain.monthly_rate import monthly_components
from .box_rates import set_box_rate


def set_monthly_rate(gateway: Any, ware: int, currency: str, month: str, picking: str,
                     common: str, boxes: str, version: int, reason: str,
                     reference: str, actor: str) -> dict[str, Any]:
    try:
        components = monthly_components(month, picking, common, boxes)
    except ValueError as exc:
        raise LogisticsCostError("COST_MONTHLY_COMPONENTS_INVALID", str(exc), 422) from exc
    return set_box_rate(gateway, ware, currency, components["combined_rate"],
                        components["month"] + "-01", version, reason, reference,
                        actor, components=components)
