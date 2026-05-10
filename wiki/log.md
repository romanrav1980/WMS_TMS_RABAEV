# Wiki Log

Append-only log of root wiki updates.

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
