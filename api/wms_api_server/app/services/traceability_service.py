from ..modules.integrations.public import adapter_request_evidence
from typing import Any

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway


class TraceabilityService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def list_edges(
        self,
        entity_type: str,
        entity_id: str,
        direction: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        normalized_direction = direction.lower()
        params = {
            "entity_type": normalize_entity_type(entity_type),
            "entity_id": entity_id,
            "limit": clamp_limit(limit),
        }
        if normalized_direction == "forward":
            predicate = "e.FROM_ENTITY_TYPE = :entity_type and e.FROM_ENTITY_ID = :entity_id"
        elif normalized_direction == "backward":
            predicate = "e.TO_ENTITY_TYPE = :entity_type and e.TO_ENTITY_ID = :entity_id"
        else:
            raise ValueError(f"Unsupported trace direction: {direction}")

        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select e.TRACE_EDGE_ID,
                       e.FROM_ENTITY_TYPE,
                       e.FROM_ENTITY_ID,
                       e.TO_ENTITY_TYPE,
                       e.TO_ENTITY_ID,
                       e.EDGE_TYPE,
                       e.QUANTITY,
                       e.UNIT_CODE,
                       e.TRACE_EVENT_ID,
                       t.EVENT_TYPE,
                       t.CORRELATION_ID,
                       e.CREATED_AT,
                       e.CREATED_BY
                  from RRL_TRACE_EDGE e
                  left join RRL_TRACE_EVENT t
                    on t.TRACE_EVENT_ID = e.TRACE_EVENT_ID
                 where {predicate}
                 order by e.CREATED_AT desc, e.TRACE_EDGE_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def list_outbox(
        self,
        status: str | None = None,
        target_system: str | None = None,
        event_type: str | None = None,
        aggregate_type: str | None = None,
        aggregate_id: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {"limit": clamp_limit(limit)}
        if status:
            conditions.append("STATUS = :status")
            params["status"] = status.upper()
        if target_system:
            conditions.append("TARGET_SYSTEM = :target_system")
            params["target_system"] = target_system.upper()
        if event_type:
            conditions.append("EVENT_TYPE = :event_type")
            params["event_type"] = event_type.upper()
        if aggregate_type:
            conditions.append("AGGREGATE_TYPE = :aggregate_type")
            params["aggregate_type"] = aggregate_type.upper()
        if aggregate_id:
            conditions.append("AGGREGATE_ID = :aggregate_id")
            params["aggregate_id"] = aggregate_id
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select EVENT_OUTBOX_ID,
                       EVENT_TYPE,
                       AGGREGATE_TYPE,
                       AGGREGATE_ID,
                       TARGET_SYSTEM,
                       CORRELATION_ID,
                       IDEMPOTENCY_KEY,
                       STATUS,
                       TRY_COUNT,
                       MAX_TRY_COUNT,
                       NEXT_RETRY_AT,
                       LOCKED_BY,
                       LOCKED_AT,
                       CLAIM_VERSION,
                       to_char(LEASE_UNTIL at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')LEASE_UNTIL,
                       LAST_ERROR,
                       CREATED_AT,
                       SENT_AT,
                       FINISHED_AT,
                       CANCELLED_AT
                  from RRL_EVENT_OUTBOX
                  {where_sql}
                 order by CREATED_AT desc, EVENT_OUTBOX_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def get_outbox_event(self, event_outbox_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """
            select EVENT_OUTBOX_ID,
                   EVENT_TYPE,
                   AGGREGATE_TYPE,
                   AGGREGATE_ID,
                   TARGET_SYSTEM,
                   CORRELATION_ID,
                   IDEMPOTENCY_KEY,
                   PAYLOAD_JSON,
                   STATUS,
                   TRY_COUNT,
                   MAX_TRY_COUNT,
                   NEXT_RETRY_AT,
                   LOCKED_BY,
                   LOCKED_AT,
                   CLAIM_VERSION,
                   to_char(LEASE_UNTIL at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')LEASE_UNTIL,
                   LAST_ERROR,
                   CREATED_AT,
                   SENT_AT,
                   FINISHED_AT,
                   CANCELLED_AT
              from RRL_EVENT_OUTBOX
             where EVENT_OUTBOX_ID = :event_outbox_id
            """,
            {"event_outbox_id": event_outbox_id},
        )
        if not rows:
            return {}
        event = rows[0]
        event["adapter_requests"] = self.list_adapter_requests(event_outbox_id=event_outbox_id, limit=200)
        return event

    def retry_outbox_event(
        self,
        event_outbox_id: int,
        dry_run: bool = True,
        reason: str | None = None,
        actor: str | None = None,
    ) -> dict[str, Any]:
        event = self.get_outbox_event(event_outbox_id)
        if not event:
            raise HTTPException(status_code=404, detail="Outbox event not found.")
        if event.get("status") in {"DONE","EXPORTED","ACKNOWLEDGED"}:
            raise HTTPException(status_code=409, detail="DONE outbox events are not retried.")
        if dry_run:
            return {
                "dry_run": True,
                "event_outbox_id": event_outbox_id,
                "current_status": event.get("status"),
                "would_set_status": "PENDING",
            }

        from ..modules.integrations.public import OutboxDelivery
        if actor is None:
            raise HTTPException(status_code=403, detail="Current retry actor required")
        try:
            OutboxDelivery(self.gateway).retry(event_outbox_id, actor, reason)
        except Exception as exc:
            code = getattr(exc.args[0], "code", 0) if exc.args else 0
            if code in (20881,20882,20886):
                raise HTTPException(status_code=403 if code==20882 else 409, detail=str(exc).split("\n",1)[0]) from exc
            raise
        return {"dry_run": False,"event_outbox_id": event_outbox_id,"updated": 1,"status": "PENDING"}

    def list_adapter_requests(
        self,
        event_outbox_id: int | None = None,
        system_code: str | None = None,
        status: str | None = None,
        business_key: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {"limit": clamp_limit(limit)}
        if event_outbox_id is not None:
            conditions.append("EVENT_OUTBOX_ID = :event_outbox_id")
            params["event_outbox_id"] = event_outbox_id
        if system_code:
            conditions.append("SYSTEM_CODE = :system_code")
            params["system_code"] = system_code.upper()
        if status:
            conditions.append("STATUS = :status")
            params["status"] = status.upper()
        if business_key:
            conditions.append("BUSINESS_KEY = :business_key")
            params["business_key"] = business_key
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return [adapter_request_evidence(row) for row in self.gateway.fetch_all(
            f"""
            select *
              from (
                select ADAPTER_REQUEST_ID,
                       EVENT_OUTBOX_ID,
                       SYSTEM_CODE,
                       REQUEST_KIND,
                       BUSINESS_KEY,
                       CERT_ALIAS,
                       CERT_THUMBPRINT,
                       SIGNATURE_STATUS,
                       EXTERNAL_REQUEST_ID,
                       EXTERNAL_DOCUMENT_ID,
                       EXTERNAL_STATUS,
                       HTTP_STATUS,
                       STATUS,
                       ERROR_CODE,
                       ERROR_TEXT,
                       TRY_NO,
                       CREATED_AT,
                       SENT_AT,
                       FINISHED_AT
                  from RRL_ADAPTER_REQUEST_LOG
                  {where_sql}
                 order by CREATED_AT desc, ADAPTER_REQUEST_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )]

    def get_adapter_request(self, adapter_request_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """
            select ADAPTER_REQUEST_ID,
                   EVENT_OUTBOX_ID,
                   SYSTEM_CODE,
                   REQUEST_KIND,
                   BUSINESS_KEY,
                   CERT_ALIAS,
                   CERT_THUMBPRINT,
                   SIGNATURE_STATUS,
                   REQUEST_JSON,
                   RESPONSE_JSON,
                   EXTERNAL_REQUEST_ID,
                   EXTERNAL_DOCUMENT_ID,
                   EXTERNAL_STATUS,
                   HTTP_STATUS,
                   STATUS,
                   ERROR_CODE,
                   ERROR_TEXT,
                   TRY_NO,
                   CREATED_AT,
                   SENT_AT,
                   FINISHED_AT
              from RRL_ADAPTER_REQUEST_LOG
             where ADAPTER_REQUEST_ID = :adapter_request_id
            """,
            {"adapter_request_id": adapter_request_id},
        )
        return adapter_request_evidence(rows[0]) if rows else {}


def normalize_entity_type(value: str) -> str:
    normalized = value.strip().upper()
    if not normalized:
        raise HTTPException(status_code=400, detail="Entity type is required.")
    if len(normalized) > 50:
        raise HTTPException(status_code=400, detail="Entity type is too long.")
    return normalized


def clamp_limit(value: int) -> int:
    return min(max(value, 1), 500)
