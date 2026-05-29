# TMS-2 Release Acceptance Runbook

Дата обновления: 2026-05-29.

Назначение: единый порядок финальной приемки ТМС-2 перед параллельной эксплуатацией с legacy C# transport module.

## Scope

Входит:

- Dispatcher Sprint 1-6 and UX hardening through Sprint 95.
- MAP/VRP Sprint 7-10 and Sprint 24.
- ARM/Gantt Sprint 11-14.
- Billing Sprint 15-28.
- Routing infrastructure checks for OSRM/Valhalla/Haversine.
- Oracle fixture `055_apply.sql` for Sprint 9 historical templates.
- Wave 3 Business Factor Trace: end-to-end factor participation tests and no-mutation factor-load runner.

Не входит:

- warehouse-map;
- MES;
- WMS picking/wave;
- SAP/SAP integration.

## Preconditions

1. Oracle dev/staging schema is available as `RABAEV`.
2. API runs through root `serv.bat` or equivalent on `config/project.defaults.json -> local.apiPort`.
3. Frontend runs through root `front.bat` or equivalent on `config/project.defaults.json -> local.frontendPort`; do not use port `3001`.
4. Test seed date is `2026-05-24`.
5. Slow SQL/SKV review is mandatory after every release-gate run. See [`slow_sql_review.md`](slow_sql_review.md).
5. Environment for Oracle apply:

```powershell
$env:TMS_ORACLE='User Id=RABAEV;Password=<password>;Data Source=127.0.0.1:1521/orcl'
```

## Apply Acceptance Fixture

Sprint 9 requires one historical planner template before the accepted seed date.

```powershell
dotnet run --project tools\oracle_apply\OracleApply.csproj -- TMS_ORACLE db\migrations\2026-05-29_tms2_planner_template_fixture\055_apply.sql --encoding=utf8
```

Verify:

```powershell
dotnet run --project tools\oracle_apply\OracleApply.csproj -- TMS_ORACLE --query "SELECT SOLVER, TO_CHAR(PLAN_DATE,'YYYY-MM-DD') AS PLAN_DATE FROM RRL_PLANNER_PLANS WHERE SOLVER='s9-template-fixture'"
```

Expected: one row with `PLAN_DATE = 2026-05-23` for release seed `2026-05-24`. A best-effort compatibility row for `PLAN_DATE = 2026-05-24` may also exist when `2026-05-25` source STs are still present.

Rollback if needed:

```powershell
dotnet run --project tools\oracle_apply\OracleApply.csproj -- TMS_ORACLE db\migrations\2026-05-29_tms2_planner_template_fixture\055_rollback.sql --encoding=utf8
```

## Non-Mutating Release Gate

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\tms2-release-gate.ps1 -SeedDate 2026-05-24
```

Current accepted strict result:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\tms2-release-gate.ps1 -SeedDate 2026-05-24 -IncludeSprint60To95 -IncludeUiSmoke -IncludeLoadSmoke -IncludeWave3
```

Accepted 2026-05-29 final sign-off result after daily VRP acceptance, v2-strengthened full-system Wave 3 Business Factor Trace, and planner-history hardening: routing smoke passed; core `446 passed`, no pytest skips; Sprint 60-95 `234 passed`; all Sprint 60-95 load scripts passed; Wave 3 load passed; grouped UI smoke passed; 2000-row NFR smoke passed with `firstRenderMs=763`, bounded rows `31/43/33`. The runner fails on any native command error and `TMS_FAIL_ON_SKIPS=1`.

Slow SQL review after the final full gate, using `from_log_id=1153`: `[]` for `min_elapsed_ms=500`. Decision: no fresh transport SQL above the review threshold. The earlier `/planner/history` slow rows were fixed by bounding the endpoint to default `limit=25`, clamping explicit limits to `1..500`, sorting newest-first with `FETCH FIRST`, and serializing the cache lookup/fetch/store path to avoid a cold-cache stampede. Historical 6-13s `/tasks?date_to=...` gate entries were corrected by narrowing billing fixture date ranges.

## Wave 3 Business Factor Trace

Functional/E2E gate:

```powershell
python -m pytest tests\transport\test_wave3_business_factor_trace.py tests\transport\test_wave3_full_system_coverage.py -q -ra --tb=short
```

Expected: `14 passed`. The factor gate traces coordinates, pallet capacity, weight, warehouse, transport type, store time windows, `TW_STRICT`, unload norm, readiness, route totals, transport-type filtering, and four-slot vehicle availability from source contract to solver response. It also checks v2 data-fidelity patterns: values are non-default/distinct, `available-sts` matches `planner/orders`, VRP stops match planner time windows when Oracle values exist, and a cleanup-bound temp route preserves pallet/weight/readiness facts in `task/sts`. The full-system coverage lock imports real TMS-2 routers and requires every endpoint to have a Wave 3 business-process owner, factors, source/state evidence, functional gate, and load/UI/E2E evidence.

