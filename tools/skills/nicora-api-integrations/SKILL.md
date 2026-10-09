---
name: nicora-api-integrations
description: Implement NICORA FastAPI commands, ERP XML exchange, background jobs and equipment adapters. Use for API boundaries, rights, idempotency and durable inbox/outbox delivery.
---

# NICORA API and integrations

Read wiki/index.md, wiki/architecture/nikora_technology_stack_20261007.md, the relevant NSxx card and process. Reuse api/wms_api_server modules after inspecting middleware, gateway and worker callers.

- Enforce rights and state server-side. Keep business effect and required outgoing event atomic; do not hold a transaction while waiting for ERP, solver, camera or printer.
- Separate diagnostic API audit from atomic business journal. Preserve correlation and replay restrictions; admin/replay calls must not recursively replay themselves.
- Define idempotency scope, payload conflicts, durable result and reconciliation after timeout following commit. Retries must not duplicate reserves, picking, loading or ERP effects.
- Derive XML mappings, identifiers, versions, states and rejection cases from approved ERP contracts. Mock outbox behavior is not evidence of ERP acceptance.
- Jobs need exclusive claims, bounded ownership, crash recovery, delayed retries and visible terminal failures. Verify two workers competing for one job; do not assume exactly-once delivery.
- Inspect synchronous Oracle/audit work inside async middleware/routes. Avoid event-loop blocking and bound total connection budget across processes using measurements.
- Device contracts identify device, timestamp, units/tare, stable-reading or print result, correlation and failure behavior. Simulator and physical hardware acceptance are separate evidence.
- Keep regulatory writes behind RRL_PRODUCTION_API or RRL_REGULATORY_API. Preserve external IDs, required certificate/signature metadata and retry diagnostics.

Verify real API/Oracle effects, denials, duplicate/malformed XML, unavailable devices and worker failure. Apply nicora-acceptance for evidence and slow-SQL decisions.
