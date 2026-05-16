# Strategic Development Plan

## Goal

Move WMS/TMS from direct legacy database access toward a controlled operational platform:

- Oracle remains the system of record during the transition.
- All mutating operations gradually move behind one API boundary.
- Terminal work moves to a modern Android application.
- Regulated integrations are isolated behind auditable adapters.

## Current Baseline

Known project parts:

- Oracle schema `RABAEV`, PL/SQL procedures, functions, triggers, and restored production-like data.
- C# WinForms desktop client.
- `Tserver` terminal contour, which currently behaves like an old API gateway over Oracle calls.
- External integration area for `SUPERMAG` / `Sfera` and future regulated flows.

Important publication rule:

- SAP/SAP_INTEGRATION projects are local-only and are not published to GitHub.

## Текущий Статус Реализации

На 2026-05-17 первый слой реализации для фабрики кормов уже внесен в Oracle:

- применена миграция `2026-05-17-001-feed-factory-traceability`;
- применена миграция `2026-05-17-002-feed-factory-traceability-api`;
- в схеме есть первые таблицы для партий производства, партий сырья, вовлечения сырья, Меркурия, Честного знака / CRPT, SSCC-агрегации, outbox и журнала JSON-файлового обмена;
- PL/SQL пакет `RRL_PRODUCTION_API` валиден и является первым управляемым DB API для этого контура;
- проверка live Oracle после реализации показала `458 VALID` объектов без учета recycle bin и `0 INVALID`;
- кодовая точка после реализации: `444354a`.

Следующий стратегический шаг - не рисовать экраны, а поставить стабильную сервисную границу поверх `RRL_PRODUCTION_API`. После этого к ней подключаются файловый обмен, адаптеры Меркурия/Честного знака и выбранные legacy-потоки.

Тактический план ведется отдельно: [`tactical_implementation_plan.md`](tactical_implementation_plan.md).

## Phase 1: Prove Database Compatibility

Purpose: confirm that the restored Oracle state works with every current application before architecture changes start.

### Scope

1. C# desktop client compatibility.
2. `Tserver` compatibility.
3. Terminal client flows that call `Tserver`.
4. Core PL/SQL package/procedure/function validity.

### Work

- Build an application-to-database call registry:
  - direct SQL queries from WinForms;
  - stored procedure/function calls from WinForms;
  - `Tserver` commands and their Oracle calls;
  - terminal operations and expected database side effects.
- Create smoke tests for safe read-only flows:
  - login;
  - user/rights lookup;
  - pallet lookup;
  - cell lookup;
  - article lookup;
  - task list lookup.
- Create controlled mutation tests only in a disposable schema or snapshot:
  - scan confirmation;
  - internal move;
  - replenishment;
  - inventory line creation;
  - assembly/picking confirmation.
- Record every required Oracle object and sequence dependency.

### Exit Criteria

- Desktop client can connect to the restored schema and open critical screens.
- `Tserver` can connect and execute its main command set.
- All tested mutations are repeatable in a snapshot-backed environment.
- A minimal regression checklist exists for future database changes.

## Phase 2: Introduce A Real API Boundary

Purpose: stop letting clients mutate Oracle directly.

The target is one stable API endpoint, with a stable DNS/IP address, where all write operations enter the system.

### Recommended Stack

- API server: Python FastAPI.
- Oracle access: `oracledb`, with `sqlalchemy` kept as an accepted DB-tooling dependency in the same family as `demand_forecast_backend`.
- Auth: JWT or internal service tokens at first, then role-based authorization mapped to WMS users.
- Documentation: OpenAPI/Swagger.
- Deployment: Uvicorn behind a Windows service wrapper, reverse proxy, or Linux container depending on the actual server environment.
- Observability: structured logs, request IDs, operation IDs, metrics, and audit tables.

### API Migration Rule

Use a strangler pattern:

1. Keep existing desktop and terminal flows working.
2. Move one operation at a time behind the API.
3. For each migrated operation, clients stop calling Oracle directly.
4. Oracle remains the transaction boundary until the API behavior is proven.

### First API Domains

- Authentication and current user context.
- Reference reads:
  - users;
  - cells;
  - articles;
  - pallets;
  - active tasks.