No-mutation load gate:

```powershell
python tests\transport\transport_wave3_business_factor_load_test.py
```

Current local evidence from the final full sign-off gate: available STs p95 `62.3 ms`, planner orders p95 `283.4 ms`, vehicle availability p95 `148.4 ms`, routing status p95 `4268.2 ms` because it probes live providers, planner solve p95 `1339.4 ms`; all response factor contracts and non-default checks passed.

## Mutating Sprint 8 Apply Evidence

Run this only on an isolated Oracle fixture or with immediate cleanup on shared dev.

Before:

```powershell
dotnet run --project tools\oracle_apply\OracleApply.csproj -- TMS_ORACLE --query "SELECT NVL(MAX(ID),0) AS MAX_ID FROM RRL_TRANSPORT_TASK"
```

Run:

```powershell
$env:TMS_RUN_MUTATING_VRP_APPLY='1'
python -m pytest tests\transport\test_sprint8_functional.py -q -ra --tb=short
```

Accepted final-sprint result: `23 passed` on seed `2026-05-24`; the mutating test verifies created task IDs, reads assigned STs for each created route, and cancels those tasks in cleanup. Post-cleanup API check found `active_vrp_auto_tasks=0`.

Cleanup pattern for shared dev after recording `MAX_ID`:

```sql
UPDATE RABAEV.RRL_SBORKA_PALLETS
   SET TRANSTASK_ID = NULL
 WHERE TRANSTASK_ID IN (
   SELECT ID FROM RABAEV.RRL_TRANSPORT_TASK
    WHERE ID > :max_id
      AND SHIPMENT_DATE >= DATE '2026-05-25'
      AND SHIPMENT_DATE <  DATE '2026-05-26'
      AND NVL(DELETED,0) = 0
 );

UPDATE RABAEV.RRL_TRANSPORT_TASK
   SET DELETED = 1
 WHERE ID > :max_id
   AND SHIPMENT_DATE >= DATE '2026-05-25'
   AND SHIPMENT_DATE <  DATE '2026-05-26'
   AND NVL(DELETED,0) = 0;

COMMIT;
```

Verify:

```sql
SELECT COUNT(*) AS ACTIVE_NEW_TASKS
  FROM RABAEV.RRL_TRANSPORT_TASK
 WHERE ID > :max_id
   AND NVL(DELETED,0) = 0;
```

Expected: `0`.

## Routing Infrastructure

Static/compose smoke:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\tms2-routing-smoke.ps1
```

Real OSRM/Valhalla smoke requires prepared local map data:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\tms2-routing-data-prep.ps1 -PbfUrl https://download.geofabrik.de/russia-latest.osm.pbf
docker compose -f docker-compose.osrm.yml up -d
$env:VALHALLA_FORCE_REBUILD='True'; $env:VALHALLA_USE_TILES_IGNORE_PBF='False'; docker compose -f docker-compose.valhalla.yml up -d
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\tms2-routing-smoke.ps1
```

Then verify API:

```powershell
curl.exe -u admin:admin123 http://127.0.0.1:8088/api/admin/transport/routing/status
curl.exe -u admin:admin123 -X POST "http://127.0.0.1:8088/api/admin/transport/distance-matrix/rebuild?source=osrm"
```

Expected in normal production routing mode: `active_provider` is `osrm` or `valhalla`, the selected provider is available, and the matrix rebuild returns a non-zero `pairs` count.

## Frontend NFR

Static gate:

```powershell
python -m pytest tests\transport\test_frontend_virtualization_nfr.py -q
```

Visual/browser gate:

```powershell
node tests\ui\transport_table_2000_nfr_smoke.cjs
```

Expected:

- first render under local smoke threshold;
- table DOM rows remain bounded;
- virtualizer shows 2000 ST total;
- scrolling through the full virtualized list keeps bounded rows;
- selection bar still works.

Current local evidence, 2026-05-29: `{"ok":true,"firstRenderMs":848,"renderedRows":51,"renderedAfterScroll":52,"page2RenderedRows":51}`.

## Final Sign-Off

Release acceptance can be marked ready when:

- `055_apply.sql` is applied and verified;
- strict release gate has no failed commands and no pytest skips;
- Sprint 8 mutating apply evidence is recorded and cleaned up;
- routing infrastructure smoke is documented for current provider mode;
- frontend 2000-row smoke passes;
- slow SQL review is recorded and every long query has a decision;
- encoding check passes;
- `git diff --check` has no errors other than normal CRLF warnings.
- fresh slow SQL review after the final full gate has no unresolved rows above the accepted threshold.
