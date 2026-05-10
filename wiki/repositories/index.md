# Repository Model

The target GitHub repository is:

- `https://github.com/romanrav1980/WMS_TMS_RABAEV`

This repository is the umbrella project for four logical subrepositories.

## Target Subrepositories

1. `oracle`
   - branch page: [`../branches/01_oracle_plsql_core.md`](../branches/01_oracle_plsql_core.md)
   - owns Oracle schema, PL/SQL procedures, functions, tables, seeds, and database deployment scripts
   - prepared local publication package: `tmp/WMS_TMS_RABAEV_oracle_publish`
   - target remote: `https://github.com/romanrav1980/WMS_TMS_RABAEV_oracle`

2. `csharp-client`
   - branch page: [`../branches/02_csharp_desktop_client.md`](../branches/02_csharp_desktop_client.md)
   - owns the C# WinForms desktop operator application
   - prepared local publication package: `tmp/WMS_TMS_RABAEV_csharp_client_publish`
   - target remote: `https://github.com/romanrav1980/WMS_TMS_RABAEV_csharp_client`

3. `terminal-contour`
   - branch page: [`../branches/03_terminal_contour.md`](../branches/03_terminal_contour.md)
   - owns handheld terminal clients, scanner flows, and terminal server/gateway code
   - prepared local publication package: `tmp/WMS_TMS_RABAEV_terminal_contour_publish`
   - target remote: `https://github.com/romanrav1980/WMS_TMS_RABAEV_terminal_contour`

4. `external-integrations`
   - branch page: [`../branches/04_external_integrations.md`](../branches/04_external_integrations.md)
   - owns `SUPERMAG` / `Sfera`, import/export, staging, and mapping flows
   - SAP/SAP_INTEGRATION projects are not part of the GitHub publication plan

## Recommended Root Layout

If this stays as a single Git repository, use this layout:

```text
WMS_TMS_RABAEV/
  oracle/
  csharp-client/
  terminal-contour/
  external-integrations/
  wiki/
  wiki-raw/
  AGENTS.md
```

If these become true separate Git repositories later, keep this repository as the umbrella/orchestration repo and connect the four parts as submodules or documented sibling repositories.

## Migration Rule

Do not physically move code into these folders until the current working changes are committed or explicitly set aside.

The current repository contains historical duplicates and snapshots. Each move should be done branch by branch, with a manifest of what moved and what stayed archival.

## Oracle Publication Status

Prepared locally:

- source: `db/windowsapplication2_xp12_oracle/`
- local package: `tmp/WMS_TMS_RABAEV_oracle_publish`
- local commit: `Initial Oracle schema and seed scripts`

Push status:

- blocked because GitHub returned `Repository not found` for `romanrav1980/WMS_TMS_RABAEV_oracle`
- next step is to create the empty GitHub repository, preferably private until credentials and seed contents are reviewed

## C# Desktop Client Publication Status

Prepared locally:

- source: `MINI WMS/WindowsApplication2/WindowsApplication2/`
- local package: `tmp/WMS_TMS_RABAEV_csharp_client_publish`
- local commit: `Initial C# desktop client`
- build check: `scripts/build-desktop-client.ps1` completed with `0` errors and legacy warnings

Push status:

- blocked because GitHub returned `Repository not found` for `romanrav1980/WMS_TMS_RABAEV_csharp_client`
- next step is to create the empty GitHub repository, preferably private until hardcoded connection strings are reviewed

## Terminal Contour Publication Status

Prepared locally:

- source: `MINI WMS/CS_CATClient/`
- source: `MINI WMS/Tserver/`
- source: `MINI WMS/DeviceApplication3/`
- source note: `WMSTerm/постановка.txt`
- local package: `tmp/WMS_TMS_RABAEV_terminal_contour_publish`
- local commit: `Initial terminal contour`
- build check: `scripts/build-terminal-server.ps1` completed with `0` errors and legacy warnings for `Tserver`

Push status:

- blocked because GitHub returned `Repository not found` for `romanrav1980/WMS_TMS_RABAEV_terminal_contour`
- next step is to create the empty GitHub repository, preferably private until hardcoded IP addresses and Oracle credentials are reviewed
