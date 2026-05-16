# Runbook: Create WMS API Server

## Goal

Create a modern API server that replaces `Tserver` as the long-term integration boundary between terminals, desktop clients, external integrations, and Oracle.

The first version should not rewrite the Oracle business logic. It should wrap existing PL/SQL and SQL-backed operations behind explicit, typed, observable API endpoints.

## Accepted Technology

Use **Python FastAPI** as the primary API-server stack.

This decision follows the local backend style from `C:\WEB\demand_forecast\demand_forecast_backend`:

- FastAPI for HTTP endpoints and OpenAPI.
- Pydantic models for request/response contracts.
- SQL-oriented service code.
- Uvicorn runtime.

For WMS/TMS the stack is extended with:

- `oracledb` for Oracle package calls and parameterized SQL;
- `sqlalchemy` kept in dependencies for the same family of DB tooling and future query/session work;
- environment-based configuration instead of hardcoded credentials;
- modular routers and services instead of one very large `main.py`;
- allowlisted legacy procedure calls for `CALL_SPF`.

Current implementation:

- [`../../api/wms_api_server/`](../../api/wms_api_server/) contains the first FastAPI server.
- [`../../api/wms_api_server/app/main.py`](../../api/wms_api_server/app/main.py) wires the app and routers.
- [`../../api/wms_api_server/app/routers/tserver.py`](../../api/wms_api_server/app/routers/tserver.py) contains the first `Tserver` compatibility endpoints.
- [`../../api/wms_api_server/app/services/tserver_service.py`](../../api/wms_api_server/app/services/tserver_service.py) maps legacy `FUNC=...|` commands to Oracle-backed handlers.
- [`../../api/wms_api_server/app/services/production_service.py`](../../api/wms_api_server/app/services/production_service.py) wraps `RRL_PRODUCTION_API`.

## Rejected Alternatives For Now

| Stack | When it makes sense | Tradeoff |
| --- | --- | --- |
| ASP.NET Core | Still a strong fit for C# teams. | Rejected by current decision because the target style is Python/FastAPI like the existing demand forecast backend. |
| Java Spring Boot + Oracle JDBC | If infrastructure/team becomes Java-heavy. | Heavier than needed for the first WMS API boundary. |
| Node.js/NestJS + OracleDB | Works for JSON APIs. | Less attractive for Oracle-heavy transactional warehouse operations. |

## Target Architecture

```text
Legacy terminal
   |
   | old TCP FUNC protocol
   v
Compatibility adapter
   |
   | HTTP JSON / internal call
   v
WMS API Server
   |
   | typed Oracle calls
   v
Oracle PL/SQL and WMS tables
```

The compatibility adapter can initially live inside the new API server as a hosted TCP listener, or as a separate small process. Its only purpose is to keep existing terminals working while the API contract is stabilized.

For new clients:

```text
C# Desktop Client / Integration Worker / New Terminal App
   |
   | HTTPS JSON
   v
WMS API Server
   |
   v
Oracle
```

## First API Surface

Start with the terminal contour, because it already has an API-like boundary.

Initial modules:

- `Users`: terminal user lookup and permissions.
- `Products`: barcode lookup and product package updates.
- `Lots`: lot items and lot check confirmation.
- `Places`: cell/place inventory reads and place check confirmation.
- `Orders`: order info, order lines, order check confirmation, picker assignment, zone update.
- `Forklift`: pallet destination, replenishment hints, forklift statistics.
- `Inventory`: initial inventory lines, cell revision, next/previous cell.
- `Picking`: full-pallet picking.

Use [`../concepts/tserver_api_registry.md`](../concepts/tserver_api_registry.md) as the initial contract inventory.

## Endpoint Design Rules

- One endpoint must represent one domain operation, not one arbitrary stored procedure.
- Do not expose `SPF_NAME` to new clients.
- Keep Oracle procedure names inside the server implementation.
- Use typed JSON request/response DTOs.
- Include `requestId` for every write operation.
- Make warehouse scan/write operations idempotent where possible.
- Return structured errors: `code`, `message`, `details`, `legacyReason`.
- Log request start/end, user, terminal id, operation, result, and Oracle call duration.

