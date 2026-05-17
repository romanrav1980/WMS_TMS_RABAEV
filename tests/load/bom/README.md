# BOM Load Tests

This folder contains local load and stress tests for the WMS/MES BOM implementation.

## Scope

The test uses only rows with the `LOAD-BOM-*` prefix and exercises:

- BOM creation;
- BOM line creation;
- approve lifecycle;
- primary BOM conflict validation;
- concurrent `calculate`;
- concurrent default BOM lookup;
- list/detail reads.

It does not drop tables and does not touch production rows.

The Oracle columns `TARGET_ARTICUL` and `COMPONENT_ARTICUL` are widened to 40 characters by migration `010`, so the runner intentionally generates 40-character product and component material codes. The full `LOAD-BOM-*` run marker is stored in `BOM_CODE` for safe cleanup.

## Start Backend

From repository root:

```bat
serv.bat
```

The backend must answer on:

```text
http://127.0.0.1:8088
```

The load runner checks `/health` and `/openapi.json`. If the backend is not up, it attempts to start `serv.bat`.

## Run Small Smoke

```powershell
python tests/load/bom/bom_load_test.py --products 2 --boms-per-product 2 --lines-per-bom 3 --concurrency 2 --calculate-requests 20 --cleanup
```

or:

```bat
tests\load\bom\run_bom_load_test.bat --products 2 --boms-per-product 2 --lines-per-bom 3 --concurrency 2 --calculate-requests 20
```

## Run Larger Local Test

```powershell
python tests/load/bom/bom_load_test.py --products 20 --boms-per-product 5 --lines-per-bom 25 --concurrency 10 --calculate-requests 1000 --cleanup
```

## Cleanup

Default cleanup uses Oracle connection variables:

```text
WMS_ORACLE_USER=RABAEV
WMS_ORACLE_PASSWORD=RABAEVWMS
WMS_ORACLE_DSN=127.0.0.1:1521/orcl
```

Manual SQL cleanup is available in:

```text
tests/load/bom/cleanup_load_bom.sql
```

It deletes only:

- `RRL_TRACE_EVENT` for BOM entities created by `LOAD-BOM-*`;
- `RRL_BOM_AUDIT`;
- `RRL_BOM_LINE`;
- `RRL_BOM`.

## Report

Default report:

```text
tests/load/bom/report.json
```

Metrics include request counts, success/failure counts, RPS, latency `min/p50/p95/p99/max`, per-endpoint summaries, created row counts, and unexpected error samples.

## Local VM Guidance

For the Oracle Developer VM and local FastAPI server, a small smoke should have:

- `failed_requests = 0`;
- `p95` below a few seconds;
- cleanup leaves `LOAD-BOM-* = 0`.

Observed local smoke on 2026-05-17:

- `68` total API requests;
- `0` failed requests;
- `2.267` requests/second;
- latency `p50 = 756.95 ms`, `p95 = 1091.2 ms`;
- cleanup verified `RRL_BOM`, `RRL_BOM_LINE`, and `RRL_BOM_AUDIT` rows for `LOAD-BOM-*` are `0`.

The larger profile is intended to expose regressions and contention, not to define final production capacity.
