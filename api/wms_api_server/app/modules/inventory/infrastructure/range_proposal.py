"""Native immutable draft journal; fresh source recomputation before draft creation."""
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_range_proposal import RangeDraft
from ..contracts_slotting import SlottingError
from .slotting_demand_reader import SlottingDemand
from .range_command import range_command
from .range_apply import RangeApply

class RangeProposal:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway
        self.reader = SlottingDemand(gateway)
        self.apply = RangeApply(gateway, self.reader)

    def _command(self, ware: int, article: str, operation: str, action: str, actor: str,
                 body: dict[str, Any], source: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Native immutable slotting proposal command") as cur:
                return range_command(cur, ware, article, operation, action, actor, body, source)
        except oracledb.DatabaseError as exc:
            code = getattr(exc.args[0], "code", 0)
            if code == 1403:
                raise SlottingError("PICK_RANGE_PROPOSAL_NOT_FOUND", "Предложение не найдено", 404) from exc
            if 20800 <= code <= 20999:
                raise SlottingError("PICK_RANGE_COMMAND_REJECTED", str(exc.args[0]).split("\n", 1)[0], 403 if code == 20882 else 409) from exc
            raise SlottingError("PICK_RANGE_COMMAND_UNCONFIRMED", "Повторите исходную команду с тем же идентификатором", 503) from exc

    def save(self, ware: int, article: str, command: RangeDraft, actor: str) -> dict[str, Any]:
        body = {"period_from": command.period_from.isoformat(), "period_to_exclusive": command.period_to_exclusive.isoformat(),
                "declared_period_forecast": None if command.declared_period_forecast is None else format(command.declared_period_forecast, "f"),
                "forecast_base_uom": command.forecast_base_uom,
                "declared_pallet_gross_weight_kg": None if command.declared_pallet_gross_weight_kg is None else format(command.declared_pallet_gross_weight_kg, "f"),
                "recommendation_costs": command.recommendation_costs, "expected_source_signature": command.expected_source_signature,
                "reason": command.reason}
        if command.candidate_pick_route_id is not None:
            body["candidate_pick_route_id"]=command.candidate_pick_route_id
        probe = self._command(ware, article, command.operation_id, "SAVE_DRAFT", actor, body)
        if probe["status"] != "SOURCE_RECOMPUTATION_REQUIRED":
            return probe
        source = self.reader.preview(ware, article, command.period_from, command.period_to_exclusive,
            command.declared_period_forecast, command.forecast_base_uom, actor,
            command.declared_pallet_gross_weight_kg, command.recommendation_costs, command.candidate_pick_route_id)
        if source["source_signature"] != command.expected_source_signature:
            raise SlottingError("PICK_RANGE_SOURCE_CHANGED", "Исходные данные изменились: пересчитайте предложение")
        return self._command(ware, article, command.operation_id, "SAVE_DRAFT", actor, body, source)

    def cancel(self, ware: int, article: str, proposal: str, operation: str, reason: str, actor: str) -> dict[str, Any]:
        return self._command(ware, article, operation, "CANCEL_DRAFT", actor, {"proposal_id": proposal, "reason": reason})

    def approve(self, ware: int, article: str, proposal: str, operation: str, reason: str,
                geometry: bool, compatibility: bool, actor: str) -> dict[str, Any]:
        return self.apply.approve(ware, article, proposal, operation, reason, geometry, compatibility, actor)

    def close(self, ware: int, article: str, mapping: int, operation: str, reason: str, actor: str) -> dict[str, Any]:
        return self.apply.close(ware, article, mapping, operation, reason, actor)

    def get(self, ware: int, article: str, proposal: str, actor: str) -> dict[str, Any]:
        with self.gateway.transaction("Original range proposal READ ONLY") as cur:
            cur.execute("set transaction read only")
            cur.execute("""select count(*)from RUSERS where ID=:actor and nvl(DELETED,0)=0
                and(WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(ID,'pick_topology_view')=1""",
                actor=actor, ware=ware)
            if cur.fetchone()[0] != 1:
                raise SlottingError("PICK_RANGE_CURRENT_VIEW_ACTOR_REQUIRED", "Требуется актуальный склад пользователя", 403)
            cur.execute("""select p.SOURCE_SIGNATURE,to_clob(p.SOURCE_JSON),to_clob(o.REQUEST_JSON),
                o.ACTOR,to_char(o.CREATED_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'),
                c.CANCEL_OPERATION_ID,c.REASON,co.ACTOR,
                to_char(co.CREATED_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'),
                ra.OPERATION_ID,ao.ACTOR,to_char(ao.CREATED_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')
                from RRL_PICK_RANGE_PROPOSAL p join RRL_PICK_RANGE_OPERATION o on o.OPERATION_ID=p.PROPOSAL_ID
                left join RRL_PICK_RANGE_CANCEL c on c.PROPOSAL_ID=p.PROPOSAL_ID
                left join RRL_PICK_RANGE_OPERATION co on co.OPERATION_ID=c.CANCEL_OPERATION_ID
                left join RRL_PICK_RANGE_APPROVAL ra on ra.PROPOSAL_ID=p.PROPOSAL_ID
                left join RRL_PICK_RANGE_OPERATION ao on ao.OPERATION_ID=ra.OPERATION_ID
                where p.PROPOSAL_ID=:proposal and p.WARE_ID=:ware and p.ARTICLE=:article""",
                proposal=proposal, ware=ware, article=article)
            row = cur.fetchone()
            if row is None:
                raise SlottingError("PICK_RANGE_PROPOSAL_NOT_FOUND", "Предложение не найдено в указанном складе", 404)
            cur.execute("""select m.PICK_FACE_ARTICUL_ID,m.ROLE_CODE,f.CELL_CODE,a.ACTIVE,s.MODE_CODE,s.APPROVAL_OPERATION_ID
                from RRL_PICK_RANGE_MEMBER m join RRL_PICK_FACE_ARTICUL a on a.PICK_FACE_ARTICUL_ID=m.PICK_FACE_ARTICUL_ID
                join RRL_PICK_FACE f on f.PICK_FACE_ID=a.PICK_FACE_ID
                left join RRL_PICK_RANGE_STATUS s on s.PICK_FACE_ARTICUL_ID=a.PICK_FACE_ARTICUL_ID
                where m.PROPOSAL_ID=:proposal and f.WARE_ID=:ware and a.ARTICUL=:article
                order by m.ROLE_CODE,m.PICK_FACE_ARTICUL_ID fetch first 201 rows only""",
                proposal=proposal,ware=ware,article=article)
            members=[dict(zip(["pick_face_articul_id","role","cell","mapping_active","current_mode","current_approval_operation_id"],item))
                     for item in cur.fetchall()]
            if len(members)>200:raise SlottingError("PICK_RANGE_MEMBER_BOUND","Сузьте область диапазона")
            return {"proposal_id": proposal, "warehouse_id": ware, "article": article,
                    "status": "APPROVED" if row[9] is not None else "CANCELLED" if row[5] is not None else "DRAFT", "source_signature": row[0],
                    "source": read_oracle_json(row[1]), "request": read_oracle_json(row[2]),
                    "created_by": row[3], "created_at": row[4],
                    "cancellation": None if row[5] is None else {"operation_id": row[5], "reason": row[6], "actor": row[7], "at": row[8]},
                    "approval":None if row[9]is None else {"operation_id":row[9],"actor":row[10],"at":row[11]},
                    "range_members":members,"range_applied":row[9]is not None,"stock_changed":False,
                    "approved_range_superseded":row[9]is not None and any(m["role"]=="NEW" and
                        (m["current_mode"]!="ACTIVE"or m["current_approval_operation_id"]!=row[9])for m in members)}
