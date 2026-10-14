"""Compatibility worker facade over the fenced native delivery coordinator."""
from typing import Any
from ..oracle_gateway import OracleGateway
from ..modules.integrations.public import (
    RegulatoryAdapter, build_regulatory_adapter, regulatory_delivery_decision, OutboxDelivery, OutboxResponseJournal)

class OutboxService:
    def __init__(self, gateway: OracleGateway | None = None, adapter: RegulatoryAdapter | None = None,
                 journal: OutboxResponseJournal | None = None) -> None:
        self.gateway = gateway or OracleGateway()
        self.adapter = adapter if adapter is not None else build_regulatory_adapter()
        self.delivery = OutboxDelivery(self.gateway)
        self.journal = journal or OutboxResponseJournal()

    def process_next(self, worker_id: str, target_system: str | None = None) -> dict[str, Any] | None:
        recovered = self.journal.recover_one(self.delivery, target_system)
        if recovered is not None:
            return recovered
        if not self.adapter.configured:
            return {"status": "NOT_CONFIGURED", "target_system": target_system, "event_outbox_id": None,
                    "real_external_ack": False, "pending_events_preserved": True}
        self.journal.ready()
        claim = self.delivery.claim(worker_id, target_system.upper() if target_system else None)
        if claim is None:
            return None
        event = self.delivery.event(claim["event_outbox_id"])
        # An unconfirmed claim/begin commit is recovered through the lease, never blindly resent.
        request_id = self.delivery.begin(claim, event, self.adapter)
        try:
            response = self.adapter.send(event)
            decision = regulatory_delivery_decision(response)
            body = {"status": decision.request_status, "error_code": decision.error_code,
                    "error_text": decision.error_text, "response_json": response.response_json,
                    "external_request_id": response.external_request_id,
                    "external_document_id": response.external_document_id,
                    "external_status": response.external_status, "http_status": response.http_status}
            real_ack = decision.delivered and response.real_external_ack is True and not self.adapter.simulated
        except Exception as exc:
            body = {"status": "ERROR", "error_code": type(exc).__name__, "error_text": str(exc)[:4000]}
            real_ack = False
        key = self.journal.save(claim, request_id, str(event.get("target_system") or "INTERNAL"),
                                body, self.adapter.simulated, real_ack)
        saved = self.journal.finalize(key, self.delivery)
        if saved is None:
            return {"event_outbox_id": claim["event_outbox_id"], "adapter_request_id": request_id,
                    "status": "RESPONSE_PENDING", "real_external_ack": False}
        return {**saved, "response_recovered": False}
