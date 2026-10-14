"""Durable cluster result; all original native writers share one Oracle UOW."""
from datetime import date
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from .plan_application import TransportPlanError
from .trip_edit import trip_error


def create_existing_cluster(
    gateway: Any, district: str, day: date, transport_type: str,
    fields: dict[str, Any], numbers: list[str], actor: str,
    operation_id: str, warehouse_ids: list[int] | None = None,
) -> dict[str, Any]:
    selected=sorted(set(numbers))
    if len(selected)>200:
        raise TransportPlanError("CLUSTER_SOURCE_BOUND_200","Разделите кластер: разрешено не более200 СТ")
    request={"raion":district,"stdate":day.isoformat(),"transtype":transport_type,
        "vehicle":fields.get("transport"),"driver_id":fields.get("voditel_id"),
        "dock":fields.get("dock"),"ware_ids":None if warehouse_ids is None else sorted(set(warehouse_ids))}
    body=json.dumps(request,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    if len(body)>2000 or len(body.encode("utf-8"))>4000:
        raise TransportPlanError("CLUSTER_REQUEST_BOUND","Сократите район и список складов",422)
    try:
        with gateway.transaction("Idempotent atomic existing cluster trip and assignment") as cursor:
            result=cursor.var(oracledb.DB_TYPE_CLOB)
            cursor.callproc("RRL_CLUSTER_CREATE_API.create_cluster",
                [operation_id,actor,body,json.dumps(selected,ensure_ascii=False),result])
            return read_oracle_json(result.getvalue())
    except oracledb.DatabaseError as exc:
        raise trip_error(exc) from exc
