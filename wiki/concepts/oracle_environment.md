# Concept: Oracle Environment

## Recommended Model

The documented target database environment is an isolated Oracle VM for the WMS project.

Recommended shape:

- Windows Server 2012 R2 or Windows Server 2016
- Oracle Database 11g Express Edition or compatible 11g-family environment
- one service name, for example `WMS11G`
- application connects over the network
- application user is `RABAEV`, not `SYSTEM`

## Schema Separation

- `RABAEV`: WMS application objects and runtime connection user
- `SUPERMAG`: external ERP/source objects
- `WMS_DEPLOY`: optional technical deployment user
- `SYSTEM`: DBA/setup only

## Why This Matters

The old application uses legacy Oracle client behavior and historical SQL assumptions. Keeping the environment close to Oracle 11g reduces compatibility risk while separating WMS ownership from external ERP data ownership.

## Primary Sources

- [`../../NEW_BD_ENVIROMENT.md`](../../NEW_BD_ENVIROMENT.md)
- [`../subprojects/oracle_schema.md`](../subprojects/oracle_schema.md)

