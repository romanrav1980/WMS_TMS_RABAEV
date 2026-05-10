# Subproject: Oracle Schema

## Role

The Oracle schema reconstruction under `db/windowsapplication2_xp12_oracle` provides the database side needed by the legacy `WindowsApplication2` application.

The target model separates:

- `RABAEV`: WMS application schema and owner of local WMS objects
- `SUPERMAG`: external ERP/source schema
- optional deployment user such as `WMS_DEPLOY`

## Important Scripts

- `create_schema.sql`: initial schema/user setup
- `01_tables.sql`: table definitions
- `02_sequences.sql`: sequences
- `03_functions.sql`: functions
- `04_procedures.sql`: procedures
- `05_gap_patch.sql`: missing compatibility fixes
- `06_transport_task_missing_impl.sql`: transport task implementation gaps

## Design Direction

The recommended environment is a separate Oracle 11g-compatible Windows VM, accessed over the network by the desktop app. The application should connect as `RABAEV`, while `SUPERMAG` remains an external data owner exposed through grants.

## Primary Sources

- [`../../NEW_BD_ENVIROMENT.md`](../../NEW_BD_ENVIROMENT.md)
- [`../../db/windowsapplication2_xp12_oracle/README.md`](../../db/windowsapplication2_xp12_oracle/README.md)
- [`../../db/windowsapplication2_xp12_oracle/gap_report.md`](../../db/windowsapplication2_xp12_oracle/gap_report.md)
- [`../concepts/oracle_environment.md`](../concepts/oracle_environment.md)

