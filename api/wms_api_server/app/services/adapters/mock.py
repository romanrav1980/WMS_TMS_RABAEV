from dataclasses import dataclass
from datetime import UTC, datetime
import json
from typing import Any


@dataclass(frozen=True)
class MockAdapterResponse:
    status: str
    external_status: str
    external_request_id: str
    external_document_id: str
    http_status: int
    response_json: str


class MockRegulatoryAdapter:
    def send(self, event: dict[str, Any]) -> MockAdapterResponse:
        system_code = str(event.get("target_system") or "INTERNAL").upper()
        event_id = event.get("event_outbox_id")
        event_type = event.get("event_type")
        external_request_id = f"MOCK-{system_code}-REQ-{event_id}"
        external_document_id = f"MOCK-{system_code}-DOC-{event_id}"
        payload = {
            "mock": True,
            "systemCode": system_code,
            "eventOutboxId": event_id,
            "eventType": event_type,
            "externalRequestId": external_request_id,
            "externalDocumentId": external_document_id,
            "acceptedAt": datetime.now(UTC).isoformat(),
        }
        return MockAdapterResponse(
            status="DONE",
            external_status="ACCEPTED",
            external_request_id=external_request_id,
            external_document_id=external_document_id,
            http_status=200,
            response_json=json.dumps(payload, ensure_ascii=False),
        )
