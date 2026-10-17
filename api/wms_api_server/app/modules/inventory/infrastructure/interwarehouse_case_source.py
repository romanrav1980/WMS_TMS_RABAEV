"""The native grouped archive owns CASE eligibility and frozen source membership."""
from decimal import Decimal
from typing import Any
from ...platform.public import read_oracle_json


def read_case_group(cursor: Any, load: str, actor: str) -> dict[str, Any]:
    cursor.execute("select RRL_IW_GROUP_SOURCE.source_json(:load_id,:actor)from dual", load_id=load, actor=actor)
    source = read_oracle_json(cursor.fetchone()[0])
    totals: dict[tuple[str, str], Decimal] = {}
    for item in source["lots"]:
        key = item["article"], item["base_uom"]
        totals[key] = totals.get(key, Decimal(0)) + Decimal(item["quantity"])
    return {**source, "physical_place_count": 1, "source_eligible": True, "blockers": [],
        "quantity_by_article": [{"article": article, "base_uom": unit, "quantity": format(value, "f")}
                                for (article, unit), value in sorted(totals.items())],
        "stock_changed": False, "grouped_receipt_available": True,
        "regulatory_ack_verified": False, "external_sap_ack": False}
