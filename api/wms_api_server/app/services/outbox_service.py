from typing import Any

from ..oracle_gateway import OracleGateway
from .adapters.mock import MockRegulatoryAdapter


class OutboxService:
    def __init__(
        self,
        gateway: OracleGateway | None = None,
        adapter: MockRegulatoryAdapter | None = None,
    ) -> None:
        self.gateway = gateway or OracleGateway()
        self.adapter = adapter or MockRegulatoryAdapter()

    def process_next(self, worker_id: str, target_system: str | None = None) -> dict[str, Any] | None:
        event_id = self.lock_next(worker_id=worker_id, target_system=target_system)
        if event_id is None:
            return None
        event = self.get_event(event_id)
        if not event:
            return {"event_outbox_id": event_id, "status": "missing"}

        request_id: int | None = None
        try:
            system_code = str(event.get("target_system") or "INTERNAL").upper()
            request_id = self.add_adapter_request(event, system_code=system_code)
            response = self.adapter.send(event)
            self.update_adapter_request(
                adapter_request_id=request_id,
                response_json=response.response_json,
                external_request_id=response.external_request_id,
                external_document_id=response.external_document_id,
                external_status=response.external_status,
                http_status=response.http_status,
                status=response.status,
            )
            self.mark_done(event_id)
            return {
                "event_outbox_id": event_id,
                "adapter_request_id": request_id,
                "status": "DONE",
                "external_status": response.external_status,
            }
        except Exception as exc:
            error_text = str(exc)
            if request_id is not None:
                self.update_adapter_request(
                    adapter_request_id=request_id,
                    status="ERROR",
                    error_code=exc.__class__.__name__,
                    error_text=error_text,
                )
            self.mark_error(event_id, error_text=error_text)
            return {
                "event_outbox_id": event_id,
                "adapter_request_id": request_id,
                "status": "ERROR",
                "error": error_text,
            }

    def lock_next(self, worker_id: str, target_system: str | None = None) -> int | None:
        return self.gateway.call_optional_number_plsql(
            """
            begin
              :result := RRL_TRACEABILITY_API.lock_next_outbox(
                p_worker_id => :worker_id,
                p_target_system => :target_system
              );
            end;
            """,
            {"worker_id": worker_id, "target_system": target_system.upper() if target_system else None},
        )

    def get_event(self, event_outbox_id: int) -> dict[str, Any]:
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
                   MAX_TRY_COUNT
              from RRL_EVENT_OUTBOX
             where EVENT_OUTBOX_ID = :event_outbox_id
            """,
            {"event_outbox_id": event_outbox_id},
        )
        return rows[0] if rows else {}

    def add_adapter_request(self, event: dict[str, Any], system_code: str) -> int:
        business_key = f"{event.get('aggregate_type')}:{event.get('aggregate_id')}"
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_TRACEABILITY_API.add_adapter_request(
                p_system_code => :system_code,
                p_request_kind => :request_kind,
                p_event_outbox_id => :event_outbox_id,
                p_business_key => :business_key,
                p_signature_status => :signature_status,
                p_request_json => :request_json,
                p_status => :status,
                p_try_no => :try_no
              );
            end;
            """,
            {
                "system_code": system_code,
                "request_kind": event.get("event_type"),
                "event_outbox_id": event.get("event_outbox_id"),
                "business_key": business_key,
                "signature_status": "MOCK_NOT_SIGNED",
                "request_json": event.get("payload_json"),
                "status": "STARTED",
                "try_no": int(event.get("try_count") or 0) + 1,
            },
        )

    def update_adapter_request(
        self,
        adapter_request_id: int,
        response_json: str | None = None,
        external_request_id: str | None = None,
        external_document_id: str | None = None,
        external_status: str | None = None,
        http_status: int | None = None,
        status: str = "DONE",
        error_code: str | None = None,
        error_text: str | None = None,
    ) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_TRACEABILITY_API.update_adapter_request(
                p_adapter_request_id => :adapter_request_id,
                p_response_json => :response_json,
                p_external_request_id => :external_request_id,
                p_external_document_id => :external_document_id,
                p_external_status => :external_status,
                p_http_status => :http_status,
                p_status => :status,
                p_error_code => :error_code,
                p_error_text => :error_text
              );
            end;
            """,
            {
                "adapter_request_id": adapter_request_id,
                "response_json": response_json,
                "external_request_id": external_request_id,
                "external_document_id": external_document_id,
                "external_status": external_status,
                "http_status": http_status,
                "status": status,
                "error_code": error_code,
                "error_text": error_text,
            },
        )

    def mark_done(self, event_outbox_id: int) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_TRACEABILITY_API.mark_outbox_done(
                p_event_outbox_id => :event_outbox_id,
                p_status => 'DONE'
              );
            end;
            """,
            {"event_outbox_id": event_outbox_id},
        )

    def mark_error(self, event_outbox_id: int, error_text: str) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_TRACEABILITY_API.mark_outbox_error(
                p_event_outbox_id => :event_outbox_id,
                p_error_text => :error_text,
                p_retry_delay_minutes => 5,
                p_dead_letter => 0
              );
            end;
            """,
            {"event_outbox_id": event_outbox_id, "error_text": error_text},
        )
