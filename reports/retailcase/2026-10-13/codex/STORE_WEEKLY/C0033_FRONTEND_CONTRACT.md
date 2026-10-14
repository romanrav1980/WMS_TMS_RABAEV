# C0033 frontend contract: native route windows

Source checked 2026-10-14: existing `app/modules/transport/api/preflight_routes.py`, `infrastructure/delivery_window_preview.py`, prepared native weekly migration. No new endpoint is needed. All endpoints below require existing `transport_dispatch_edit`.

## Read endpoints

1. `GET /api/transport/preflight/trips/{trip_id}/time-context`

Response: `{trip_id, source_hash, version, approval_status, operational_admission:false, source, last_approval?}`. Approval status is `NO_APPROVAL`, `APPROVED`, `SOURCE_CHANGED` or `LEGACY_SOURCE_CONTRACT`. `version` is the expected approval version, **not** store profile version.

After native V7 installation, `source.source_contract_version=7`; `source.store_window_profiles[]` contains `{address, profile_absent, profile_version?, mode, time_zone?, windows:[{weekday,from_minute,to_minute}], max_vehicle_outer_height_mm?,max_vehicle_outer_length_mm?}`. Absence is explicit; do not display absent/default as open24h. `source.vehicle_profile_material` contains matching vehicle cardinality and current fleet `describe_profile` result (or ABSENT/AMBIGUOUS state). These fields belong to the context snapshot, not each schedule stop.

2. `GET /api/transport/preflight/trips/{trip_id}/delivery-windows?time_zone=Europe%2FMoscow`

`time_zone` required: UTC / Europe/Moscow / Asia/Tbilisi. Optional `depot_address` defaults empty (configured warehouse base), `max_age_hours` defaults24. Do not invent another depot or freshness value; native preview validates current policy. Read-only, stock unchanged.

Response **is the schedule at the top level**:

```json
{
  "trip_id": 33641,
  "source_hash": "64 lowercase hex characters",
  "consistent_snapshot": true,
  "status": "NO_EARLIEST_WINDOW_VIOLATION or INSUFFICIENT_EVIDENCE",
  "time_zone": "Europe/Moscow",
  "stops": [{
    "address": "actual RRL_ADDR.ADDR",
    "st_numbers": ["..."],
    "window_source": "ST_MATERIALIZED or STORE_WEEKLY or ST_AND_STORE_WEEKLY",
    "window_from": "ISO timestamp with explicit offset, or null",
    "window_to": "ISO timestamp with explicit offset, or null",
    "arrival_at": "ISO timestamp with explicit offset, or null",
    "service_start_at": "ISO timestamp with explicit offset, or null",
    "service_finish_at": "ISO timestamp with explicit offset, or null",
    "wait_min": "decimal string or null",
    "late_min": "decimal string or null",
    "unload_norm_min": "decimal string or null",
    "window_strict": 0,
    "issues": ["error/warning code"]
  }],
  "segments": [{"code":"DRIVE/REST/WAIT/UNLOAD/etc", "start_at":"ISO", "finish_at":"ISO", "duration_min":"decimal string, may be absent for preserved stages", "address":"may be absent"}],
  "issues": [{"code":"...", "address":"... or null"}],
  "warnings": [{"code":"...", "address":"..."}],
  "operational_admission": false,
  "legal_compliance_verified": false,
  "read_only": true,
  "stock_changed": false
}
```

`window_source` is additive after installation; old servers may omit it. Null times must display unavailable, not epoch1970. For profile/version/timezone alongside a stop, join context profile by exact `address` **only when context.source_hash equals preview.source_hash**. If hashes differ, reload context and preview; never attach a newer card to an older route silently.

## Errors to render

Existing errors remain. New blocking codes: `STORE_CLOSED` (closed on arrival-local day), `STORE_NO_FEASIBLE_INTERVAL` (whole unloading does not fit one available interval), `DELIVERY_WINDOW_UNCONFIGURED`, `DELIVERY_WINDOW_PARTIAL`, `DELIVERY_WINDOW_REVERSED_OR_EMPTY`, `DELIVERY_WINDOW_DISJOINT`, `STORE_TIMEZONE_REQUIRED`, `STORE_TIMEZONE_OR_WINDOW_INVALID`, `STORE_WINDOW_DST_AMBIGUOUS_OR_NONEXISTENT`, `STORE_WEEKLY_INTERVAL_INVALID`, `DELIVERY_MEMBERS_MISSING`.

Weekly errors block regardless of TW_STRICT: the UI must not offer a client-side override. Materialized ST soft lateness remains `DELIVERY_SOFT_WINDOW_MISSED` warning; hard lateness is `DELIVERY_HARD_WINDOW_MISSED`. One arrival-local service day is the current explicit horizon: no automatic overnight move. Show the operator that the route date/configuration needs correction.

## Existing approval command

`POST /api/transport/preflight/time-approvals` body:

```json
{"operation_id":"stable-command-id", "trip_id":33641, "expected_version":0, "source_hash":"context/preview shared hash", "time_zone":"Europe/Moscow", "reason":"At least 8 characters", "approval_phase":"BEFORE_LOADING"}
```

`approval_phase` optional, allowed BEFORE_LOADING / AFTER_LOADING_REVIEW. Keep existing workflow and explicit approval action; viewing this panel must not approve anything. Retry the identical operation_id/body after an uncertain response. Changed source/version requires refresh and new command, not automatic acceptance. Successful approval result contains the native schedule at `result.route_schedule`, unlike the top-level preview response. Source V7 is in `result.source_contract_version` and `result.plan_source`. Approval does not mean legal compliance or physical warehouse admission.
