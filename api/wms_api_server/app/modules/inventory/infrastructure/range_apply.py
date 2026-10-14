"""Rare publication uses existing CONFIG fence; source recalculated on same cursor."""
from datetime import date
from decimal import Decimal
from typing import Any
import oracledb
from ...platform.public import read_oracle_json, stock_configuration_transaction
from ..contracts_slotting import SlottingError
from .range_command import range_command
from .slotting_demand_reader import SlottingDemand

class RangeApply:
    def __init__(self, gateway: Any, reader: SlottingDemand) -> None:
        self.gateway = gateway; self.reader = reader

    def approve(self, ware: int, article: str, proposal: str, operation: str, reason: str,
                geometry: bool, compatibility: bool, actor: str) -> dict[str, Any]:
        body = {"proposal_id": proposal, "reason": reason, "geometry_checked": geometry,
                "product_compatibility_checked": compatibility}
        try:
            with self.gateway.transaction("Range approval historical replay probe") as cur:
                probe = range_command(cur, ware, article, operation, "APPROVE", actor, body)
            if probe["status"] != "SOURCE_RECOMPUTATION_REQUIRED":
                return probe
            with stock_configuration_transaction(self.gateway, "Publish original pick range and drain policy", actor, "pick_topology_edit") as cur:
                confirmed = range_command(cur, ware, article, operation, "APPROVE", actor, body)
                if confirmed["status"] != "SOURCE_RECOMPUTATION_REQUIRED":
                    return confirmed
                cur.execute("""select to_clob(o.REQUEST_JSON),p.SOURCE_SIGNATURE from RRL_PICK_RANGE_PROPOSAL p
                    join RRL_PICK_RANGE_OPERATION o on o.OPERATION_ID=p.PROPOSAL_ID
                    where p.PROPOSAL_ID=:id and p.WARE_ID=:ware and p.ARTICLE=:article""",
                    id=proposal, ware=ware, article=article)
                row = cur.fetchone()
                if row is None:
                    raise SlottingError("PICK_RANGE_PROPOSAL_NOT_FOUND", "Черновик не найден в указанном складе", 404)
                request = read_oracle_json(row[0])
                source = self.reader.snapshot(cur, ware, article,
                    date.fromisoformat(request["period_from"]), date.fromisoformat(request["period_to_exclusive"]),
                    None if request["declared_period_forecast"] is None else Decimal(request["declared_period_forecast"]),
                    request["forecast_base_uom"], actor,
                    None if request["declared_pallet_gross_weight_kg"] is None else Decimal(request["declared_pallet_gross_weight_kg"]),
                    request["recommendation_costs"],request.get("candidate_pick_route_id"))
                if source["source_signature"] != row[1]:
                    raise SlottingError("PICK_RANGE_SOURCE_CHANGED", "Исходные данные изменились: требуется новое предложение")
                return range_command(cur, ware, article, operation, "APPROVE", actor, body, source)
        except oracledb.DatabaseError as exc:
            raise map_range_error(exc) from exc

    def close(self, ware: int, article: str, mapping: int, operation: str, reason: str, actor: str) -> dict[str, Any]:
        try:
            with stock_configuration_transaction(self.gateway, "Finish empty original pick-range drain", actor, "pick_topology_edit") as cur:
                return range_command(cur, ware, article, operation, "CLOSE_DRAIN", actor,
                    {"pick_face_articul_id": mapping, "reason": reason})
        except oracledb.DatabaseError as exc:
            raise map_range_error(exc) from exc

def map_range_error(exc: oracledb.DatabaseError) -> SlottingError:
    code = getattr(exc.args[0], "code", 0)
    if code == 1403:
        return SlottingError("PICK_RANGE_APPLY_SOURCE_NOT_FOUND", "Исходное предложение или правило отсутствует", 404)
    if 20800 <= code <= 20999:
        return SlottingError("PICK_RANGE_APPLY_REJECTED", str(exc.args[0]).split("\n", 1)[0], 403 if code == 20882 else 409)
    return SlottingError("PICK_RANGE_APPLY_UNCONFIRMED", "Повторите исходную команду без изменения идентификатора", 503)
