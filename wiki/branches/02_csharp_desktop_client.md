# Branch: C# Desktop Client

## Role

This branch is the main operator-facing desktop application.

It is the C# WinForms client used for day-to-day warehouse and transport work from a workstation.

## What Lives Here

Desktop workflows belong here:

- forms and grids
- document screens
- acceptance and shipping operator flows
- transport and route UI
- user administration screens
- manual corrections and operator decisions
- reports or views initiated by a desktop operator

## Main Current Location

- [`../../MINI WMS/WindowsApplication2/WindowsApplication2/`](../../MINI%20WMS/WindowsApplication2/WindowsApplication2/)
- [`../../TMS.sln`](../../TMS.sln)

There are also multiple legacy snapshots and working examples under `MINI WMS/`, `WMS перенос v1/`, `WMS Эталон/`, and `WindowsApplication2/`. Treat them as historical sources unless a current task names them explicitly.

## What It Depends On

- [[oracle_plsql_core]] for business logic and persistent state.
- [[external_integrations]] for external ERP source data once it reaches Oracle or staging.

## Boundaries

- The desktop client should orchestrate user interaction, not duplicate core warehouse algorithms that already live in PL/SQL.
- Before changing SQL embedded in forms, check whether it is a local UI query or a business rule that should be reconciled with the Oracle branch.
- Keep historical snapshots separate from the current `TMS.sln` entry point.

## Primary Sources

- [`../../TMS.sln`](../../TMS.sln)
- [`../../MINI WMS/WindowsApplication2/WindowsApplication2/WindowsApplication2.csproj`](../../MINI%20WMS/WindowsApplication2/WindowsApplication2/WindowsApplication2.csproj)
- [`../../MINI WMS/WindowsApplication2/WindowsApplication2/Form1.cs`](../../MINI%20WMS/WindowsApplication2/WindowsApplication2/Form1.cs)
- [`../subprojects/windowsapplication2.md`](../subprojects/windowsapplication2.md)
