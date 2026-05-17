from typing import Any

from ..oracle_gateway import OracleGateway
from ..schemas import (
    StockReservationCreateRequest,
    StockReservationPromoteRequest,
    StockReservationStatusRequest,
)


ACTIVE_HARD_STATUSES = {"ACTIVE", "ALLOCATED", "PICKING"}
VALID_KINDS = {"SOFT", "HARD"}
VALID_SCOPES = {"PALLET", "QTY"}
VALID_DOMAINS = {"MES_RAW", "PICKING", "WAVE", "SHIPMENT"}
VALID_STATUSES = {"ACTIVE", "ALLOCATED", "PICKING", "CONSUMED", "RELEASED", "CANCELLED", "EXPIRED"}


class StockReservationService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def list_reservations(
        self,
        reservation_kind: str | None = None,
        reservation_domain: str | None = None,
        status: str | None = None,
        source_doc_type: str | None = None,
        source_doc_id: int | None = None,
        articul: str | None = None,
        ware_id: int | None = None,
        cell: str | None = None,
        uid_pallet: str | None = None,
        batch_id: str | None = None,
        production_order_id: int | None = None,
        pick_plan_id: int | None = None,
        pick_wave_id: int | None = None,
        only_active: int | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {"limit": min(max(limit, 1), 1000)}
        if reservation_kind:
            conditions.append("r.RESERVATION_KIND = :reservation_kind")
            params["reservation_kind"] = reservation_kind.upper()
        if reservation_domain:
            conditions.append("r.RESERVATION_DOMAIN = :reservation_domain")
            params["reservation_domain"] = reservation_domain.upper()
        if status:
            conditions.append("r.STATUS = :status")
            params["status"] = status.upper()
        if source_doc_type:
            conditions.append("r.SOURCE_DOC_TYPE = :source_doc_type")
            params["source_doc_type"] = source_doc_type.upper()
        if source_doc_id is not None:
            conditions.append("r.SOURCE_DOC_ID = :source_doc_id")
            params["source_doc_id"] = source_doc_id
        if articul:
            conditions.append("upper(r.ARTICUL) like :articul")
            params["articul"] = f"%{articul.upper()}%"
        if ware_id is not None:
            conditions.append("r.WARE_ID = :ware_id")
            params["ware_id"] = ware_id
        if cell:
            conditions.append("upper(r.CELL) like :cell")
            params["cell"] = f"%{cell.upper()}%"
        if uid_pallet:
            conditions.append("upper(r.UID_PALLET) = :uid_pallet")
            params["uid_pallet"] = uid_pallet.upper()
        if batch_id:
            conditions.append("upper(r.BATCH_ID) = :batch_id")
            params["batch_id"] = batch_id.upper()
        if production_order_id is not None:
            conditions.append("r.PRODUCTION_ORDER_ID = :production_order_id")
            params["production_order_id"] = production_order_id
        if pick_plan_id is not None:
            conditions.append("r.PICK_PLAN_ID = :pick_plan_id")
            params["pick_plan_id"] = pick_plan_id
        if pick_wave_id is not None:
            conditions.append("r.PICK_WAVE_ID = :pick_wave_id")
            params["pick_wave_id"] = pick_wave_id
        if only_active is not None and int(only_active) == 1:
            conditions.append("r.STATUS in ('ACTIVE', 'ALLOCATED', 'PICKING')")
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select r.*
                  from RRL_STOCK_RESERVATION r
                  {where_sql}
                 order by r.RESERVATION_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def get_reservation(self, reservation_id: int) -> dict[str, Any] | None:
        rows = self.gateway.fetch_all(
            """
            select *
              from RRL_STOCK_RESERVATION
             where RESERVATION_ID = :reservation_id
            """,
            {"reservation_id": reservation_id},
        )
        return rows[0] if rows else None

    def create_reservation(self, request: StockReservationCreateRequest) -> int:
        data = _model_dict(request)
        self._validate_kind_scope_status(data)
        self._validate_physical_fields(data)
        reservation_id = self._next_id()
        self.gateway.execute(
            """
            insert into RRL_STOCK_RESERVATION (
              RESERVATION_ID, RESERVATION_KIND, RESERVATION_SCOPE, RESERVATION_DOMAIN,
              SOURCE_DOC_TYPE, SOURCE_DOC_ID, SOURCE_LINE_ID, TASK_ID,
              CUSTOMER_ID, CUSTOMER_ORDER_ID, PRODUCTION_ORDER_ID,
              PICK_PLAN_ID, PICK_PLAN_LINE_ID, PICK_WAVE_ID, PICK_WAVE_LINE_ID,
              ARTICUL, QTY, UNIT_CODE, WARE_ID, CELL, BATCH_ID, PROD_BATCH_ID,
              UID_PALLET, SSCC, STATUS, PRIORITY, CREATED_BY
            ) values (
              :reservation_id, :reservation_kind, :reservation_scope, :reservation_domain,
              :source_doc_type, :source_doc_id, :source_line_id, :task_id,
              :customer_id, :customer_order_id, :production_order_id,
              :pick_plan_id, :pick_plan_line_id, :pick_wave_id, :pick_wave_line_id,
              :articul, :qty, :unit_code, :ware_id, :cell, :batch_id, :prod_batch_id,
              :uid_pallet, :sscc, :status, :priority, :created_by
            )
            """,
            {
                **self._normalized_params(data),
                "reservation_id": reservation_id,
            },
        )
        return reservation_id

    def promote_to_hard(self, reservation_id: int, request: StockReservationPromoteRequest) -> None:
        existing = self.get_reservation(reservation_id)
        if existing is None:
            raise LookupError(f"Reservation not found: {reservation_id}")
        data = _model_dict(request)
        merged = {
            "reservation_kind": "HARD",
            "reservation_scope": data.get("reservation_scope") or "PALLET",
            "ware_id": data.get("ware_id"),
            "cell": data.get("cell"),
            "batch_id": data.get("batch_id"),
            "prod_batch_id": data.get("prod_batch_id"),
            "uid_pallet": data.get("uid_pallet"),
            "sscc": data.get("sscc"),
            "qty": data.get("qty") if data.get("qty") is not None else existing.get("qty"),
        }
        self._validate_kind_scope_status({"reservation_kind": "HARD", "reservation_scope": merged["reservation_scope"], "status": "ACTIVE"})
        self._validate_physical_fields(merged)
        self.gateway.execute(
            """
            update RRL_STOCK_RESERVATION
               set RESERVATION_KIND = 'HARD',
                   RESERVATION_SCOPE = :reservation_scope,
                   WARE_ID = :ware_id,
                   CELL = :cell,
                   BATCH_ID = :batch_id,
                   PROD_BATCH_ID = :prod_batch_id,
                   UID_PALLET = :uid_pallet,
                   SSCC = :sscc,
                   QTY = nvl(:qty, QTY),
                   STATUS = 'ACTIVE',
                   LOCK_OWNER = null,
                   LOCKED_AT = null,
                   LAST_ERROR = null
             where RESERVATION_ID = :reservation_id
            """,
            {
                "reservation_id": reservation_id,
                "reservation_scope": str(merged["reservation_scope"]).upper(),
                "ware_id": merged["ware_id"],
                "cell": _upper_or_none(merged["cell"]),
                "batch_id": _upper_or_none(merged["batch_id"]),
                "prod_batch_id": merged["prod_batch_id"],
                "uid_pallet": _upper_or_none(merged["uid_pallet"]),
                "sscc": _upper_or_none(merged["sscc"]),
                "qty": merged["qty"],
            },
        )

    def release_reservation(self, reservation_id: int, request: StockReservationStatusRequest) -> None:
        self._set_status(
            reservation_id=reservation_id,
            status="RELEASED",
            actor=request.updated_by,
            reason=request.reason,
            timestamp_column="RELEASED_AT",
            actor_column="RELEASED_BY",
        )

    def consume_reservation(self, reservation_id: int, request: StockReservationStatusRequest) -> None:
        self._set_status(
            reservation_id=reservation_id,
            status="CONSUMED",
            actor=request.updated_by,
            reason=request.reason,
            timestamp_column="CONSUMED_AT",
            actor_column="CONSUMED_BY",
        )

    def cancel_reservation(self, reservation_id: int, request: StockReservationStatusRequest) -> None:
        self._set_status(
            reservation_id=reservation_id,
            status="CANCELLED",
            actor=request.updated_by,
            reason=request.reason,
            timestamp_column="RELEASED_AT",
            actor_column="RELEASED_BY",
        )

    def _set_status(
        self,
        reservation_id: int,
        status: str,
        actor: str | None,
        reason: str | None,
        timestamp_column: str,
        actor_column: str,
    ) -> None:
        existing = self.get_reservation(reservation_id)
        if existing is None:
            raise LookupError(f"Reservation not found: {reservation_id}")
        self.gateway.execute(
            f"""
            update RRL_STOCK_RESERVATION
               set STATUS = :status,
                   {timestamp_column} = systimestamp,
                   {actor_column} = :actor,
                   RELEASE_REASON = nvl(:reason, RELEASE_REASON)
             where RESERVATION_ID = :reservation_id
            """,
            {
                "reservation_id": reservation_id,
                "status": status,
                "actor": actor,
                "reason": reason,
            },
        )

    def _next_id(self) -> int:
        rows = self.gateway.fetch_all(
            "select RRL_STOCK_RESERVATION_SQ.nextval RESERVATION_ID from dual"
        )
        return int(rows[0]["reservation_id"])

    def _validate_kind_scope_status(self, data: dict[str, Any]) -> None:
        kind = str(data.get("reservation_kind") or "").upper()
        scope = str(data.get("reservation_scope") or "QTY").upper()
        status = str(data.get("status") or "ACTIVE").upper()
        domain = data.get("reservation_domain")
        if kind not in VALID_KINDS:
            raise ValueError("reservation_kind must be SOFT or HARD")
        if scope not in VALID_SCOPES:
            raise ValueError("reservation_scope must be PALLET or QTY")
        if status not in VALID_STATUSES:
            raise ValueError("Invalid reservation status")
        if domain is not None and str(domain).upper() not in VALID_DOMAINS:
            raise ValueError("Invalid reservation_domain")

    def _validate_physical_fields(self, data: dict[str, Any]) -> None:
        kind = str(data.get("reservation_kind") or "").upper()
        if kind == "SOFT":
            physical_values = [
                data.get("ware_id"),
                data.get("cell"),
                data.get("batch_id"),
                data.get("prod_batch_id"),
                data.get("uid_pallet"),
                data.get("sscc"),
            ]
            if any(value not in (None, "") for value in physical_values):
                raise ValueError("SOFT reservation must not contain warehouse/cell/batch/pallet/SSCC fields")
        if kind == "HARD":
            if data.get("ware_id") is None or not data.get("cell"):
                raise ValueError("HARD reservation requires ware_id and cell")
            if not (data.get("uid_pallet") or data.get("batch_id") or data.get("prod_batch_id")):
                raise ValueError("HARD reservation requires uid_pallet or batch/prod_batch identifier")

    def _normalized_params(self, data: dict[str, Any]) -> dict[str, Any]:
        return {
            **data,
            "reservation_kind": str(data.get("reservation_kind") or "SOFT").upper(),
            "reservation_scope": str(data.get("reservation_scope") or "QTY").upper(),
            "reservation_domain": str(data.get("reservation_domain") or "").upper(),
            "source_doc_type": str(data.get("source_doc_type") or "").upper(),
            "articul": str(data.get("articul") or "").upper(),
            "unit_code": _upper_or_none(data.get("unit_code")),
            "cell": _upper_or_none(data.get("cell")),
            "batch_id": _upper_or_none(data.get("batch_id")),
            "uid_pallet": _upper_or_none(data.get("uid_pallet")),
            "sscc": _upper_or_none(data.get("sscc")),
            "status": str(data.get("status") or "ACTIVE").upper(),
        }


def _upper_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text.upper() if text else None


def _model_dict(model) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
