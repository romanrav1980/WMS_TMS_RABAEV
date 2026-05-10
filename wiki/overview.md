# TMS Overview

## What This Repository Is

TMS is a recovered and actively organized WMS/TMS codebase centered on an older C# WinForms application, Oracle database logic, and integrations with external warehouse/ERP systems.

Target GitHub repository:

- `https://github.com/romanrav1980/WMS_TMS_RABAEV`

The repository is not a single clean modern service. It contains:

- legacy application snapshots and working examples
- a Visual Studio 2008 solution for `WindowsApplication2`
- Oracle schema reconstruction scripts
- documentation for external ERP integration
- working manifests, checkpoints, logs, and generated wiki pages

## Current High-Level Shape

- `TMS.sln` opens the main `WindowsApplication2` application and related database/docs/script items.
- `MINI WMS/WindowsApplication2/WindowsApplication2` is the main legacy desktop application.
- `db/windowsapplication2_xp12_oracle` contains the reconstructed Oracle schema path.
- SAP/SAP_INTEGRATION projects are intentionally excluded from this GitHub publication.

## Four Logical Branches

The project is now organized around four logical branches:

1. [Oracle / PL/SQL Core](branches/01_oracle_plsql_core.md)
   - database schema, stored procedures, functions, triggers, and persistent warehouse rules

2. [C# Desktop Client](branches/02_csharp_desktop_client.md)
   - main workstation application for operators and administrative workflows

3. [Terminal Contour](branches/03_terminal_contour.md)
   - handheld/scanner clients, terminal server, and scanned operation confirmation

4. [External Integrations](branches/04_external_integrations.md)
   - `SUPERMAG` / `Sfera`, file exchange, imports, exports, and staging

These four branches map to the intended subrepositories described in [repositories/index.md](repositories/index.md).

## Current Working Focus

The current critical focus is the Oracle restore point:

- preserve the repaired `RABAEV` schema state from `127.0.0.1:1521/orcl`
- keep the SQL restore bundle under `db/restore_points/`
- use VirtualBox snapshots before any future destructive Oracle operation

## Boundaries To Preserve

- Do not mix raw source files and synthesized wiki pages.
- Do not publish SAP/SAP_INTEGRATION project files or runbooks to GitHub.
- Do not treat old manifest notes as automatically current when newer checkpoint or schema pages supersede them.
- Do not rewrite legacy code or SQL merely to make documentation cleaner.

## Primary Sources

- [`../TMS.sln`](../TMS.sln)
- [`../EXTERNAL_INTEGRATION.MD`](../EXTERNAL_INTEGRATION.MD)
- [`../NEW_BD_ENVIROMENT.md`](../NEW_BD_ENVIROMENT.md)
- [`../db/windowsapplication2_xp12_oracle/README.md`](../db/windowsapplication2_xp12_oracle/README.md)
