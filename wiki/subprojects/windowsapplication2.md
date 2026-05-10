# Subproject: WindowsApplication2

## Role

`WindowsApplication2` is the main legacy WinForms WMS/TMS desktop application in this repository.

It is included in the root Visual Studio 2008 solution and appears to be the operational center around which Oracle schema reconstruction and external ERP integration are documented.

## What It Depends On

- Oracle schema owned by `RABAEV`
- external ERP objects exposed through `SUPERMAG` / `Sfera`
- legacy .NET / WinForms project conventions
- database procedures, functions, and tables reconstructed under `db/windowsapplication2_xp12_oracle`

## What To Be Careful With

- The codebase is legacy and likely contains large forms with embedded SQL and business logic.
- External table names such as `SUPERMAG.SMCARD`, `SUPERMAG.SMDOCUMENTS`, and `SUPERMAG.MON_WMS_STBYPALL` are business contracts, not just implementation details.
- Changes should be scoped and checked against the Oracle scripts and integration docs.

## Primary Sources

- [`../../TMS.sln`](../../TMS.sln)
- [`../../MINI WMS/WindowsApplication2/WindowsApplication2/WindowsApplication2.csproj`](../../MINI%20WMS/WindowsApplication2/WindowsApplication2/WindowsApplication2.csproj)
- [`../../MINI WMS/WindowsApplication2/WindowsApplication2/Form1.cs`](../../MINI%20WMS/WindowsApplication2/WindowsApplication2/Form1.cs)
- [`../concepts/external_integration_supermag.md`](../concepts/external_integration_supermag.md)
- [`../subprojects/oracle_schema.md`](oracle_schema.md)

