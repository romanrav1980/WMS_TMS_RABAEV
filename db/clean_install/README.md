# Clean Oracle Install Kit

This folder is the from-zero install kit for a separate TMS/WMS Oracle
installation.

Decision:

- Keep the canonical legacy SQL in `db/windowsapplication2_xp12_oracle/`.
- Keep reviewed deltas in `db/migrations/`.
- Put only install orchestration, phase scripts, profiles, and verification here.

This avoids copying large SQL exports into a second source of truth while still
giving a clean install entry point.

## Isolation Model

The legacy application and PL/SQL source are hard-wired to schema owner
`RABAEV`. For a separate installation, use a separate Oracle service/PDB/VM and
create `RABAEV` there. Do not try to rename the schema unless the application
code and all PL/SQL references are changed deliberately.

Default owner password in the bootstrap script is the legacy development value
from the original scripts. Change it after install in any real environment.

## Folder Layout

- `structure/`: owner, tables, sequences, PL/SQL, modern structural extensions.
- `settings/`: runtime constants, admin user, rights, and master reference data.
- `fixtures/`: dev/acceptance-only seed data.
- `profiles/`: ordered SQL entry points.
- `verify/`: assertion scripts for each profile layer.
- `scripts/`: PowerShell runner wrappers around `tools/oracle_apply`.

## Profiles

| Profile | Purpose | Includes dev fixtures |
|---|---|---|
| `legacy-runtime` | Legacy schema plus minimal runtime settings/admin user. | No |
| `legacy-master` | Legacy schema plus imported master reference data. | No |
| `modern-prod` | Legacy master data plus WMS/MES/warehouse-map and TMS-2 production structure. | No |
| `tms2-acceptance` | `modern-prod` plus deterministic TMS-2 acceptance data. | Yes |

Do not use `tms2-acceptance` for production. It applies Dobrotseny test data,
the Sprint 9 planner template fixture, and the test geocode fixture.

## Run

Set an admin connection string for the target empty Oracle environment:

```powershell
$env:TMS_ORACLE_ADMIN = "User Id=SYSTEM;Password=...;Data Source=127.0.0.1:1521/orcl"
```

Run a profile from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\db\clean_install\scripts\install-clean-db.ps1 `
  -Profile modern-prod `
  -ConnectionEnv TMS_ORACLE_ADMIN `
  -IUnderstandThisRebuildsRabaev
```

Verify later without reinstalling:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\db\clean_install\scripts\verify-clean-db.ps1 `
  -Profile modern-prod `
  -ConnectionEnv TMS_ORACLE_ADMIN
```

For direct execution through `OracleApply`:

```powershell
dotnet run --project .\tools\oracle_apply\OracleApply.csproj -- `
  TMS_ORACLE_ADMIN `
  .\db\clean_install\profiles\03_modern_prod.sql `
  --encoding=utf8 `
  --stop-on-error
```

## Important Notes

- These profiles are for an empty or disposable target. The legacy core scripts
  drop and recreate many `RABAEV` objects.
- `042/043` TMS-2 historical migrations are not replayed in clean install
  because they reference the non-existent legacy column
  `RRL_SBORKA_PALLETS.DELETED`. Clean install applies the final compatible
  TMS-2 structure through `051+` instead.
- Production installs must provide real business data or a controlled import.
  Acceptance fixtures are intentionally isolated under `fixtures/`.
- SAP/SAP_INTEGRATION materials are not part of this install kit.
