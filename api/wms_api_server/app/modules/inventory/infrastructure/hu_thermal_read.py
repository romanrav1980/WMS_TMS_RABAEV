"""Normative cell/SKU admission; no observed temperature or hardware assertion."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json


def hu_thermal_admission(cursor: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    if snapshot.get("historical_composition"):
        return dict(domain="HU_THERMAL_ADMISSION", version=1, status="HISTORICAL_NOT_EVALUATED",
                    allowed=None, policy_only=True, observed_temperature_c=None)
    nodes = json.dumps(snapshot["nodes"], ensure_ascii=False, separators=(",", ":"))
    value = cursor.callfunc("RRL_HU_THERMAL_READ.admission_json", oracledb.DB_TYPE_CLOB,
                            [nodes, snapshot["warehouse"], snapshot["cell"], None])
    return read_oracle_json(value)
