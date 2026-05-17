# Local Launch Scripts

Use root `.bat` files for local Windows runs:

- [`../serv.bat`](../serv.bat): starts the WMS FastAPI server on port `8088`.
- [`../front.bat`](../front.bat): starts the WMS admin frontend on port `3000`.
- [`../terminal.bat`](../terminal.bat): starts the WMS terminal Web/PWA app on port `3010`.
- [`../worker.bat`](../worker.bat): starts the WMS external outbox worker for Oracle-backed adapter events.
- [`../production-exchange.bat`](../production-exchange.bat): starts the production-release folder/JSON exchange worker.
- [`../stop-listeners.bat`](../stop-listeners.bat): stops all known local WMS listeners and workers.
- [`kill-port.ps1`](kill-port.ps1): shared cleanup helper for stale listeners and old command-line matched worker processes.
- [`stop-listeners.ps1`](stop-listeners.ps1): grouped listener shutdown command for API, admin frontend, terminal frontend, and outbox worker.
- [`check-encoding.ps1`](check-encoding.ps1): checks UTF-8 text files for common mojibake markers before commit.

Port-based scripts first call `scripts/kill-port.ps1`, terminate an existing listening process on that port, terminate Uvicorn reloader children such as `parent_pid=<old pid>`, and fail loudly if the port is still busy. This keeps repeated local launches from silently attaching to stale processes.

`worker.bat` and `production-exchange.bat` have no listening port, so they use the same helper with `-CommandLineLike` to clear stale worker loops before starting a new one.

Current behavior:

- `serv.bat` starts `api/wms_api_server` through `python -m uvicorn`.
- `worker.bat` starts `api/wms_api_server` through `python -m app.workers.outbox_worker --loop`.
- `production-exchange.bat` starts `api/wms_api_server` through `python -m app.workers.production_exchange_worker --loop`.
- `front.bat` starts `admin/wms_admin_frontend` with `npm start` when that React project exists.
- Until the React admin frontend is created, `front.bat` serves the raw UI reference from `wiki-raw/wms_admin_ui_reference` through `python -m http.server`.
- `terminal.bat` starts `terminal/wms_terminal_web` with `npm run dev`.

Environment defaults:

- `WMS_ORACLE_USER=RABAEV`
- `WMS_ORACLE_PASSWORD=RABAEVWMS`
- `WMS_ORACLE_DSN=127.0.0.1:1521/orcl`
- `WMS_API_AUDIT_ENABLED=1`
- `WMS_API_AUDIT_LOCAL_DIR=runtime\api_audit`
- `WMS_API_REPLAY_BASE_URL=http://127.0.0.1:8088`
- `WMS_PRODUCTION_EXCHANGE_ROOT_DIR=exchange\production_release`
- `REACT_APP_API_BASE_URL=http://127.0.0.1:8088`
- `VITE_WMS_API_BASE_URL=http://127.0.0.1:8088`

Override these variables before running the scripts when a different local setup is needed.

## Encoding Discipline

Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-encoding.ps1` before committing wiki, HTML, SQL, Python, or JavaScript changes that include Russian text. The default mode checks changed and new files; add `-All` for a full repository scan. The repository uses UTF-8; when inspecting files in PowerShell, prefer `Get-Content -Encoding UTF8` to avoid console-side mojibake.

Oracle SQL migrations must also be applied as UTF-8. The tracked helper `tools/oracle_apply/OracleApply.csproj` reads scripts as strict UTF-8 by default and accepts legacy Windows-1251 only when it is explicitly requested with `--encoding=cp1251`. New migrations and seed scripts must not rely on the local Windows code page. Verification scripts that insert/read Russian seed data should include a small mojibake-marker check when practical. The older `tmp/oracle_apply` copy is a local scratch copy only.

The full `-All` mode intentionally checks only maintained roots and skips archived/legacy import roots such as `MINI WMS/`, `SQL/`, `WMS перенос v1/`, old restore points, and `db/windowsapplication2_xp12_oracle/`. Those folders contain historical source material with mixed encodings. Current maintained work should live in `api/`, `db/migrations/`, `wiki/`, `wiki-raw/`, `scripts/`, `terminal/`, `tests/`, and `tools/`, where the UTF-8 guard is enforced.

## Load Tests

BOM load tests live in [`../tests/load/bom`](../tests/load/bom). The quick local smoke is:

```powershell
python tests/load/bom/bom_load_test.py --products 2 --boms-per-product 2 --lines-per-bom 3 --concurrency 2 --calculate-requests 20 --cleanup
```

or:

```bat
tests\load\bom\run_bom_load_test.bat --products 2 --boms-per-product 2 --lines-per-bom 3 --concurrency 2 --calculate-requests 20
```

The runner uses the shared `serv.bat` startup path if the backend is not responding, writes `tests/load/bom/report.json`, and deletes only test BOM rows whose `BOM_CODE` starts with `LOAD-BOM-`.
