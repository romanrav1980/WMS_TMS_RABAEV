# Wiki Log

Append-only log of root wiki updates.

## [2026-05-17] oracle-migration-001-applied | Applied feed factory traceability migration

- Applied `db/migrations/2026-05-17_feed_factory_traceability/001_apply.sql` to `RABAEV@127.0.0.1:1521/orcl` after explicit user approval.
- Code checkpoint before apply: `0e0c270`.
- Apply result: `Statements=4; Errors=0`.
- Verify result after removing SQL*Plus-only formatting from `001_verify.sql`: `Statements=6; Errors=0`.
- Recompiled the `RABAEV` schema with `dbms_utility.compile_schema`.
- Final live object check excluding recycle-bin objects: `456 VALID`, `0 INVALID`, no current `USER_ERRORS`.

## [2026-05-17] oracle-migration-001 | Prepared feed factory traceability migration for review

- Added versioned migration folder `db/migrations/2026-05-17_feed_factory_traceability/`.
- Added `001_apply.sql`, `001_rollback.sql`, and `001_verify.sql` for the first feed-factory traceability schema layer.
- Added [`database/feed_factory_traceability_schema.md`](database/feed_factory_traceability_schema.md) as the local schema mirror for the migration.
- Recorded the migration version ID `2026-05-17-001-feed-factory-traceability`.
- Updated [`database/oracle_change_protocol.md`](database/oracle_change_protocol.md) with the code version rule for Oracle migrations.
- Did not apply the migration to live Oracle; it is ready for user review and explicit approval.

## [2026-05-17] feed-factory-file-exchange | Added JSON folder exchange for production release

- Updated [`requirements/feed_factory_mercury_crpt_tz.md`](requirements/feed_factory_mercury_crpt_tz.md).
- Added `PRODUCTION_BATCH_SOURCE = FILE_EXCHANGE` as a configurable source for finished-goods production releases.
- Defined the folder-based JSON exchange standard: `in/`, `processing/`, `archive/`, `error/`, and `out/`.
- Added idempotency by `messageId`, JSON examples, response files, and `RRL_FILE_EXCHANGE_LOG`.

## [2026-05-16] feed-factory-tz | Added production traceability requirements for Mercury and Honest Sign

- Added [`requirements/feed_factory_mercury_crpt_tz.md`](requirements/feed_factory_mercury_crpt_tz.md) in Russian.
- Captured the target process model for raw-material receipt, raw-material usage, production batch release, marking, aggregation, pallet receipt, and client shipment.
- Recorded that some clients accept Honest Sign aggregation by `SSCC`, while others require full item-level `CIS` lists.
- Linked the technical assignment from the root index, wiki schema, external integrations branch, and strategic roadmap.

## [2026-05-16] oracle-schema-mirror | Added local wiki mirror rule for Oracle changes

- Added [`database/index.md`](database/index.md) as the local wiki mirror entry point for the Oracle `RABAEV` schema.
- Added [`database/oracle_change_protocol.md`](database/oracle_change_protocol.md) to require wiki + SQL source + live Oracle alignment for schema changes.
- Linked the database mirror from the root index, Oracle branch, Oracle schema subproject, wiki schema, and agent onramp.
- Recorded the safety discipline: no invisible Oracle changes, no stored secrets in wiki, and verification through read-only metadata checks after applying changes.

## [2026-05-11] compatibility-fix | Closed missing DB API and Tserver config gaps

- Created VM snapshot `before-compat-fixes-2026-05-11` before applying Oracle DDL.
- Added `db/compatibility_fixes/2026-05-11/001_client_tserver_compat.sql`.
- Added missing table-like objects and compatibility packages for `PRIHOD`, `PALL_SPLITTER`, `TRANSPORT_PLN`, `STORE_ADRESSES`, and `HELP`.
- Extended `COMPL` with `ADD_ART_2PALL`, `DIVIDE_ORDER_BYPAL2`, and `UPDATE_SEQ2`.
- Fixed `Tserver` `adr.txt` parsing so malformed config no longer falls back to `192.168.208.200`.
- Added `adr.txt` as `Tserver.csproj` content so Release builds place a valid config beside `Tserver.exe`.
- Normalized `Tserver.sln` header so MSBuild 17 recognizes it as a solution file.
- Recompiled Oracle schema; final invalid object count is `0`.
- Rebuilt `WindowsApplication2` and `Tserver`, and reran `Tserver` `GET_RUSER` smoke against local Oracle.

## [2026-05-11] compatibility | Checked Oracle with desktop client and Tserver

- Built `WindowsApplication2` Release x64: `0` errors, legacy warnings remain.
- Built `Tserver` Release AnyCPU: `0` errors, `System.Data.OracleClient` deprecation warnings remain.
- Verified managed ODP.NET and legacy `System.Data.OracleClient` connections to `RABAEV@127.0.0.1:1521/orcl`.
- Ran read-only `Tserver` smoke command `GET_RUSER` against local Oracle VM.
- Added [`runbooks/db_app_compatibility_check_2026_05_11.md`](runbooks/db_app_compatibility_check_2026_05_11.md) with findings and gaps.

