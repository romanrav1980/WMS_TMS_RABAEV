"""Physical facts supplement existing ST-trip assignment and load plans."""
from collections.abc import Callable
from typing import Any
import json
import oracledb
from ..contracts import TransportLoadingError
from ...platform.public import read_oracle_json


class TransportLoading:
    def __init__(self, gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> None:
        self.gateway = gateway
        self.post = post

    def status(self, task_id: int, actor: str) -> dict[str, Any]:
        from .loading_status import loading_status
        return loading_status(self.gateway, task_id, actor)

    def load(self, operation_id: str, identifier: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]:
        return self.post("HU_SHIP", operation_id, {"uid": identifier}, metadata, actor)

    def preview_bulk(self, identifier: str, actor: str) -> dict[str, Any]:
        from .bulk_loading_read import bulk_loading_preview
        try:return bulk_loading_preview(self.gateway,identifier,actor)
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code==20882:
                raise TransportLoadingError("BULK_BOX_FORBIDDEN",str(exc.args[0]).split("\n",1)[0],status=403)from exc
            if code==1403 or 20800<=abs(code)<=20999:
                raise TransportLoadingError("BULK_BOX_SOURCE_UNAVAILABLE",str(exc.args[0]).split("\n",1)[0])from exc
            raise

    def unload(self, operation_id: str, load_operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]:
        return self.post("UNLOAD_SHIPMENT", operation_id, {"load_operation_id": load_operation_id}, metadata, actor)

    def depart(self, operation_id: str, task_id: int, actor: str, temperature_confirmation: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.post("TRIP_DEPART", operation_id, {"task_id": task_id},
                         {"temperature_confirmation": temperature_confirmation} if temperature_confirmation is not None else {}, actor)


    def preview_single(self, shipment_identifier: str, actor: str | None = None) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Current warehouse standalone loading preview") as q:
                q.execute("set transaction read only")
                q.execute("select RRL_STOCK_LOADING_READ.preview_json(:identifier,:actor) from dual",
                          identifier=shipment_identifier,actor=actor)
                return read_oracle_json(q.fetchone()[0])
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code==20882:
                raise TransportLoadingError("SINGLE_LOAD_FORBIDDEN",str(exc.args[0]).split("\n",1)[0],status=403) from exc
            if code==1403 or 20800<=abs(code)<=20999:
                raise TransportLoadingError("SINGLE_LOAD_SOURCE_UNAVAILABLE",str(exc.args[0]).split("\n",1)[0]) from exc
            raise

    def load_single(self, operation_id: str, shipment_identifier: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]:
        return self.post("LOAD_SHIPMENT",operation_id,{"pallet_identifier":shipment_identifier},metadata,actor)

    def preview_reconciliation(self, shipping_operation_id: str) -> dict[str, Any]:
        try:
            rows=self.gateway.fetch_all("select RRL_STOCK_LOAD_RECONCILE_READ.preview_json(:op) PREVIEW from dual",{"op":shipping_operation_id})
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code==1403 or 20800<=abs(code)<=20999:
                raise TransportLoadingError("RECONCILIATION_SOURCE_UNAVAILABLE",str(exc.args[0]).split("\n",1)[0]) from exc
            raise
        value=rows[0]["preview"]
        return value if isinstance(value,dict) else json.loads(value)

    def reconcile(self, operation_id: str, shipping_operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]:
        return self.post("RECONCILE_HU_LOAD",operation_id,{"shipping_operation_id":shipping_operation_id},metadata,actor)
