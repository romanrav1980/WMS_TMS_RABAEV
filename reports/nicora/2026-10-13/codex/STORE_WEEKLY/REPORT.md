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

## Timezone conversion refinement

Prepared helper now caches only Oracle timezone offset candidates per explicit zone/local day, bounded to256 keys/session (cleared on reaching bound). Editable store profiles/resolved windows are never cached. Each cold zone/day uses **one set-based SQL of97 rows**, followed by a small exact roundtrip check per endpoint. No session parameter changes, rights changes, DML or DDL.

Read-only native anonymous PL/SQL benchmark (17 conversions = arrival +16 endpoints for8 intervals; Moscow, one zone/day; includes cold cache per run):

| Stop equivalents | Original ms | Cached ms |
|---|---:|---:|
| 1 | 37.775 | 30.032 |
| 8 | 134.244 | 32.506 |
| 200 | 3150.916 | 795.040 |

`conversion_native.json` contains results; Berlin fold/gap rejection passed for both versions. This isolates conversion work, not full route/API latency or p95. A separate initial per-query/client-roundtrip measurement is retained in `conversion_before.json` and must not be compared as native execution. Decision: keep bounded offset cache; measure full meaningful route after root application. Store-window package remains **not applied** by this agent.

Frontend handoff: `C0033_FRONTEND_CONTRACT.md` gives existing endpoints, exact JSON placement, additive window source, source-hash pairing, error codes and approval command.

## Installed native acceptance on existing planning fixture

Root installed the dependency/profile and weekly packages, then this agent ran the bounded scenario on existing **TT33641 / ST641515 / NI081.SHOP.0b960a9257** only. B01/B02 untouched; no physical stock/movement/loading/departure command.

Results (`native_fixture.json`):

- Complete materialized ST interval wins despite configured weekly interval.
- Clearing both endpoints on this own ST uses STORE_WEEKLY; native arrival waits until11:30, whole unloading fits the first interval.
- Final `RRL_TT_TIME_API.approve` produces **exactly the same route_schedule JSON** as native preview; V7. Final approval transaction rolled back.
- Owner profile update changes source_hash; approval using the earlier hash is rejected TT_TIME_SOURCE_CHANGED.
- All original non-profile source data (including ST windows and synthetic road timestamps) restored exactly; approval version unchanged. Original profile was absent, therefore restored by owner as semantically UNCONFIGURED **version3**, preserving immutable history, rather than deleting a profile. This intentionally changes the fixture source hash relative to its original absent-profile state.

Clean CONFIG transactions reject DIRTY_TRANSACTION after prewrites. The first outer-rollback attempt hit this guard, and all attempted changes were rolled back. The successful run therefore used separate clean owner transactions for temporary profile versions1/2 and restore3; own ST/road configuration restored exactly. Temporary profile reason strings retain the earlier phrase 'outer rollback'; actual persistence is the versioned restore described here. The approval itself was rolled back. No existing owner/guard was bypassed.

Measured native calls (not HTTP): context13.122–31.628ms, materialized calculation19.109ms, weekly calculation21.213ms, final approval203.692ms. These are single bounded observations, not p95/performance acceptance.

### Slow SQL decision

`native_sql.json`: changed packages INVALID=[], matching RRL_SQL_SLOW_LOG entries in last hour=[], actual current route-leg SQL average0.819ms. Profile lookup average0.041ms; window lookup0.081ms. Bounded read-only `material` on real address sets measured1address13.024ms,8addresses8.096ms,200addresses75.233ms (cold effects visible). The two-per-address lookup is bounded and does **not** dominate this measured scenario. Retain current PK lookups; no speculative batching/index migration. Owner root/transport revisits batching if full200-stop route pilot shows material dominating measuredp95. API audit unavailable for this native-direct case by design; native timings, V$SQL and slow-log evidence are supplied instead.

No additional DDL was applied by this agent. Root retains common release gate/UI acceptance/publication ownership.
