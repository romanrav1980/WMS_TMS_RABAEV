# Concept: External Integration With SUPERMAG / Sfera

## Meaning

Within this repository, `Sfera` and `SUPERMAG` refer to the same external ERP context:

- `Sfera` is the business-facing name.
- `SUPERMAG` is the technical Oracle schema/object prefix used in code and SQL.

## Why It Matters

`WindowsApplication2` reads external ERP data to build WMS operational state, including goods, packaging, document headers, document lines, stores, clients, and pallet breakdown data.

These objects should be treated as external contracts. The WMS schema should receive only the required grants, not own or mutate the external ERP schema by default.

## Important External Objects

- `SUPERMAG.MON_WMS_STBYPALL`
- `SUPERMAG.SMCARD`
- `SUPERMAG.SMCARDPROPERTIES`
- `SUPERMAG.vcardstoreprop_rc`
- `SUPERMAG.SMSTOREUNITS`
- `SUPERMAG.SMDOCUMENTS`
- `SUPERMAG.SMSPEC`
- `SUPERMAG.SMCLIENTINFO`
- `SUPERMAG.SMSTORELOCATIONS`
- `SUPERMAG.SMCOMMONBASES`

## Primary Sources

- [`../../EXTERNAL_INTEGRATION.MD`](../../EXTERNAL_INTEGRATION.MD)
- [`../subprojects/windowsapplication2.md`](../subprojects/windowsapplication2.md)
- [`../subprojects/oracle_schema.md`](../subprojects/oracle_schema.md)