## Database Access Rules

- The API server must not connect as schema owner `RABAEV`.
- Create a runtime user such as `WMS_API_APP`.
- Grant only required `EXECUTE`, `SELECT`, `INSERT`, `UPDATE`, and `DELETE` permissions.
- Prefer stored procedure/package calls for writes.
- If direct SQL is unavoidable during migration, parameterize it.
- Move dynamic `CALL_SPF` to an allowlist immediately.

## Compatibility Plan

Phase 1: mirror current Tserver behavior.

- Implement the legacy TCP reader/writer.
- Decode `FUNC=...|key=value|...`.
- Map each legacy `FUNC` to an internal API handler.
- Keep old response block names, such as `USER_INFO`, `LOT_LINE`, `END`.
- Add logs and request IDs around every call.

Phase 2: create typed HTTP endpoints.

- Expose JSON endpoints for the same operations.
- Add OpenAPI documentation.
- Add tests for request validation and legacy protocol mapping.

Phase 3: remove risky behavior.

- Replace generic `CALL_SPF` with explicit allowlisted operations.
- Move direct SQL writes behind stored procedures or repository methods with parameters.
- Add service account permissions and remove embedded Oracle credentials from clients.

Phase 4: migrate clients.

- New terminal app or desktop functions call HTTP API directly.
- Old Windows CE terminals continue through compatibility adapter until retired.
- Desktop write operations move first; reporting/read screens can migrate later.

## Suggested Project Layout

```text
api/
  wms_api_server/
    requirements.txt
    .env.example
    README.md
    app/
      main.py
      config.py
      db.py
      oracle_gateway.py
      legacy_protocol.py
      schemas.py
      routers/
        health.py
        production.py
        tserver.py
      services/
        production_service.py
        tserver_service.py
```

## Minimum Viable Version

The first useful version should include:

- `GET /health`.
- `GET /db/ping`.
- `GET /api/terminal/users/{userId}` mapped from `GET_RUSER`.
- `GET /api/products/by-barcode/{barcode}` mapped from `GET_PRODUCT_INFO`.
- `GET /api/lots/{usscc}/items` mapped from `GET_LOT_ITEMS`.
- `POST /api/terminal/lots/{usscc}/check` mapped from `LOT_CHECK_PASSED`.
- allowlisted compatibility calls for the observed `CALL_SPF` procedures.
- production traceability endpoints over `RRL_PRODUCTION_API`.
- structured logs and Oracle call timing.
- configuration-driven Oracle connection string with secrets outside source code.

## Local Test Status

Checked on 2026-05-17:

- Python `3.13.3` is installed.
- The new FastAPI source under `api/wms_api_server/app` passes `python -m py_compile`.
- Oracle Developer VM is reachable from the Windows host at `127.0.0.1:1521/orcl`.
- The current Oracle schema has applied migrations:
  - `2026-05-17-001-feed-factory-traceability`;
  - `2026-05-17-002-feed-factory-traceability-api`.
- `RRL_PRODUCTION_API` is valid in Oracle and is the preferred DB write boundary for feed-factory traceability.
- Full runtime API smoke still requires installing Python dependencies from `api/wms_api_server/requirements.txt`.

## Non-Goals For The First Version

- Do not rewrite PL/SQL business logic.
- Do not replace the desktop client in the same step.
- Do not redesign all warehouse workflows before the API boundary exists.
- Do not introduce a generic remote stored procedure API for new clients.

## Decision

The accepted path is Python FastAPI plus a legacy `Tserver` compatibility layer. This matches the existing local backend methodology from the demand forecast project while still preserving the Oracle PL/SQL core and avoiding a big-bang rewrite.

## Reference Links

- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [python-oracledb documentation](https://python-oracledb.readthedocs.io/)
- [SQLAlchemy Oracle dialect documentation](https://docs.sqlalchemy.org/en/latest/dialects/oracle.html)
