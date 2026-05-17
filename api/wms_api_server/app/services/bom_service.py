from datetime import date
from typing import Any

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway
from ..schemas import (
    BomCalculateRequest,
    BomCloneRequest,
    BomCreateRequest,
    BomLineRequest,
    BomUpdateRequest,
)


class BomService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def list_boms(
        self,
        target_articul: str | None = None,
        status: str | None = None,
        is_primary: int | None = None,
        active_on: date | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {"limit": clamp_limit(limit)}
        if target_articul:
            conditions.append("b.TARGET_ARTICUL = :target_articul")
            params["target_articul"] = target_articul.upper()
        if status:
            conditions.append("b.STATUS = :status")
            params["status"] = status.upper()
        if is_primary is not None:
            conditions.append("b.IS_PRIMARY = :is_primary")
            params["is_primary"] = 1 if int(is_primary) == 1 else 0
        if active_on is not None:
            conditions.append("b.VALID_FROM <= :active_on")
            conditions.append("nvl(b.VALID_TO, date '2999-12-31') >= :active_on")
            params["active_on"] = active_on
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select b.BOM_ID,
                       b.BOM_CODE,
                       b.BOM_NAME,
                       b.TARGET_ARTICUL,
                       b.TARGET_MOD_ID,
                       b.TARGET_GTIN,
                       b.BOM_KIND,
                       b.BASE_QTY,
                       b.BASE_UNIT_CODE,
                       b.IS_PRIMARY,
                       b.STATUS,
                       b.VALID_FROM,
                       b.VALID_TO,
                       b.WARE_ID,
                       b.PRODUCTION_LINE,
                       b.VERSION_NO,
                       b.PARENT_BOM_ID,
                       b.CREATED_AT,
                       b.CREATED_BY,
                       b.UPDATED_AT,
                       b.UPDATED_BY,
                       b.APPROVED_AT,
                       b.APPROVED_BY,
                       (select count(*)
                          from RRL_BOM_LINE l
                         where l.BOM_ID = b.BOM_ID) LINE_COUNT
                  from RRL_BOM b
                  {where_sql}
                 order by b.UPDATED_AT desc nulls last, b.CREATED_AT desc, b.BOM_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def get_bom(self, bom_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """
            select BOM_ID,
                   BOM_CODE,
                   BOM_NAME,
                   TARGET_ARTICUL,
                   TARGET_MOD_ID,
                   TARGET_GTIN,
                   BOM_KIND,
                   BASE_QTY,
                   BASE_UNIT_CODE,
                   IS_PRIMARY,
                   STATUS,
                   VALID_FROM,
                   VALID_TO,
                   WARE_ID,
                   PRODUCTION_LINE,
                   VERSION_NO,
                   PARENT_BOM_ID,
                   COMMENT_TEXT,
                   CREATED_AT,
                   CREATED_BY,
                   UPDATED_AT,
                   UPDATED_BY,
                   APPROVED_AT,
                   APPROVED_BY
              from RRL_BOM
             where BOM_ID = :bom_id
            """,
            {"bom_id": bom_id},
        )
        if not rows:
            return {}
        bom = rows[0]
        bom["lines"] = self.list_lines(bom_id)
        bom["audit"] = self.list_audit(bom_id)
        return bom

    def list_lines(self, bom_id: int) -> list[dict[str, Any]]:
        return self.gateway.fetch_all(
            """
            select BOM_LINE_ID,
                   BOM_ID,
                   LINE_NO,
                   COMPONENT_TYPE,
                   COMPONENT_ARTICUL,
                   COMPONENT_MOD_ID,
                   COMPONENT_NAME,
                   QTY_PER_BASE,
                   UNIT_CODE,
                   LOSS_PERCENT,
                   MIN_TOLERANCE_PCT,
                   MAX_TOLERANCE_PCT,
                   IS_REQUIRED,
                   SUBSTITUTION_GROUP,
                   REPLACEMENT_RATIO,
                   COMMENT_TEXT,
                   CREATED_AT,
                   CREATED_BY,
                   UPDATED_AT,
                   UPDATED_BY
              from RRL_BOM_LINE
             where BOM_ID = :bom_id
             order by LINE_NO, BOM_LINE_ID
            """,
            {"bom_id": bom_id},
        )

    def list_audit(self, bom_id: int) -> list[dict[str, Any]]:
        return self.gateway.fetch_all(
            """
            select BOM_AUDIT_ID,
                   BOM_ID,
                   ACTION_TYPE,
                   OLD_STATUS,
                   NEW_STATUS,
                   MESSAGE,
                   PAYLOAD_JSON,
                   CREATED_AT,
                   CREATED_BY
              from RRL_BOM_AUDIT
             where BOM_ID = :bom_id
             order by BOM_AUDIT_ID desc
            """,
            {"bom_id": bom_id},
        )

    def create_bom(self, request: BomCreateRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_BOM_API.create_bom(
                p_bom_code => :bom_code,
                p_bom_name => :bom_name,
                p_target_articul => :target_articul,
                p_target_mod_id => :target_mod_id,
                p_target_gtin => :target_gtin,
                p_bom_kind => :bom_kind,
                p_base_qty => :base_qty,
                p_base_unit_code => :base_unit_code,
                p_is_primary => :is_primary,
                p_valid_from => :valid_from,
                p_valid_to => :valid_to,
                p_ware_id => :ware_id,
                p_production_line => :production_line,
                p_comment_text => :comment_text,
                p_created_by => :created_by
              );
            end;
            """,
            _model_dict(request),
        )

    def update_bom(self, bom_id: int, request: BomUpdateRequest) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_BOM_API.update_bom(
                p_bom_id => :bom_id,
                p_bom_code => :bom_code,
                p_bom_name => :bom_name,
                p_target_articul => :target_articul,
                p_target_mod_id => :target_mod_id,
                p_target_gtin => :target_gtin,
                p_bom_kind => :bom_kind,
                p_base_qty => :base_qty,
                p_base_unit_code => :base_unit_code,
                p_is_primary => :is_primary,
                p_valid_from => :valid_from,
                p_valid_to => :valid_to,
                p_ware_id => :ware_id,
                p_production_line => :production_line,
                p_comment_text => :comment_text,
                p_updated_by => :updated_by
              );
            end;
            """,
            {"bom_id": bom_id, **_model_dict(request)},
        )

    def add_line(self, bom_id: int, request: BomLineRequest) -> int:
        params = _model_dict(request)
        params.pop("updated_by", None)
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_BOM_API.add_line(
                p_bom_id => :bom_id,
                p_line_no => :line_no,
                p_component_type => :component_type,
                p_component_articul => :component_articul,
                p_component_mod_id => :component_mod_id,
                p_component_name => :component_name,
                p_qty_per_base => :qty_per_base,
                p_unit_code => :unit_code,
                p_loss_percent => :loss_percent,
                p_min_tolerance_pct => :min_tolerance_pct,
                p_max_tolerance_pct => :max_tolerance_pct,
                p_is_required => :is_required,
                p_substitution_group => :substitution_group,
                p_replacement_ratio => :replacement_ratio,
                p_comment_text => :comment_text,
                p_created_by => :created_by
              );
            end;
            """,
            {"bom_id": bom_id, **params},
        )

    def update_line(self, line_id: int, request: BomLineRequest) -> None:
        params = _model_dict(request)
        params.pop("created_by", None)
        self.gateway.execute_plsql(
            """
            begin
              RRL_BOM_API.update_line(
                p_bom_line_id => :bom_line_id,
                p_line_no => :line_no,
                p_component_type => :component_type,
                p_component_articul => :component_articul,
                p_component_mod_id => :component_mod_id,
                p_component_name => :component_name,
                p_qty_per_base => :qty_per_base,
                p_unit_code => :unit_code,
                p_loss_percent => :loss_percent,
                p_min_tolerance_pct => :min_tolerance_pct,
                p_max_tolerance_pct => :max_tolerance_pct,
                p_is_required => :is_required,
                p_substitution_group => :substitution_group,
                p_replacement_ratio => :replacement_ratio,
                p_comment_text => :comment_text,
                p_updated_by => :updated_by
              );
            end;
            """,
            {"bom_line_id": line_id, **params},
        )

    def delete_line(self, line_id: int, deleted_by: str | None = None) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_BOM_API.delete_line(
                p_bom_line_id => :bom_line_id,
                p_deleted_by => :deleted_by
              );
            end;
            """,
            {"bom_line_id": line_id, "deleted_by": deleted_by},
        )

    def approve_bom(self, bom_id: int, user_name: str | None) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_BOM_API.approve_bom(
                p_bom_id => :bom_id,
                p_approved_by => :user_name
              );
            end;
            """,
            {"bom_id": bom_id, "user_name": user_name},
        )

    def block_bom(self, bom_id: int, reason: str | None, user_name: str | None) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_BOM_API.block_bom(
                p_bom_id => :bom_id,
                p_reason => :reason,
                p_updated_by => :user_name
              );
            end;
            """,
            {"bom_id": bom_id, "reason": reason, "user_name": user_name},
        )

    def archive_bom(self, bom_id: int, reason: str | None, user_name: str | None) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_BOM_API.archive_bom(
                p_bom_id => :bom_id,
                p_reason => :reason,
                p_updated_by => :user_name
              );
            end;
            """,
            {"bom_id": bom_id, "reason": reason, "user_name": user_name},
        )

    def make_primary(self, bom_id: int, user_name: str | None) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_BOM_API.make_primary(
                p_bom_id => :bom_id,
                p_updated_by => :user_name
              );
            end;
            """,
            {"bom_id": bom_id, "user_name": user_name},
        )

    def clone_bom(self, source_bom_id: int, request: BomCloneRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_BOM_API.clone_bom(
                p_source_bom_id => :source_bom_id,
                p_bom_code => :bom_code,
                p_valid_from => :valid_from,
                p_valid_to => :valid_to,
                p_created_by => :created_by
              );
            end;
            """,
            {"source_bom_id": source_bom_id, **_model_dict(request)},
        )

    def find_primary(
        self,
        target_articul: str,
        planned_date: date | None = None,
        target_mod_id: int | None = None,
        ware_id: int | None = None,
        production_line: str | None = None,
    ) -> dict[str, Any]:
        bom_id = self.gateway.call_optional_number_plsql(
            """
            begin
              :result := RRL_BOM_API.find_primary_bom(
                p_target_articul => :target_articul,
                p_planned_date => :planned_date,
                p_target_mod_id => :target_mod_id,
                p_ware_id => :ware_id,
                p_production_line => :production_line
              );
            end;
            """,
            {
                "target_articul": target_articul,
                "planned_date": planned_date,
                "target_mod_id": target_mod_id,
                "ware_id": ware_id,
                "production_line": production_line,
            },
        )
        return self.get_bom(bom_id) if bom_id is not None else {}

    def calculate(self, bom_id: int, request: BomCalculateRequest) -> dict[str, Any]:
        bom = self.get_bom(bom_id)
        if not bom:
            raise HTTPException(status_code=404, detail="BOM not found.")
        base_qty = to_float(bom.get("base_qty"))
        planned_qty = float(request.planned_qty)
        if base_qty <= 0:
            raise HTTPException(status_code=409, detail="BOM base quantity is invalid.")
        if planned_qty <= 0:
            raise HTTPException(status_code=400, detail="planned_qty must be greater than zero.")

        factor = planned_qty / base_qty
        lines = []
        for line in bom["lines"]:
            qty_per_base = to_float(line.get("qty_per_base"))
            loss_percent = to_float(line.get("loss_percent"))
            base_required_qty = qty_per_base * factor
            loss_qty = base_required_qty * loss_percent / 100
            required_qty = base_required_qty + loss_qty
            min_qty = apply_tolerance(required_qty, line.get("min_tolerance_pct"), -1)
            max_qty = apply_tolerance(required_qty, line.get("max_tolerance_pct"), 1)
            lines.append(
                {
                    "bom_line_id": line.get("bom_line_id"),
                    "line_no": line.get("line_no"),
                    "component_type": line.get("component_type"),
                    "component_articul": line.get("component_articul"),
                    "component_name": line.get("component_name"),
                    "unit_code": line.get("unit_code") or bom.get("base_unit_code"),
                    "qty_per_base": qty_per_base,
                    "base_required_qty": round(base_required_qty, 6),
                    "loss_percent": loss_percent,
                    "loss_qty": round(loss_qty, 6),
                    "required_qty": round(required_qty, 6),
                    "min_qty": min_qty,
                    "max_qty": max_qty,
                    "is_required": line.get("is_required"),
                    "substitution_group": line.get("substitution_group"),
                    "replacement_ratio": line.get("replacement_ratio"),
                }
            )

        return {
            "bom_id": bom_id,
            "bom_code": bom.get("bom_code"),
            "target_articul": bom.get("target_articul"),
            "planned_qty": planned_qty,
            "planned_unit_code": request.unit_code or bom.get("base_unit_code"),
            "base_qty": base_qty,
            "base_unit_code": bom.get("base_unit_code"),
            "factor": round(factor, 6),
            "lines": lines,
        }


def clamp_limit(value: int) -> int:
    return min(max(value, 1), 500)


def to_float(value: Any) -> float:
    if value is None:
        return 0.0
    return float(value)


def apply_tolerance(value: float, pct: Any, sign: int) -> float | None:
    if pct is None:
        return None
    return round(value * (1 + sign * to_float(pct) / 100), 6)


def _model_dict(model) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