## [2026-05-11] roadmap | Strategic development plan

- Added [`roadmap/strategic_development_plan.md`](roadmap/strategic_development_plan.md).
- Captured the path from Oracle compatibility checks to API gateway, queueing, Android terminals, and regulated integrations.
- Recorded queue decision guidance: Oracle command journal/outbox first, RabbitMQ or Kafka when their semantics are justified.

## [2026-05-11] oracle-recovery | Restored RABAEV and exported restore point

- Recovered Oracle VM `orcl` schema `RABAEV` from recycle bin after accidental DDL damage.
- Created VirtualBox snapshots `before-flashback-repair-2026-05-11` and `after-flashback-repair-2026-05-11`.
- Recompiled `RABAEV`; final verification showed no invalid objects.
- Exported SQL restore bundle under `db/restore_points/rabaev_orcl_after_flashback_2026-05-11`.
- Added [`runbooks/oracle_recovery_2026_05_11.md`](runbooks/oracle_recovery_2026_05_11.md) with the incident and recovery context.

## [2026-05-11] api-server | Verified local API and Oracle VM connectivity

- Verified local ASP.NET Core API build/run on installed .NET SDK 9.0.
- Verified Oracle Developer VM listener through `tnsping //127.0.0.1:1521/orcl`.
- Confirmed old Windows `sqlplus` 10.2 is not usable against the VM because of `ORA-28040`.
- Installed `Oracle.ManagedDataAccess.Core` 23.8.0 in a temporary probe project.
- Verified an ASP.NET Core `/db/ping` endpoint can query Oracle VM service `orcl` through managed ODP.NET.
- Noted that legacy `DBWMS` at `192.168.208.9:1521` is currently unreachable from this workstation/session.

## [2026-05-11] terminal-api | Documented Tserver as legacy API gateway

- Added [`concepts/tserver_api_registry.md`](concepts/tserver_api_registry.md) with fixed `FUNC` commands, observed `CALL_SPF` procedures, database effects, and candidate modern endpoints.
- Added [`runbooks/create_api_server.md`](runbooks/create_api_server.md) with the recommended ASP.NET Core API server path and compatibility adapter plan.
- Linked the API migration notes from the terminal contour branch and root wiki index.

## [2026-05-11] terminal-contour | Prepared separate terminal contour repository package

- Prepared local package `tmp/WMS_TMS_RABAEV_terminal_contour_publish` from `CS_CATClient`, `Tserver`, `DeviceApplication3`, and `WMSTerm` notes.
- Split terminal publication into `src/`, `scripts/`, and `docs/`.
- Created local initial commit `Initial terminal contour`.
- Verified `Tserver` builds with `scripts/build-terminal-server.ps1`: `0` errors, legacy warnings remain.
- Push to `romanrav1980/WMS_TMS_RABAEV_terminal_contour` was blocked because GitHub returned `Repository not found`.

## [2026-05-11] csharp-client | Prepared separate desktop client repository package

- Prepared local package `tmp/WMS_TMS_RABAEV_csharp_client_publish` from `MINI WMS/WindowsApplication2/WindowsApplication2/`.
- Split desktop publication into `src/`, `scripts/`, and `docs/`.
- Created local initial commit `Initial C# desktop client`.
- Verified the package builds with `scripts/build-desktop-client.ps1`: `0` errors, legacy warnings remain.
- Push to `romanrav1980/WMS_TMS_RABAEV_csharp_client` was blocked because GitHub returned `Repository not found`.

## [2026-05-11] oracle | Prepared separate Oracle repository package

- Prepared local package `tmp/WMS_TMS_RABAEV_oracle_publish` from `db/windowsapplication2_xp12_oracle/`.
- Split Oracle publication into `ddl/`, `seed/`, and `docs/`.
- Created local initial commit `Initial Oracle schema and seed scripts`.
- Push to `romanrav1980/WMS_TMS_RABAEV_oracle` was blocked because GitHub returned `Repository not found`.

## [2026-05-11] repository | New GitHub target and subrepository model

- Switched local `origin` to `https://github.com/romanrav1980/WMS_TMS_RABAEV.git`.
- Added [`repositories/index.md`](repositories/index.md) describing the umbrella repository and four target subrepositories.
- Linked the repository model from the wiki index, overview, and branch index.

## [2026-05-11] architecture | Four logical branches

- Added `wiki/branches/` with four top-level architectural branches:
  Oracle / PL/SQL Core, C# Desktop Client, Terminal Contour, and External Integrations.
- Updated the root index, overview, schema, and source catalog to use the four-branch model.

## [2026-05-10] scaffold | Root Karpathy-style wiki

- Added root `wiki/` knowledge layer for the whole TMS repository.
- Added `wiki-raw/` for immutable imported sources.
- Added `AGENTS.md` as the agent-facing schema/onramp.
- Recorded that SAP/SAP_INTEGRATION projects are excluded from GitHub publication.
