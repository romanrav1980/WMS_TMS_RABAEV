"""Reuse existing pallet identities; quantities remain on physical leaves."""
import json
from decimal import Decimal
from typing import Any
import oracledb
from fastapi import HTTPException
from ..domain.historical_hu import departure_subtree
from .hu_placement_read import recorded_placement
from .hu_view_access import assert_hu_view, assert_resolved_hu_view, assert_hu_stock_owners
from .hu_thermal_read import hu_thermal_admission
from .hu_identifier_resolution import resolve_hu_rows
from ....transaction_gateway import TransactionGateway
from ..contracts_stock import StockCommand
from .stock_posting_uow import StockPosting
from ..domain.pallet_identifiers import normalize_incoming_sscc


class WarehouseHu:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def preview(self, identifier: str, actor: str) -> dict:
        with self.gateway.transaction("Warehouse HU composition READ ONLY") as cur:
            if not getattr(self.gateway, "transaction_bound", False):
                cur.execute("set transaction read only")
            bound = WarehouseHu(TransactionGateway(cur))
            data = bound._preview(identifier, actor)
            assert_hu_view(cur, actor, int(data["warehouse"]))
            assert_hu_stock_owners(cur, actor, data)
            data["thermal_admission"] = hu_thermal_admission(cur, data)
            data["placement"] = recorded_placement(cur, data)
            if data.get("case_task_id") is not None:
                cur.execute("select OPERATION_ID,PALLET_TYPE_ID,OWNER_WARE_ID from RRL_TARE_BOOK where PLACE_KIND='CASE'and PLACE_ID=:p_case and STATUS='HELD' fetch first 2 rows only",
                            p_case=str(data["case_task_id"]))
                books = cur.fetchall()
                if len(books) > 1:
                    raise HTTPException(409, "CASE_TARE_BOOK_AMBIGUOUS")
                data["tare_booking"] = ({"operation_id": books[0][0], "pallet_type_id": int(books[0][1]),
                                         "warehouse": int(books[0][2]), "nested_asset_preserved": True} if books else None)
            return data

    def _preview(self, identifier: str, actor: str) -> dict:
        normalized = normalize_incoming_sscc(identifier)
        case_number = identifier[5:] if identifier.startswith("CASE:") else ""
        case_id = (int(case_number) if case_number.isascii() and case_number.isdigit()
                   and len(case_number) <= 18 and str(int(case_number)) == case_number else None)
        rows = resolve_hu_rows(self.gateway, identifier, normalized, case_id)
        if not rows:
            raise HTTPException(404, "Грузовое место не найдено")
        if len(rows) != 1:
            raise HTTPException(409, "Идентификатор неоднозначен; укажите внутренний идентификатор паллеты")
        assert_resolved_hu_view(self.gateway, rows[0], actor)
        try:
            if rows[0].get("hu_shipped_operation"):
                raw = self.gateway.fetch_all("select RESULT_JSON SNAPSHOT from RRL_STOCK_OPERATION where OPERATION_ID=:p_op and STATE='APPLIED'",
                                             {"p_op":rows[0]["hu_shipped_operation"]})
                if not raw:
                    raise HTTPException(409,"История отгрузки грузового места недоступна")
                departure=raw[0]["snapshot"] if isinstance(raw[0]["snapshot"],dict) else json.loads(raw[0]["snapshot"])
                try:
                    snapshot=departure_subtree(departure["composition_at_departure"],rows[0]["uid_pallet"])
                except ValueError as exc:
                    raise HTTPException(409,"История состава грузового места противоречива") from exc
                snapshot["status"]="SHIPPED"
                snapshot["departure_operation_id"]=rows[0]["hu_shipped_operation"]
                snapshot["historical_composition"]=True
                raw=[{"snapshot":json.dumps(snapshot)}]
            elif rows[0].get("case_task_id") is not None:
                raw = self.gateway.fetch_all("select RRL_STOCK_HU_READ.case_snapshot_json(:p_task) SNAPSHOT from dual",
                                             {"p_task": rows[0]["case_task_id"]})
            else:
                raw = self.gateway.fetch_all(
                    "select RRL_STOCK_HU_READ.snapshot_json(:p_uid) SNAPSHOT from dual", {"p_uid": rows[0]["uid_pallet"]})
        except oracledb.DatabaseError as exc:
            error = exc.args[0]
            if 20800 <= abs(getattr(error, "code", 0)) <= 20999:
                raise HTTPException(409, detail={"code": "HU_COMPOSITION_UNAVAILABLE",
                    "reason": str(getattr(error, "message", exc)).split("\n", 1)[0]}) from exc
            raise
        result = raw[0]["snapshot"] if isinstance(raw[0]["snapshot"], dict) else json.loads(raw[0]["snapshot"])
        totals = {}
        weight = Decimal(0)
        unknown = 0
        unknown_tare = 0
        measured_cases={node["case_task_id"] for node in result["nodes"]if node["kind"]=="CASE"and node.get("gross_weight_kg")is not None}
        for node in result["nodes"]:
            covered=node["kind"]=="STOCK"and node.get("case_task_id")in measured_cases
            if node["kind"]=="CASE" and node.get("tare_weight_kg") is None:
                unknown_tare += 1
            if node["kind"]=="CASE"and node.get("gross_weight_kg")is not None:
                weight += Decimal(node["gross_weight_kg"])
            elif not covered:
                weight += Decimal(node.get("tare_weight_kg") or "0")
            if node["kind"] == "STOCK":
                key = (node["article"], node["base_uom"])
                totals[key] = totals.get(key, Decimal(0)) + Decimal(node["quantity"])
                if covered:
                    continue
                if node.get("weight_kg") is None:
                    unknown += 1
                else:
                    weight += Decimal(node["weight_kg"])
        result["quantities"] = [{"article": article, "base_uom": base, "quantity": format(qty, "f")}
                                for (article, base), qty in sorted(totals.items())]
        result["gross_weight_kg"] = None if unknown or unknown_tare else format(weight, "f")
        result["unknown_weight_leaves"] = unknown
        result["unknown_tare_containers"] = unknown_tare
        return result

    def target_slots(self, cell: str, warehouse: int, actor: str) -> list[dict]:
        with self.gateway.transaction("Warehouse HU target slots READ ONLY") as cur:
            if not getattr(self.gateway, "transaction_bound", False):
                cur.execute("set transaction read only")
            assert_hu_view(cur, actor, warehouse)
            return WarehouseHu(TransactionGateway(cur))._target_slots(cell, warehouse)

    def _target_slots(self, cell: str, warehouse: int) -> list[dict]:
        return self.gateway.fetch_all("""
            select sl.CELL_SLOT_ID,sl.SLOT_CODE,sl.WIDTH_M,sl.DEPTH_M,sl.HEIGHT_M,
                   sl.CAPACITY_WEIGHT_KG,sl.CAPACITY_VOLUME_M3,
                   case when nvl(c.BLOCKED_FOR_REMAINS,0)!=0 or nvl(c.BLOCKED_FOR_POPOLNENIE,0)!=0
                     or nvl(c.BLOCKED_FOR_ACCEPT,0)!=0 then 'CELL_BLOCKED'
                    when exists(select 1 from RRL_RECEIPT_SLOT_CLAIM cl where cl.CELL_SLOT_ID=sl.CELL_SLOT_ID
                      and cl.STATUS in('RESERVED','OCCUPIED')) then 'SLOT_OCCUPIED'
                    when (exists(select 1 from RRL_REMAINS r where r.CELL=c.CELL and r.REMAIN>0)
                     or exists(select 1 from RRL_PALLETS p where p.HU_KIND='CONTAINER' and p.HU_CURRENT_CELL=c.CELL))
                     and not exists(select 1 from RRL_RECEIPT_SLOT_CLAIM cl join RRL_PALLETS p on p.UID_PALLET=cl.UID_PALLET
                       where cl.CELL=c.CELL and cl.STATUS='OCCUPIED' and ((p.HU_KIND='CONTAINER' and p.HU_CURRENT_CELL=c.CELL)
                         or(p.HU_KIND='STOCK' and cl.HU_STOCK_COMPOSITION_VERSION=p.STOCK_COMPOSITION_VERSION
                           and cl.HU_UNIT_SIGNATURE is not null and exists(select 1 from RRL_REMAINS sr
                             where sr.UID_POLETA=p.UID_PALLET and sr.CELL=c.CELL and sr.REMAIN>0)))
                         and cl.HU_COMPOSITION_VERSION=p.HU_CONTENT_VERSION and cl.HU_GROSS_WEIGHT_KG is not null
                         and cl.HU_BOUNDING_VOLUME_M3 is not null) then 'CELL_MEASUREMENTS_REQUIRED'
                    when exists(select 1 from RRL_WAREHOUSE_TASK wt where wt.TO_CELL=c.CELL
                      and wt.STATUS not in('DONE','CANCELLED') and(wt.TO_CELL_SLOT_ID=sl.CELL_SLOT_ID
                        or wt.TO_CELL_SLOT_ID is null or wt.HU_MEASUREMENTS_JSON is null))
                       then 'ARRIVAL_PLANNED' end UNAVAILABLE_REASON
              from RRL_CELLS c join RRL_TOPOLOGY_CELL tc on tc.LEGACY_CELL_CODE=c.CELL
               and tc.WARE_ID=c.WARE_ID and tc.ACTIVE=1
              join RRL_TOPOLOGY_CELL_SLOT sl on sl.TOPOLOGY_CELL_ID=tc.TOPOLOGY_CELL_ID
               and sl.ACTIVE=1 and sl.SLOT_KIND='STORAGE_SLOT'
             where c.CELL=:p_cell and c.WARE_ID=:p_warehouse and nvl(c.IS_SYSTEM,0)=0 and nvl(c.OTBOR,0)=0
               and tc.TOPOLOGY_ID=(select max(TOPOLOGY_ID) from RRL_WAREHOUSE_TOPOLOGY
                 where WARE_ID=:p_warehouse and STATUS='PUBLISHED')
             order by sl.STORAGE_ORDER nulls last,sl.SLOT_CODE fetch first 200 rows only
            """, {"p_cell": cell, "p_warehouse": warehouse})

    def command(self, kind: str, uid: str, operation_id: str, metadata: dict, actor: str) -> dict:
        metadata = dict(metadata)
        child_owner=metadata.get("child_uid")
        if metadata.get("child_case_task_id") is not None:
            rows=self.gateway.fetch_all("select SSCC from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_task",
                                        {"p_task":metadata["child_case_task_id"]})
            if rows:
                child_owner=rows[0]["sscc"]
        for name, owner in (("scan_container", uid), ("scan_child", child_owner)):
            if metadata.get(name) != owner:
                metadata[name] = normalize_incoming_sscc(metadata.get(name))
        return StockPosting().post(StockCommand(
            operation_id=operation_id, command_type=kind, actor=actor, lines=(),
            source={"uid": uid}, metadata=metadata))
