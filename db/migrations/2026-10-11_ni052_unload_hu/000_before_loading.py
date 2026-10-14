"""Physical facts supplement existing ST-trip assignment and load plans."""
from collections.abc import Callable
from typing import Any
import json
import oracledb
from ..contracts import TransportLoadingError


class TransportLoading:
    def __init__(self, gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> None:
        self.gateway = gateway
        self.post = post

    def status(self, task_id: int) -> dict[str, Any]:
        trips = self.gateway.fetch_all(
            "select ID,TRANSPORT,DOCK,CONDITION,VODITEL_ID from RRL_TRANSPORT_TASK where ID=:id",
            {"id": task_id})
        if len(trips) != 1:
            raise TransportLoadingError("TRIP_NOT_FOUND", "Рейс не найден", status=404)
        members = self.gateway.fetch_all("""
            select sp.ID,sp.ST_NUMBER,sp.PALLET_UID,sp.CONDITION,ls.DESTINATION_ADDR,lf.LOAD_OPERATION_ID,
                   coalesce(lf.ROOT_UID,'CASE:'||to_char(lf.ROOT_CASE_TASK_ID)) ROOT_UID,lf.STATUS LOAD_STATUS,lf.VEHICLE_NUMBER,lf.DOCK
              from RRL_SBORKA_PALLETS sp left join RRL_TT_HU_LOAD_ST ls
                on ls.SBORKA_PALLET_ID=sp.ID and ls.ACTIVE_FLAG=1
              left join RRL_TT_HU_LOAD_FACT lf on lf.LOAD_OPERATION_ID=ls.LOAD_OPERATION_ID
             where sp.TRANSTASK_ID=:id order by sp.ID fetch first 201 rows only
        """, {"id": task_id})
        if len(members) > 200:
            raise TransportLoadingError("TRIP_MEMBER_BOUND_200", "Разбейте рейс: больше 200 СТ")
        loads = self.gateway.fetch_all("""
            select LOAD_OPERATION_ID,coalesce(ROOT_UID,'CASE:'||to_char(ROOT_CASE_TASK_ID)) ROOT_UID,VEHICLE_NUMBER,DOCK,STATUS,
                   to_char(GROSS_WEIGHT_KG,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') GROSS_WEIGHT_KG,
                   LOADED_BY,LOADED_AT,DEPARTURE_OPERATION_ID,DEPARTED_AT,CONTENT_VERSION,ROOT_CASE_TASK_ID,
                   json_value(COMPOSITION_JSON,'$.nodes[0].sscc') ROOT_SCAN_IDENTIFIER,
                   json_value(COMPOSITION_JSON,'$.cell') ORIGIN_CELL
              from RRL_TT_HU_LOAD_FACT where TT_ID=:id order by LOADED_AT,LOAD_OPERATION_ID
               fetch first 201 rows only
        """, {"id": task_id})
        if len(loads) > 200:
            raise TransportLoadingError("TRIP_LOAD_HISTORY_BOUND_200", "История рейса превышает окно")
        pending = [row["id"] for row in members if row.get("load_status") not in {"LOADED", "DEPARTED"}]
        return {"trip": trips[0], "members": members, "physical_places": loads,
                "loaded_place_count": sum(row["status"] in {"LOADED", "DEPARTED"} for row in loads),
                "pending_st_ids": pending, "all_members_physically_loaded": bool(members) and not pending,
                "logically_shipped_without_load_st_ids":[row["id"] for row in members if row.get("condition")==2 and not row.get("load_operation_id")],
                "departure_requires_server_confirmation": True}

    def load(self, operation_id: str, identifier: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]:
        return self.post("HU_SHIP", operation_id, {"uid": identifier}, metadata, actor)

    def unload(self, operation_id: str, load_operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]:
        return self.post("UNLOAD_SHIPMENT", operation_id, {"load_operation_id": load_operation_id}, metadata, actor)

    def depart(self, operation_id: str, task_id: int, actor: str) -> dict[str, Any]:
        return self.post("TRIP_DEPART", operation_id, {"task_id": task_id}, {}, actor)


    def preview_single(self, shipment_identifier: str) -> dict[str, Any]:
        try:
            rows=self.gateway.fetch_all("select RRL_STOCK_LOADING_READ.preview_json(:identifier) PREVIEW from dual",{"identifier":shipment_identifier})
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code==1403 or 20800<=abs(code)<=20999:
                raise TransportLoadingError("SINGLE_LOAD_SOURCE_UNAVAILABLE",str(exc.args[0]).split("\n",1)[0]) from exc
            raise
        value=rows[0]["preview"]
        return value if isinstance(value,dict) else json.loads(value)

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
