"""C-0175: the article's published unit coefficients (current policy version per input unit) for order-line normalization.
The same registry and latest-version rule as inventory.sap_quantity; read inside the caller's transaction, no writes."""
from typing import Any
from ..domain.order_units import Conversion


def article_conversions(cur: Any, article: str, units: set[str]) -> dict[str, Conversion]:
    if not units:
        return {}
    binds = {f"u{i}": unit for i, unit in enumerate(sorted(units))}
    cur.execute("select u.INPUT_UOM,u.NUMERATOR,u.DENOMINATOR,u.BASE_UOM,u.BASE_SCALE,u.POLICY_VERSION from RRL_STOCK_UOM_CONVERSION u "
                "where u.ARTICUL=:article and u.INPUT_UOM in(" + ",".join(":" + k for k in binds) + ") and u.POLICY_VERSION="
                "(select max(v.POLICY_VERSION) from RRL_STOCK_UOM_CONVERSION v where v.ARTICUL=u.ARTICUL and v.INPUT_UOM=u.INPUT_UOM)",
                article=article, **binds)
    found: dict[str, Conversion] = {}
    ambiguous: set[str] = set()
    for unit, numerator, denominator, base, scale, version in cur.fetchall():
        if unit in found or unit in ambiguous:  # several rows of the same latest version: no coefficient rather than a guess
            found.pop(unit, None); ambiguous.add(unit); continue
        found[unit] = Conversion(int(numerator), int(denominator), str(base), int(scale or 0), int(version))
    return found
