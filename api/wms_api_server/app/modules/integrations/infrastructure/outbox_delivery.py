"""Short native lease transactions; provider calls remain outside Oracle locks."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_regulatory import RegulatoryAdapter

class OutboxDelivery:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def claim(self, worker: str, target: str | None, seconds: int = 300) -> dict[str, Any] | None:
        with self.gateway.transaction("Outbox claim with generation and aware lease") as cur:
            cur.arraysize = 1
            cur.prefetchrows = 0
            result = cur.var(oracledb.DB_TYPE_CLOB)
            cur.callproc("RRL_OUTBOX_DELIVERY_API.claim_next", [worker, target, seconds, result])
            value = result.getvalue()
            return read_oracle_json(value) if value is not None else None

    def event(self, event_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all("""select EVENT_OUTBOX_ID,EVENT_TYPE,AGGREGATE_TYPE,AGGREGATE_ID,
            TARGET_SYSTEM,CORRELATION_ID,IDEMPOTENCY_KEY,to_clob(PAYLOAD_JSON) PAYLOAD_JSON,
            STATUS,TRY_COUNT,MAX_TRY_COUNT,CLAIM_VERSION
            from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=:id""", {"id": event_id})
        return rows[0] if rows else {}

    def begin(self, claim: dict[str, Any], event: dict[str, Any], adapter: RegulatoryAdapter) -> int:
        with self.gateway.transaction("Outbox durable attempt before provider call") as cur:
            request = cur.var(oracledb.DB_TYPE_NUMBER)
            payload = cur.var(oracledb.DB_TYPE_CLOB)
            payload.setvalue(0, event["payload_json"])
            cur.callproc("RRL_OUTBOX_DELIVERY_API.begin_attempt", [
                claim["event_outbox_id"], claim["claim_version"], claim["worker_id"],
                str(event.get("target_system") or "INTERNAL").upper(), event["event_type"],
                f'{event.get("aggregate_type")}:{event.get("aggregate_id")}',
                adapter.cert_alias, adapter.cert_thumbprint, adapter.signature_status, payload, request])
            return int(request.getvalue())

    def finish(self, claim: dict[str, Any], request_id: int, body: dict[str, Any]) -> dict[str, Any]:
        serialized = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        with self.gateway.transaction("Outbox response and event finalization atomically") as cur:
            payload = cur.var(oracledb.DB_TYPE_CLOB)
            payload.setvalue(0, serialized)
            result = cur.var(oracledb.DB_TYPE_CLOB)
            cur.callproc("RRL_OUTBOX_DELIVERY_API.finish_attempt", [
                claim["event_outbox_id"], claim["claim_version"], claim["worker_id"], request_id, payload, result])
            return read_oracle_json(result.getvalue())

    def retry(self, event_id: int, actor: str, reason: str | None) -> None:
        with self.gateway.transaction("Outbox manual retry with current actor and durable reason") as cur:
            cur.callproc("RRL_OUTBOX_DELIVERY_API.manual_retry", [event_id, actor, reason])