- Mutating commands:
  - confirm scan;
  - create inventory line;
  - internal movement;
  - assign destination cell;
  - confirm picking/assembly operation.
- Feed-factory traceability:
  - register production batch from API or JSON file exchange;
  - attach pallets and SSCC aggregation;
  - register raw-material usage;
  - enqueue Mercury and Honest Sign events;
  - expose processing status to operators and integrations.

### Design Rules

- Every mutation has an idempotency key.
- Every mutation returns an operation ID.
- The API writes an audit record before and after execution.
- Business rules initially delegate to existing PL/SQL rather than reimplementing logic in C#.
- Direct DB credentials are removed from new clients.

## Phase 3: Add Queueing And Conflict Control

Purpose: avoid race conditions when several terminals or desktop operators touch the same pallet, cell, order, or task.

### Key Architectural Choice

Do not start with Kafka just because it is powerful. Start from the required semantics:

- If the main problem is strict command ordering and operational safety, use an API command table plus a worker and transactional outbox.
- If the system needs high-volume event streams, replay, and multiple downstream consumers, Kafka becomes attractive.
- If the system needs a simpler durable work queue with acknowledgements and retries, RabbitMQ is often easier.
- If the system must stay very close to Oracle at first, an Oracle-backed command queue/outbox can be the lowest-risk first step.

### Recommended Path

1. Implement API command journal in Oracle:
   - `operation_id`;
   - `operation_type`;
   - `idempotency_key`;
   - `resource_key`;
   - `payload`;
   - `status`;
   - `created_at`;
   - `started_at`;
   - `finished_at`;
   - `error_code`;
   - `error_message`.
2. Add background workers that process commands.
3. Partition/serialize commands by `resource_key`:
   - pallet;
   - cell;
   - order;
   - transport task;
   - inventory document.
4. Add retry policy:
   - retry only technical failures;
   - do not blindly retry business validation failures.
5. Emit events through an outbox table.
6. Add Kafka or RabbitMQ only after the command model is proven.

### Kafka Decision Point

Kafka is justified when at least two of these are true:

- multiple systems need the same operation events;
- event replay is needed for audit/rebuild;
- event volume is high;
- external integrations need independent asynchronous processing;
- operations can be partitioned by stable keys.

If not, begin with Oracle outbox or RabbitMQ.

## Phase 4: Modern Android Terminal Application

Purpose: replace fragile legacy terminal software with a maintainable scanner-first mobile client.

### Target Capabilities

- Android app for warehouse scanners or rugged phones.
- Barcode/DataMatrix scanning.
- Online-first with limited offline buffering for safe scan capture.
- No direct Oracle access.
- All writes through the API.
- Fast operator UX:
  - login;
  - current task;
  - scan pallet;
  - scan cell;
  - confirm action;
  - show error/retry state clearly.

### Recommended Stack

- Android native Kotlin.
- Jetpack Compose for UI.
- CameraX or vendor scanner SDK depending on hardware.
- Local SQLite/Room for short-lived offline queue.
- API client generated from OpenAPI where practical.

### Migration Strategy

1. Mirror the current terminal command registry.
2. Implement read-only lookup screens first.
3. Implement one write flow end to end through the new API.
4. Pilot with one warehouse operation.
5. Expand operation by operation.
6. Retire old terminal flow only after parallel run.

## Phase 5: Regulated Integrations

Purpose: integrate with national regulated systems without mixing those concerns into core warehouse logic.

The detailed product/warehouse requirements for the feed factory scenario are captured in [`../requirements/feed_factory_mercury_crpt_tz.md`](../requirements/feed_factory_mercury_crpt_tz.md).

### Honest Sign

`Честный знак` / ГИС МТ integration should be a separate adapter service.

Core needs:

- store DataMatrix codes and aggregation relations;
- support clients that accept aggregation by `SSCC`;
- support clients that require full item-level `CIS` transfer;
- validate code format at receiving/scanning time;
- track code ownership/status where required by product group;
- send or receive documents through True API or EDI-related flows;
- persist external document IDs and processing statuses;
- support retries and manual reconciliation.

Architectural rule:

- WMS records operational facts.
- The Honest Sign adapter translates those facts into external documents and status checks.

### Mercury

`Меркурий` should be a separate VetIS.API adapter.

Core needs:

