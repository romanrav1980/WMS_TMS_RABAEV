# WMS/TMS Python API Server

FastAPI backend for the WMS/TMS modernization track.

The stack follows the local `C:\WEB\demand_forecast\demand_forecast_backend` style:

- FastAPI
- Pydantic models
- SQL execution helpers
- Uvicorn runtime

Intentional improvements for this project:

- modular routers instead of one huge `main.py`;
- Oracle credentials are read from environment variables;
- Oracle writes use package calls or bind parameters;
- legacy `Tserver` protocol is isolated in a compatibility router;
- generic `CALL_SPF` is allowlisted, not public arbitrary procedure execution.

## Run Locally

```powershell
cd C:\projects\TMS\api\wms_api_server
$env:WMS_ORACLE_USER="RABAEV"
$env:WMS_ORACLE_PASSWORD="<password>"
$env:WMS_ORACLE_DSN="127.0.0.1:1521/orcl"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8088
```

OpenAPI:

```text
http://127.0.0.1:8088/docs
```

## Implemented Surface

Core:

- `GET /health`
- `GET /db/ping`

Production traceability:

- `POST /api/production-batches`
- `POST /api/production-batches/{prod_batch_id}/pallets`
- `POST /api/production-batches/{prod_batch_id}/raw-usage`
- `POST /api/production-batches/{prod_batch_id}/crpt-codes`
- `POST /api/production-batches/{prod_batch_id}/aggregations`
- `POST /api/production-batches/{prod_batch_id}/mercury`
- `GET /api/production-batches/{prod_batch_id}/status`

Legacy `Tserver` compatibility:

- `POST /api/legacy/tserver/execute`
- `GET /api/terminal/users/{user_id}`
- `GET /api/products/by-barcode/{barcode}`
- `GET /api/lots/{usscc}/items`
- `GET /api/places/{place_id}/items`
- `POST /api/terminal/lots/{usscc}/check`
- `POST /api/terminal/place-checks`
- `POST /api/terminal/order-checks`
- `POST /api/terminal/call-spf`

## Notes

Some legacy `Tserver` operations update both Oracle and Access MDB. This first API version implements the Oracle part and records the Access limitation in the response/documentation. The Access side should be replaced by Oracle/API-owned state or by a separate adapter before production cutover.

## Local Smoke Status

Checked on 2026-05-17:

- `python -m py_compile` passes for all files under `app/`.
- `GET /health` returns `{"status": "ok"}`.
- `GET /db/ping` returns `RABAEV / orcl / ORCL`.
- `GET /api/terminal/users/DO` returns a legacy `USER_INFO` block.
- `POST /api/legacy/tserver/execute` with `FUNC=GET_RUSER|USERID=DO|` returns an encoded legacy `USER_INFO` payload.
- `GET /api/lots/{usscc}/items` was checked against an existing lot and returned `LOT_LINES`, `LOT_LINE`, and `END`.
