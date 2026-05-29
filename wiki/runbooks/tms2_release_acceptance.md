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

Не входит:

- warehouse-map;
- MES;
- WMS picking/wave;
- SAP/SAP integration.

## Preconditions

1. Oracle dev/staging schema is available as `RABAEV`.
2. API runs through root `serv.bat` or equivalent on `config/project.defaults.json -> local.apiPort`.
3. Frontend runs through root `front.bat` or equivalent on `config/project.defaults.json -> local.frontendPort`; do not use port `3001`.
4. Test seed date is `2026-05-25`.
5. Environment for Oracle apply:

```powershell
$env:TMS_ORACLE='User Id=RABAEV;Password=<password>;Data Source=127.0.0.1:1521/orcl'
```

## Apply Acceptance Fixture

Sprint 9 requires one historical planner template before `2026-05-25`.

```powershell
dotnet run --project tools\oracle_apply\OracleApply.csproj -- TMS_ORACLE db\migrations\2026-05-29_tms2_planner_template_fixture\055_apply.sql --encoding=utf8
```

Verify:

```powershell
dotnet run --project tools\oracle_apply\OracleApply.csproj -- TMS_ORACLE --query "SELECT SOLVER, TO_CHAR(PLAN_DATE,'YYYY-MM-DD') AS PLAN_DATE FROM RRL_PLANNER_PLANS WHERE SOLVER='s9-template-fixture'"
```

Expected: one row with `PLAN_DATE = 2026-05-24`.

Rollback if needed:

```powershell
dotnet run --project tools\oracle_apply\OracleApply.csproj -- TMS_ORACLE db\migrations\2026-05-29_tms2_planner_template_fixture\055_rollback.sql --encoding=utf8
```

## Non-Mutating Release Gate

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\tms2-release-gate.ps1 -SeedDate 2026-05-25
```

Current accepted result: `267 passed`.

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

Accepted result: `23 passed`; after the 2026-05-29 repeat run, active `vrp_auto` transport tasks for `2026-05-25` remained `0`.

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
- non-mutating release gate is `267 passed`;
- Sprint 8 mutating apply evidence is recorded and cleaned up;
- routing infrastructure smoke is documented for current provider mode;
- frontend 2000-row smoke passes;
- encoding check passes;
- `git diff --check` has no errors other than normal CRLF warnings.
