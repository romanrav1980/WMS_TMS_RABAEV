# ТМС-2 — local verification runbook

Дата обновления: 2026-05-28.

Назначение: единая инструкция, как локально проверить ТМС-2 после изменений.

## Порты и запуск

- Единый источник локальных host/ports/Oracle DSN: [`../../config/project.defaults.json`](../../config/project.defaults.json).
- API: root `serv.bat`, по умолчанию `local.apiPort`.
- Frontend: root `front.bat`, по умолчанию `local.frontendPort`.
- Для временного переопределения использовать env: `TMS_LOCAL_HOST`, `TMS_FRONTEND_PORT`, `TMS_API_PORT`, `TMS_API_BIND_HOST`, `TMS_FRONTEND_BASE_URL`, `TMS_API_BASE_URL`, `WMS_ORACLE_DSN`.
- UI/load tests должны брать адреса через `tests/support/project_config.cjs` или `tests/support/project_config.py`; новые hardcoded IP/port в тестах не добавлять.
- Не использовать frontend port `3001`.
- Не трогать `warehouse-map`, MES, WMS-picking, если задача явно про ТМС-2.

## Oracle env

Локальные проверки используют `TMS_ORACLE`.

Пример PowerShell:

```powershell
$env:TMS_ORACLE='User Id=RABAEV;Password=...;Data Source=127.0.0.1:1521/orcl'
```

Не коммитить реальные пароли в wiki/code.

## Быстрый audit перед работой

```powershell
git status --short
rg --files | rg "transport|Transport|billing|planner|gantt|vrp"
rg --files tests\transport
```

Unrelated dirty worktree не откатывать без явной команды.

## Миграции

Применение dev migration:

```powershell
dotnet run --project tools\oracle_apply\OracleApply.csproj -- TMS_ORACLE db\migrations\<folder>\<file>.sql --encoding=utf8
```

После структурных изменений:

- проверить `ALL_TABLES`, `ALL_TAB_COLUMNS`, `ALL_ARGUMENTS`;
- проверить legacy-visible views/functions;
- если менялись русские тексты, запустить encoding check.

## Functional tests по блокам

Block I:

```powershell
python -m pytest tests\transport\test_sprint4_functional.py tests\transport\test_sprint5_functional.py tests\transport\test_sprint6_functional.py -q -ra --tb=short
```

Block II:

```powershell
python -m pytest tests\transport\test_sprint7_functional.py tests\transport\test_sprint8_functional.py tests\transport\test_sprint9_functional.py tests\transport\test_sprint10_functional.py -q -ra --tb=short
```

Block III:

```powershell
python -m pytest tests\transport\test_sprint11_functional.py tests\transport\test_sprint12_functional.py tests\transport\test_sprint13_functional.py tests\transport\test_sprint14_functional.py -q -ra --tb=short
```

Block IV:

```powershell
python -m pytest tests\transport\test_sprint15_functional.py tests\transport\test_sprint16_functional.py tests\transport\test_sprint17_functional.py tests\transport\test_sprint18_functional.py tests\transport\test_sprint19_functional.py tests\transport\test_sprint20_functional.py -q -ra --tb=short
```

Full Sprint 4-20 gate:

```powershell
python -m pytest tests\transport\test_sprint4_functional.py tests\transport\test_sprint5_functional.py tests\transport\test_sprint6_functional.py tests\transport\test_sprint7_functional.py tests\transport\test_sprint8_functional.py tests\transport\test_sprint9_functional.py tests\transport\test_sprint10_functional.py tests\transport\test_sprint11_functional.py tests\transport\test_sprint12_functional.py tests\transport\test_sprint13_functional.py tests\transport\test_sprint14_functional.py tests\transport\test_sprint15_functional.py tests\transport\test_sprint16_functional.py tests\transport\test_sprint17_functional.py tests\transport\test_sprint18_functional.py tests\transport\test_sprint19_functional.py tests\transport\test_sprint20_functional.py -q -ra --tb=short
```

Current strict baseline after TMS-2 fixture `055_apply.sql`: no failed commands and no pytest skips. The full 2026-05-29 release gate on seed date `2026-05-24` produced core `427 passed`, Sprint 60-95 `234 passed`, load/UI/NFR passed.

Stable release-gate runner for Sprint 1-20 plus routing/NFR static checks:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\tms2-release-gate.ps1 -SeedDate 2026-05-24
```

Run the mutating VRP apply only on an isolated Oracle fixture:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\tms2-release-gate.ps1 -SeedDate 2026-05-24 -IncludeMutatingVrpApply
```

On shared dev Oracle, prefer running only `tests\transport\test_sprint8_functional.py` with `TMS_RUN_MUTATING_VRP_APPLY=1`, then clean up created tasks/ST assignments immediately.

## Encoding and diff checks

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-encoding.ps1
git diff --check -- <changed-files>
```

## Как трактовать skipped

Allowed temporarily:

- no free STs in current dated seed;
- no geocoded STs;
- no historical planner templates;
- no active vehicle fixture;
- VRP solver returns empty plan on current seed.

Not acceptable for release:

- Sprint 1-3 missing direct tests;
- Sprint 8 route-detail/apply tests skipped because no deterministic VRP fixture;
- billing protection tests skipped because no billable task fixture.

## Frontend smoke

Frontend only on:

```text
config/project.defaults.json -> local.frontendPort
```

Minimum manual smoke after API hardening:

1. Open transport page.
2. Load available STs.
3. Open routes list.
4. Open planner page and routing status.
5. Open Gantt/plan-fact paths if exposed in current UI.
6. Open billing registry.
7. Verify no console/network 500 on primary tabs.

## Routing and Table NFR Smoke

OSRM/Valhalla compose and optional live endpoint smoke:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\tms2-routing-smoke.ps1
```

The script validates both compose files and checks live OSRM/Valhalla endpoints if containers are running. If neither container is up, Haversine fallback remains acceptable for normal local development.

Static NFR gates:

```powershell
python -m pytest tests\transport\test_routing_infrastructure.py tests\transport\test_frontend_virtualization_nfr.py -q
```

For final release, run the visual/browser NFR smoke:

```powershell
node tests\ui\transport_table_2000_nfr_smoke.cjs
```

It uses a mocked 2000-row available-ST dataset and confirms bounded DOM through pagination plus windowed row rendering.

## Slow SQL Review

Every meaningful case, load test, release gate, and pilot rehearsal must finish with the slow SQL/SKV review from [`slow_sql_review.md`](slow_sql_review.md). For release gates, record the last `LOG_ID` before the run and inspect fresh rows after the run with `from_log_id=<last_log_id_plus_1>`.

## Release and Pilot Docs

- [`tms2_release_acceptance.md`](tms2_release_acceptance.md): final acceptance sequence.
- [`tms2_pilot_checklist.md`](tms2_pilot_checklist.md): 5-day parallel-operation checklist and incident rules.
- [`slow_sql_review.md`](slow_sql_review.md): mandatory slow SQL/SKV review and remediation decision rules.