- store raw-material and finished-goods production batch linkage;
- map WMS receipt/shipment/stock records to veterinary document concepts;
- track eVSD identifiers;
- reconcile incoming and outgoing certificates;
- process asynchronous application status;
- isolate XML/WSDL complexity from WMS clients.

Architectural rule:

- Do not attempt to use Honest Sign API as a replacement for VetIS/Mercury API. These are separate integration contours.

## Target Architecture

```text
C# Desktop Client
Android Terminal App
Other Internal Tools
        |
        v
WMS API Gateway
        |
        +-- Command Journal / Idempotency / Audit
        |
        +-- Queue / Worker Layer
        |
        +-- Oracle RABAEV schema
        |
        +-- Integration Adapters
              |
              +-- Honest Sign / GIS MT / True API
              +-- VetIS.API / Mercury
              +-- SUPERMAG / Sfera
```

## Technology Recommendation

Start conservative:

- Python FastAPI, following the local `demand_forecast_backend` style.
- Oracle remains primary database.
- Oracle command journal and outbox first.
- Add RabbitMQ if a separate queue broker is needed quickly.
- Add Kafka when event streaming, replay, and multiple consumers become real requirements.
- Android terminal client in Kotlin.

This gives a practical path: stabilize first, then centralize writes, then introduce queueing, then modernize terminals, then expand regulated integrations.

## Risks

- Hidden business logic in C# forms or `Tserver`.
- Stored procedures with side effects that are not documented.
- Race conditions currently masked by operator habits.
- Hardcoded credentials and direct DB connections.
- Regulatory API changes in `Честный знак` and `Меркурий`.
- Testing destructive warehouse operations against the only working database.

## Guardrails

- Never test destructive database changes without a VM snapshot or disposable schema.
- New clients must not receive Oracle write credentials.
- Every new write operation must be idempotent.
- Every external integration must store request/response status and external IDs.
- SAP/SAP_INTEGRATION projects stay out of GitHub publication.

## First 30 Days

1. Keep the applied Oracle traceability migrations under version control and export a new restore point.
2. Build the API server skeleton with health check, Oracle connectivity check, OpenAPI, logging, and idempotency middleware.
3. Implement feed-factory endpoints over `RRL_PRODUCTION_API`.
4. Implement the JSON folder-exchange worker for production batch release.
5. Add smoke tests that create a production batch, raw-material usage, SSCC aggregation, CRPT code, Mercury metadata, and outbox events, then clean their own test data.
6. Build the DB compatibility matrix for WinForms and `Tserver`.
7. Document top 20 terminal/API operations.
8. Decide queue MVP: Oracle command journal/outbox unless a broker is already available.

## 90 Day Target

- Existing desktop client and `Tserver` compatibility proven against restored Oracle.
- API gateway running in test.
- At least three high-value terminal operations routed through API in pilot mode.
- Command journal/audit exists.
- Android terminal prototype can login, scan, and execute one controlled operation.
- Integration discovery completed for `Честный знак` and `Меркурий`.

## Official References

- [CRPT True API documentation](https://docs.crpt.ru/gismt/True_API/)
- [Честный знак community note: API documentation is in GIS MT Help / integrator knowledge base](https://markirovka.ru/community/developers/metody-api-chestnogo-znaka)
- [Честный знак note: GIS MT API does not replace VetIS API](https://markirovka.ru/knowledge/tovarnye-gruppy/molochnaya-produkciya/mozhno-li-rabotat-posredstvom-api-gis-mt-s-vetis)
- [VetIS.API component documentation](https://help.vetrf.ru/wiki/%D0%9A%D0%BE%D0%BC%D0%BF%D0%BE%D0%BD%D0%B5%D0%BD%D1%82_%D0%92%D0%B5%D1%82%D0%B8%D1%81.API)
- [VetIS.API application processing subsystem](https://help.vetrf.ru/wiki/%D0%9F%D0%BE%D0%B4%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%B0_%D0%BE%D0%B1%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B8_%D0%B7%D0%B0%D1%8F%D0%B2%D0%BE%D0%BA_%D0%B2_%D0%92%D0%B5%D1%82%D0%B8%D1%81.API)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [python-oracledb documentation](https://python-oracledb.readthedocs.io/)
