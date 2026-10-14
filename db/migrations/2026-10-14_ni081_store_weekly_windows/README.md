# NI08.1: weekly store windows — prepared, NOT APPLIED

Migration `2026-10-14-ni081-store-weekly-windows`. Owner: Codex store_schedule; root owns application and acceptance.

Dependencies: `2026-10-14-1490-ni051-store-profile` and `2026-10-14-ni022-vehicle-outer-dimensions` must be installed first. Schema uses actual `MAX_VEHICLE_OUTER_HEIGHT_MM` / `MAX_VEHICLE_OUTER_LENGTH_MM` fields in Claude's prepared DDL.

## Behavior

- `RRL_STORE_WINDOW_RULES` is a read-only native helper. It supplies canonical profile material and resolves a stop window. No Python scheduling rules, stock mutation, commit, or new lock.
- Each complete ST materialized interval wins over weekly defaults. A partial, reversed or empty interval is an error. Complete members at one stop intersect. Members missing both endpoints use the shared destination weekly profile, intersected with any complete members.
- Weekly availability must contain the whole unload duration in one interval. Lunch breaks are preserved. Exact completion at closing is allowed. Missing weekday returns `STORE_CLOSED`, even for soft `TW_STRICT`. No fitting interval returns `STORE_NO_FEASIBLE_INTERVAL`.
- **Explicit horizon: one arrival-local service day, at most eight intervals.** No automatic overnight/week-ahead rescheduling. A dispatcher must adjust the route date explicitly. Materialized soft/hard lateness behavior remains the existing behavior.
- Profile timezone is explicit. Oracle timezone offsets are sampled across +/-48 hours; each local endpoint must round-trip to exactly one UTC instant. DST fold/gap is rejected rather than guessed. Planning timezone retains the existing UTC / Europe/Moscow / Asia/Tbilisi restriction. No session timezone dependence and no `ALTER SESSION`.
- The existing route calculator is still used by both preview and final approval. Existing CONFIG -> TT -> sorted address/matrix locking and immutable replay are untouched.
- Snapshot contract V7 adds sorted destination profile identity, explicit absence, version, mode, timezone, canonical window rows, store outer limits; also fleet identity cardinality plus current `describe_profile` (version/base hash/state/outer dimensions). Edits therefore invalidate prior source hashes even if a materialized ST window currently wins. Absence and duplicate vehicle identity are explicit.

## Installation/recovery

Fresh read-only checkpoint of both package specs/bodies and SHA256 manifest is included. `rollback.sql` restores original bodies then drops the new helper; no business data is deleted. Run `python scripts/store_weekly_preflight.py` immediately before applying: it refuses source drift. Do not rebuild checkpoints after installation.

Root applies `apply.sql` through existing OracleApply. It installs helper + route + snapshot, verifies compilation, runs ten no-DML native resolver cases, and only then writes the migration ledger. DDL is not transactional: on failure root uses the saved rollback, rather than claiming atomic installation. Root must inspect dependencies and apply status first.

## Evidence and remaining acceptance

- Read-only target confirmed RABAEV/orcl. Preflight PASS.
- Live Oracle read-only timezone expression probes: Moscow regular time -> one UTC match; UTC -> one; Berlin 2026-10-25 02:30 -> two (fold); Berlin 2026-03-29 02:30 -> zero (gap). This verifies the conversion expression, **not package compilation**.
- `selftest.sql`: opening wait, lunch gap, exact end, closed day, insufficient interval, missing profile, partial ST, materialized precedence, reversed ST, mixed ST/default intersection. Prepared, not executed before installation.
- Still required from root: package compile/selftest, one real preview/final hash invalidation case under CONFIG, common quality gate, slow-SQL review. No real route or profile was mutated by this task.
- Performance decision: bounded indexed profile/window lookups, max200 addresses/56 rows each; same-day resolution max8 intervals and fixed97 timezone samples/endpoint. Root must capture the meaningful route case latency; optimize timezone conversion if it dominates. No speculative index added (profile PK and window composite PK already cover access).

Timezone implementation refinement: offset candidates are now cached per explicit region/local day, max256 session keys; no editable configuration is cached. One set-based97-row SQL per cold key, then exact endpoint roundtrip. Native read-only 200-stop/3400-conversion probe improved3150.916ms→795.040ms; fold/gap refusal retained. See handoff report and `conversion_native.json`; full route performance remains root acceptance.
