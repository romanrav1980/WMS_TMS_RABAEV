# Runbook: Create WMS API Server

## Goal

Create a modern API server that replaces `Tserver` as the long-term integration boundary between terminals, desktop clients, external integrations, and Oracle.

The first version should not rewrite the Oracle business logic. It should wrap existing PL/SQL and SQL-backed operations behind explicit, typed, observable API endpoints.

## Recommended Technology

Use **ASP.NET Core Web API on .NET 10 LTS** as the primary stack.

Recommended components:

- ASP.NET Core Minimal APIs or Controllers for HTTP endpoints.
- `Oracle.ManagedDataAccess.Core` for Oracle access.
- Dapper or plain ADO.NET for stored procedure calls and tightly controlled SQL.
- OpenAPI/Swagger for contract documentation.
- Serilog or built-in structured logging.
- Windows Service hosting first; Linux container later if infrastructure allows it.

Why this is the best fit:

- The current codebase is already C#.
- The team can migrate `Tserver` behavior incrementally instead of crossing both language and architecture boundaries at once.
- Oracle stored procedure calls map naturally to `Oracle.ManagedDataAccess`.
- It is practical to run near the existing Windows/Oracle environment.
- It gives a clean path to serve both old terminal adapters and future clients.

Current version note:

- As of 2026-05-11, Microsoft lists .NET 10 as an active LTS release with support until 2028-11-14.
- Microsoft recommends Minimal APIs for new ASP.NET Core HTTP API projects.
- Oracle documents ODP.NET Core as a fully managed ADO.NET provider available through the `Oracle.ManagedDataAccess.Core` NuGet package.

## Acceptable Alternatives

| Stack | When it makes sense | Tradeoff |
| --- | --- | --- |
| Java Spring Boot + Oracle JDBC | If the infrastructure/team is already Java-heavy. | Strong enterprise option, but heavier migration from current C# code. |
| Python FastAPI + `oracledb` | Good for prototypes, admin APIs, and integration glue. | Less natural for replacing C# Tserver as a long-lived warehouse transaction gateway. |
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
src/
  Wms.Api/
    Program.cs
    appsettings.json
    Features/
      Users/
      Products/
      Lots/
      Places/
      Orders/
      Forklift/
      Inventory/
      Picking/
    LegacyTcp/
      LegacyTcpHostedService.cs
      LegacyProtocolParser.cs
      LegacyProtocolWriter.cs
      LegacyCommandMapper.cs
    Oracle/
      OracleConnectionFactory.cs
      OracleProcedureExecutor.cs
      OracleOptions.cs
    Common/
      RequestContext.cs
      ApiError.cs
      Idempotency.cs
tests/
  Wms.Api.Tests/
```

## Minimum Viable Version

The first useful version should include:

- `GET /api/users/{userId}` mapped from `GET_RUSER`.
- `GET /api/products/by-barcode/{barcode}` mapped from `GET_PRODUCT_INFO`.
- `GET /api/lots/{usscc}/items` mapped from `GET_LOT_ITEMS`.
- `POST /api/terminal/lots/{usscc}/check` mapped from `LOT_CHECK_PASSED`.
- allowlisted compatibility calls for the observed `CALL_SPF` procedures.
- structured logs and Oracle call timing.
- configuration-driven Oracle connection string with secrets outside source code.

## Local Test Status

Checked on 2026-05-11:

- .NET SDK 9.0 is installed and can build/run ASP.NET Core APIs locally.
- .NET 10 SDK is not installed yet, so local development can start on `net9.0` or the SDK should be upgraded before targeting `net10.0`.
- Oracle Developer VM is reachable from the Windows host at `127.0.0.1:1521`.
- `tnsping //127.0.0.1:1521/orcl` succeeds.
- Old Windows `sqlplus` 10.2 fails against the VM with `ORA-28040`, so do not use it as the API connectivity test.
- `Oracle.ManagedDataAccess.Core` 23.8.0 builds under the local ASP.NET Core probe project.
- ASP.NET Core probe endpoint `/db/ping` successfully connected through `Oracle.ManagedDataAccess.Core` to service `orcl` and returned `SYSTEM` from `dual`.
- Legacy `DBWMS` from repository `tnsnames.ora` currently times out at `192.168.208.9:1521`; use the VM for API development tests until real WMS database network access is available.

## Non-Goals For The First Version

- Do not rewrite PL/SQL business logic.
- Do not replace the desktop client in the same step.
- Do not redesign all warehouse workflows before the API boundary exists.
- Do not introduce a generic remote stored procedure API for new clients.

## Decision

The recommended path is ASP.NET Core Web API on .NET 10 LTS plus a legacy TCP compatibility adapter. This keeps migration close to the existing C# codebase, preserves the Oracle PL/SQL core, and gives the project a proper API boundary without forcing a big-bang rewrite.

## Reference Links

- [.NET Support Policy](https://dotnet.microsoft.com/en-us/platform/support/policy)
- [ASP.NET Core APIs overview](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/apis?view=aspnetcore-10.0)
- [Oracle ODP.NET Core installation](https://docs.oracle.com/en/database/oracle/oracle-database/26/odpnt/InstallODPCore.html)
